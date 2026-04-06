# Title, Author, PublicationYear
import csv
from dataclasses import dataclass
from datetime import datetime
from enum import auto, Enum
from operator import itemgetter, attrgetter

FILE_PATH = "books.csv"
AUTHOR_UNKNOWN = "Author Unknown"


# Decided to use a Class to represent each book because it allows to easily manipulate the data and keep 
# track of the information of each one of them
@dataclass()
class Book:
    title: str # Always present
    author: str
    publication_year: int


# Enum class to represent the type of record processed when reading the csv file to keep track of the metrics 
class TypeOfRecord(Enum):
    ADDED = auto()
    DISCARDED_DUPLICATE = auto()
    ENRICHED_DUPLICATE = auto()


def initialize_book(title: str, author: str, pubYear: str) -> Book | None:
    title = title.strip()
    author = author.strip()
    pubYear = pubYear.strip()

    # Validating title is not empty
    if title == "":
        return None
    else:
        title = " ".join(title.split()) # Removing extra spaces between words and replacing it with a single space
    
    # Correcting author
    if author == "":
        author = AUTHOR_UNKNOWN
    else:
        author = " ".join(author.split())

    # Correcting publication year
    pubYearNumber = 0
    pubYear = "".join(pubYear.split()) # Removing extra spaces between digits
    if pubYear.isdigit():
        pubYearNumber = int(pubYear) 
        if pubYearNumber < 0 or pubYearNumber > datetime.now().year:
                pubYearNumber = 0
    # If pubYear not digit, pubYearNumber remain as 0

    return Book(title, author, pubYearNumber)


# This function takes an existing book and updates (enriches) its missing fields with the information from the new duplicated book (Author or Publication Year)
def complete_book(existingBook: Book, newBook: Book) -> TypeOfRecord:
    enriched = False
    if existingBook.author == AUTHOR_UNKNOWN and newBook.author != AUTHOR_UNKNOWN:
        existingBook.author = newBook.author # Update the book with the known author
        enriched = True
    if existingBook.publication_year == 0 and newBook.publication_year != 0:
        existingBook.publication_year = newBook.publication_year # Update the book with the known publication year
        enriched = True
    
    if enriched:
        return TypeOfRecord.ENRICHED_DUPLICATE # Book was enriched with new information
    return TypeOfRecord.DISCARDED_DUPLICATE # Book was a duplicate, so is discarded
    

# This function checks if the book is already in a s
def add_or_complete_book(booksDict: dict, book: Book) -> TypeOfRecord:
    bookTitle = book.title.casefold()
    if bookTitle not in booksDict: 
        booksDict[bookTitle] = book # Using title as key to avoid duplicates
        return  TypeOfRecord.ADDED # Book was added
    return complete_book(booksDict[bookTitle], book)
    

# This function groups the books by author or by publication year (if author is unknown)
def group_books_by_author_or_publication_year(books: dict) -> tuple[dict, dict]:
    groupedBooksAuthor = {}
    groupedBooksPubYear = {}
    for book in books.values():
        if book.author != AUTHOR_UNKNOWN:
            bookAuthor = book.author.casefold()
            groupedBooksAuthor.setdefault(bookAuthor, []).append(book)
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

    # Sorting by title
    books = dict(sorted(books.items(), key=itemgetter(0)))
        

    return sortedGroupedBooksAuthor, sortedGroupedBooksPubYear


