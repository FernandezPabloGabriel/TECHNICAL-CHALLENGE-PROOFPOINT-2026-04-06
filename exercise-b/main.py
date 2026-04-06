# Title, Author, PublicationYear
import csv
from dataclasses import dataclass
from datetime import datetime
from enum import auto, Enum
from operator import itemgetter, attrgetter


@dataclass(frozen=False)
class Book:
    title: str # Always present
    author: str
    publication_year: int


class TypeOfRecord(Enum):
    ADDED = auto()
    #DISCARDED = auto()
    DISCARDED_DUPLICATE = auto()
    ENRICHED_DUPLICATE = auto()
    #INCOMING = auto()


def initialize_book(title: str, author: str, pubYear: str) -> Book | None:
    # Validating title is not empty
    if title == "":
        return None
    
    # Correcting author
    if author == "":
        author = "Author Unknown"

    # Correcting publication year
    pubYearNumber = 0
    if pubYear.isdigit():
        pubYearNumber = int(pubYear)
        if pubYearNumber < 0 or pubYearNumber > datetime.now().year:
                pubYearNumber = 0
    # If pubYear not digit, pubYearNumber remain as 0

    return Book(title, author, pubYearNumber)


def complete_book(existingBook: Book, newBook: Book) -> TypeOfRecord:
    enriched = False
    if existingBook.author == "Author Unknown" and newBook.author != "Author Unknown":
        existingBook.author = newBook.author # Update the book with the known author
        enriched = True
    if existingBook.publication_year == 0 and newBook.publication_year != 0:
        existingBook.publication_year = newBook.publication_year # Update the book with the known publication year
        enriched = True
    
    if enriched:
        return TypeOfRecord.ENRICHED_DUPLICATE # Book was enriched with new information
    return TypeOfRecord.DISCARDED_DUPLICATE # Book was a duplicate, so is discarded
    


def add_or_complete_book(booksSet: dict, book: Book) -> TypeOfRecord:
    bookTitle = book.title.casefold()
    if bookTitle not in booksSet: 
        booksSet[bookTitle] = book # Using title as key to avoid duplicates
        return  TypeOfRecord.ADDED # Book was added
    return complete_book(booksSet[bookTitle], book)
    


def group_books_by_author_or_publication_year(books: dict) -> tuple[dict, dict]:
    groupedBooksAuthor = {}
    groupedBooksPubYear = {}
    for book in books.values():
        if book.author != "Author Unknown":
            bookAuthor = book.author.casefold()
            groupedBooksAuthor.setdefault(bookAuthor, []).append(book)
            # if bookAuthor not in groupedBooksAuthor:
            #     groupedBooksAuthor[book.author] = []
            # groupedBooksAuthor[book.author].append(book)
        else:
            bookPubYear = book.publication_year
            groupedBooksPubYear.setdefault(bookPubYear, []).append(book)
    
    # Sorting by title and then by author
    for author in groupedBooksAuthor:
        groupedBooksAuthor[author].sort(key=attrgetter("title"))
    sortedGroupedBooksAuthor = dict(sorted(groupedBooksAuthor.items(), key=itemgetter(0))) # Remember that authors arent casefolded

    # Sorting by title and then by publication year
    for pubYear in groupedBooksPubYear:
        groupedBooksPubYear[pubYear].sort(key=attrgetter("title"))
    sortedGroupedBooksPubYear = dict(sorted(groupedBooksPubYear.items(), key=itemgetter(0)))

    return sortedGroupedBooksAuthor, sortedGroupedBooksPubYear


