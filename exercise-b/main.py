# Title, Author, PublicationYear
import csv
from dataclasses import dataclass
from datetime import datetime
from enum import auto, Enum


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
            if bookAuthor not in groupedBooksAuthor:
                groupedBooksAuthor[book.author] = []
            groupedBooksAuthor[book.author].append(book)
        else:
            bookPubYear = book.publication_year
            if bookPubYear not in groupedBooksPubYear:
                groupedBooksPubYear[bookPubYear] = []
            groupedBooksPubYear[bookPubYear].append(book)
    return groupedBooksAuthor, groupedBooksPubYear


def read_csv(FILE_PATH: str, booksSet: dict):
    with open(FILE_PATH, mode="r", encoding="utf-8") as file:
        fileReader = csv.reader(file)
        ### COULD GO A CONDITIONAL TO CHECK IF THERE IS A HEADER
        fileReader.__next__()  # Skip header

        countIncomingRecords = 0
        countAddedBooks = 0
        countDiscardedBooks = 0
        countDiscardedDuplicateBooks = 0
        countEnrichedDuplicateBooks = 0
        
        for row in fileReader:
            countIncomingRecords += 1
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
            else:
                countDiscardedBooks += 1
                        
        
        print(f"\nTotal incoming records: {countIncomingRecords}")
        print(f"Total books added: {countAddedBooks}")
        print(f"Total books discarded: {countDiscardedBooks}")
        print(f"Total books duplicated and discarded: {countDiscardedDuplicateBooks}")
        print(f"Total books duplicated and enriched: {countEnrichedDuplicateBooks}")
        print(f"Integrity check: {countAddedBooks + countDiscardedBooks + countDiscardedDuplicateBooks + countEnrichedDuplicateBooks}")
            

def md_escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def generate_report_md(groupedBooksAuthor, groupedBooksPubYear) -> str:
    books = list(booksSet.values())

    # Resumen
    total = len(books)
    missing_author = sum(1 for b in books if b.author == "Author Unknown")
    missing_year = sum(1 for b in books if b.publication_year == 0)

    # Agrupar (ideal: arreglar tu grouping para que use keys consistentes)
    by_author = {}
    by_year = {}
    for b in books:
        if b.author != "Author Unknown":
            by_author.setdefault(b.author, []).append(b)
        if b.publication_year != 0:
            by_year.setdefault(b.publication_year, []).append(b)

    # Orden “bonito”
    for a in by_author:
        by_author[a].sort(key=lambda x: (x.publication_year or 99999, x.title))
    for y in by_year:
        by_year[y].sort(key=lambda x: (x.author, x.title))

    lines = []
    lines.append("# Reporte de libros")
    lines.append("")
    lines.append(f"_Generado: {datetime.now().date()}_")
    lines.append("")
    lines.append("## Resumen")
    lines.append(f"- Total únicos: {total}")
    lines.append(f"- Sin autor: {missing_author}")
    lines.append(f"- Sin año: {missing_year}")
    lines.append("")
    lines.append("## Agrupados por autor")

    for author in sorted(by_author.keys(), key=str.casefold):
        items = by_author[author]
        lines.append("<details>")
        lines.append(f"  <summary><strong>{md_escape(author)}</strong> ({len(items)})</summary>")
        lines.append("")
        for b in items:
            year = b.publication_year if b.publication_year != 0 else "s/año"
            lines.append(f"  - {md_escape(b.title)} ({year})")
        lines.append("</details>")
        lines.append("")

    lines.append("## Agrupados por año")
    for year in sorted(by_year.keys()):
        items = by_year[year]
        lines.append("<details>")
        lines.append(f"  <summary><strong>{year}</strong> ({len(items)})</summary>")
        lines.append("")
        for b in items:
            lines.append(f"  - {md_escape(b.title)} — {md_escape(b.author)}")
        lines.append("</details>")
        lines.append("")

    return "\n".join(lines)





def main():
    # Lector de csv
    FILE_PATH = "books.csv"
    booksSet = {} # Using a set to avoid duplicates
    read_csv(FILE_PATH, booksSet)
    
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

    # report_md = generate_report_md(groupedBooksAuthor, groupedBooksPubYear)
    # with open("report.md", "w", encoding="utf-8") as f:
    #     f.write(report_md)
    
    # mostrar resultados en .md
    # mostrar registros descartados, ingresados, duplicados, egresados, registros sin autor, registros sin año


if __name__ == "__main__":
    main()