def read_csv(FILE_PATH: str, booksDict: dict) -> None | dict:
    try:
        with open(FILE_PATH, mode="r", encoding="utf-8") as file:
            fileReader = csv.reader(file)

            # Skip header and check if it exists
            header = next(fileReader, None)  
            if header is None:
                print("Error: The csv file is empty.")
                return None
            
            countIncomingBooks = 0
            countAddedBooks = 0
            countDiscardedBooks = 0
            countDiscardedDuplicateBooks = 0
            countEnrichedDuplicateBooks = 0
            
            for row in fileReader:
                # Some validations respecting the number of columns. 
                # If there are some missing, they are filled with ""
                if len(row) == 0:
                    countDiscardedBooks += 1
                    continue
                elif len(row) > 3:
                    row = row[:3]
                else:
                    row += [""] * (3 - len(row))

                title, author, pubYear = row
                book = initialize_book(title, author, pubYear)    
                countIncomingBooks += 1

                if book is not None:
                    typeOfRecord = add_or_complete_book(booksDict, book)
                    if typeOfRecord == TypeOfRecord.ADDED:
                        countAddedBooks += 1
                    elif typeOfRecord == TypeOfRecord.ENRICHED_DUPLICATE:
                        countEnrichedDuplicateBooks += 1
                    else:
                        countDiscardedDuplicateBooks += 1
                else:
                    countDiscardedBooks += 1

            metrics = {
                "incoming_books": countIncomingBooks,
                "added_books": countAddedBooks,
                "discarded_books": countDiscardedBooks,
                "discarded_duplicate_books": countDiscardedDuplicateBooks,
                "enriched_duplicate_books": countEnrichedDuplicateBooks
            }

            return metrics
        
    except FileNotFoundError:
        print(f"Error: The file '{FILE_PATH}' was not found.")
        return None
        
        
def md_escape(text: str) -> str:
    text = str(text) # Ensure the input is a string
    # Escaping special characters for Markdown (&, <, >) to avoid formatting issues in the generated report
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") 


# Report generation in markdown format
def generate_report_md(booksDict: dict, groupedBooksAuthor: dict, groupedBooksPubYear: dict, metrics: dict) -> str:
    lines = []
    lines.append("# Library's Books Report")
    lines.append("")
    lines.append(f"_Generated in: {datetime.now().date()}_")
    lines.append("")
    lines.append("## Metrics")
    lines.append(f"From the given csv file, the following metrics were obtained:")
    lines.append(f"- **Total of processed books (rows):** _{metrics['incoming_books']}_")
    lines.append(f"- **Total of added books:** _{metrics['added_books']}_")
    lines.append(f"- **Total of discarded books:** _{metrics['discarded_books']}_")
    lines.append(f"- **Total of duplicated and discarded books:** _{metrics['discarded_duplicate_books']}_")
    lines.append(f"- **Duplicated books used to enrich previously registered books:** _{metrics['enriched_duplicate_books']}_")
    lines.append("")

    lines.append("## Books catalog")
    for book in booksDict.values():
        if book.publication_year != 0:
            lines.append(f"- **Title:** _{md_escape(book.title)}_ **- Author:** _{md_escape(book.author)}_ **- Publication Year:** _{book.publication_year}_")
        else:
            lines.append(f"- **Title:** _{md_escape(book.title)}_ **- Author:** _{md_escape(book.author)}_ **- Publication Year:** _Unknown_")
    lines.append("")

    lines.append("## Books grouped by author")
    for author in groupedBooksAuthor:
        lines.append("<details open>")
        booksFromAuthor = groupedBooksAuthor[author]
        caseSensitiveAuthor = booksFromAuthor[0].author
        lines.append(f"  <summary><strong>{md_escape(caseSensitiveAuthor)}</strong> ({len(booksFromAuthor)})</summary>")
        lines.append("")
        for book in booksFromAuthor:
            if book.publication_year != 0:
                lines.append(f"  - {md_escape(book.title)} - _{book.publication_year}_")
            else:
                lines.append(f"  - {md_escape(book.title)} - _Unknown Publication Year_")
        lines.append("</details>")
    lines.append("")

    lines.append("## Books grouped by publication year (With missing author)")
    for pubYear in groupedBooksPubYear:
        lines.append("<details open>")
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
    booksDict = {}
    metrics = read_csv(FILE_PATH, booksDict)
    groupedBooksAuthor, groupedBooksPubYear = group_books_by_author_or_publication_year(booksDict)

    if metrics is None:
        print("Error reading the csv file or csv file not found. Exiting the program.")
    else:
        report_md = generate_report_md(booksDict, groupedBooksAuthor, groupedBooksPubYear, metrics)
        with open("report.md", "w", encoding="utf-8") as f:
            f.write(report_md)
            print("Report generated successfully in 'report.md' file.")


if __name__ == "__main__":
    main()