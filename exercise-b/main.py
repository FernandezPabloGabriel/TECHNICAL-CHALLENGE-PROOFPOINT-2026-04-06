# Title, Author, PublicationYear
import csv
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Book:
    title: str # Always present
    author: str
    publication_year: int

    def __hash__(self):
        return hash((self.title, self.author))
    
    def __eq__(self, other):
        if not isinstance(other, Book):
            return NotImplemented
        return self.title == other.title and self.author == other.author


def is_book_duplicated(booksSet: set, book: Book):
    if book in booksSet:
        if book.author == "Author Unknown":
            return True
    return 


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


def read_csv(FILE_PATH: str, booksSet: set):
    with open(FILE_PATH, mode="r", encoding="utf-8") as file:
        fileReader = csv.reader(file)
        ### COULD GO A CONDITIONAL TO CHECK IF THERE IS A HEADER
        fileReader.__next__()  # Skip header

        for row in fileReader:
            title=row[0].strip()
            author=row[1].strip()
            pubYear=row[2].strip()
            book = initialize_book(title, author, pubYear)

            if book is not None and not is_book_duplicated(booksSet, book): 
                booksSet.append(book)
                
        for book in booksSet:
            print(f"Title: {book.title}, Author: {book.author}, Publication Year: {book.publication_year}")
            


def main():
    # Lector de csv
    FILE_PATH = "books.csv"
    booksSet = [] # Using a set to avoid duplicates
    read_csv(FILE_PATH, booksSet)
    
    # mostrar resultados


if __name__ == "__main__":
    main()