def read_csv(FILE_PATH: str, booksSet: dict) -> None | dict:
    with open(FILE_PATH, mode="r", encoding="utf-8") as file:
        fileReader = csv.reader(file)
        ### COULD GO A CONDITIONAL TO CHECK IF THERE IS A HEADER
        fileReader.__next__()  # Skip header

        countIncomingBooks = 0
        countAddedBooks = 0
        countDiscardedBooks = 0
        countDiscardedDuplicateBooks = 0
        countEnrichedDuplicateBooks = 0
        
        for row in fileReader:
            countIncomingBooks += 1
            title=row[0].strip()
            author=row[1].strip()
            pubYear=row[2].strip()
            book = initialize_book(title, author, pubYear)

            if book is not None:
                typeOfRecord = add_or_complete_book(booksSet, book)
                if typeOfRecord == TypeOfRecord.ADDED:
                    countAddedBooks += 1
                elif typeOfRecord == TypeOfRecord.ENRICHED_DUPLICATE:
                    countEnrichedDuplicateBooks += 1
                else:
                    countDiscardedDuplicateBooks += 1
                print(f"{book.title} | {book.author} | {book.publication_year}")
            else:
                countDiscardedBooks += 1
        
        print(f"\nTotal incoming books: {countIncomingBooks}")
        print(f"Total books added: {countAddedBooks}")
        print(f"Total books discarded: {countDiscardedBooks}")
        print(f"Total books duplicated and discarded: {countDiscardedDuplicateBooks}")
        print(f"Total books duplicated and enriched: {countEnrichedDuplicateBooks}")
        print(f"Integrity check: {countAddedBooks + countDiscardedBooks + countDiscardedDuplicateBooks + countEnrichedDuplicateBooks}")

        metrics = {
            "incoming_books": countIncomingBooks,
            "added_books": countAddedBooks,
            "discarded_books": countDiscardedBooks,
            "discarded_duplicate_books": countDiscardedDuplicateBooks,
            "enriched_duplicate_books": countEnrichedDuplicateBooks
        }

        return metrics
        
        
def md_escape(text: str) -> str:
    text = str(text) # Ensure the input is a string
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def generate_report_md(groupedBooksAuthor: dict, groupedBooksPubYear: dict, metrics: dict) -> str:
    lines = []
    lines.append("# Library's Books Report")
    lines.append("")
    lines.append(f"_Generated in: {datetime.now().date()}_")
    lines.append("")
    lines.append("## Metrics")
    lines.append(f"From the given csv file, the following metrics were obtained:")
    lines.append(f"- Total of processed books (rows): {metrics['incoming_books']}")
    lines.append(f"- Total of added books: {metrics['added_books']}")
    lines.append(f"- Total of discarded books: {metrics['discarded_books']}")
    lines.append(f"- Total of duplicated and discarded books: {metrics['discarded_duplicate_books']}")
    lines.append(f"- Duplicated books used to enrich previously registered books: {metrics['enriched_duplicate_books']}")
    lines.append("")
    lines.append("## Books grouped by author")

    for author in groupedBooksAuthor:
        lines.append("<details>")
        booksFromAuthor = groupedBooksAuthor[author]
        caseSensitiveAuthor = booksFromAuthor[0].author
        lines.append(f"  <summary><strong>{md_escape(caseSensitiveAuthor)}</strong> ({len(booksFromAuthor)})</summary>")
        lines.append("")
        for book in booksFromAuthor:
            lines.append(f"  - {md_escape(book.title)} | {book.publication_year}")
        lines.append("</details>")
        lines.append("")

    lines.append("## Books grouped by publication year (And missing author)")
    for pubYear in groupedBooksPubYear:
        lines.append("<details>")
        booksFromPubYear = groupedBooksPubYear[pubYear]
        if pubYear == 0:
            lines.append(f"  <summary><strong>Unknown Publication Year</strong> ({len(booksFromPubYear)})</summary>")
        else:
            lines.append(f"  <summary><strong>{md_escape(pubYear)}</strong> ({len(booksFromPubYear)})</summary>")
        lines.append("")
        for book in booksFromPubYear:
            lines.append(f"  - {md_escape(book.title)}")
        lines.append("</details>")
        lines.append("")

    return "\n".join(lines)





def main():
    # Lector de csv
    FILE_PATH = "books.csv"
    booksSet = {}
    metrics = read_csv(FILE_PATH, booksSet)
    groupedBooksAuthor, groupedBooksPubYear = group_books_by_author_or_publication_year(booksSet)
    print("\nBooks grouped by author:")
    for author, books in groupedBooksAuthor.items():
        print(f"Author: {author}")
        for book in books:
            print(f"  - {book.title} ({book.publication_year})")
    print("\nBooks grouped by publication year:")
    for pubYear, books in groupedBooksPubYear.items():
        print(f"Publication Year: {pubYear}")
        for book in books:
            print(f"  - {book.title}")

    report_md = generate_report_md(groupedBooksAuthor, groupedBooksPubYear, metrics)
    with open("report.md", "w", encoding="utf-8") as f:
        f.write(report_md)
    
    # mostrar resultados en .md
    # mostrar registros descartados, ingresados, duplicados, egresados, registros sin autor, registros sin año


if __name__ == "__main__":
    main()