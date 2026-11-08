from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Iterator

class LibraryError(Exception):
    pass

class BookNotAvailable(LibraryError):
    pass

class LoanNotActive(LibraryError):
    pass

class ItemStatus(Enum):
    AVAILABLE = "available"
    BORROWED = "borrowed"

class LoanStatus(Enum):
    ACTIVE = "active"
    RETURNED = "returned"

class TimestampMixin:
    updated_at: datetime

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)

@dataclass
class LibraryItem(TimestampMixin, ABC):
    title: str
    status: ItemStatus = field(
        default=ItemStatus.AVAILABLE,
        init=False,
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc),
        init=False,
    )

    @abstractmethod
    def description(self) -> str:
        pass

    def borrow(self) -> None:
        if self.status == ItemStatus.BORROWED:
            raise BookNotAvailable(f"{self.title} is unavailable")

        self.status = ItemStatus.BORROWED
        self.touch()

    def return_item(self) -> None:
        if self.status == ItemStatus.AVAILABLE:
            raise LibraryError(f"{self.title} is already available")

        self.status = ItemStatus.AVAILABLE
        self.touch()

@dataclass
class Book(LibraryItem):
    author: str

    def description(self) -> str:
        return f"Book: {self.title}, author: {self.author}"
@dataclass
class Magazine(LibraryItem):
    issuenumber: int

    def description(self) -> str:
        return f"Magazine: {self.title}, issue: {self.issuenumber}"
@dataclass
class Reader:
    name: str

@dataclass
class Loan:
    item: LibraryItem
    reader: Reader
    status: LoanStatus = field(
        default=LoanStatus.ACTIVE,
        init=False,
    )


class Library:
    def __init__(self) -> None:
        self.items: list[LibraryItem] = []
        self.readers: list[Reader] = []
        self.loans: list[Loan] = []

    def add_item(self, item: LibraryItem) -> None:
        self.items.append(item)

    def add_reader(self, reader: Reader) -> None:
        self.readers.append(reader)

    def lend(self, item: LibraryItem, reader: Reader) -> Loan:
        if not any(existing is item for existing in self.items):
            raise LibraryError("Item is not registered")

        if not any(existing is reader for existing in self.readers):
            raise LibraryError("Reader is not registered")

        item.borrow()
        loan = Loan(item=item, reader=reader)
        self.loans.append(loan)
        return loan

    def return_loan(self, loan: Loan) -> None:
        if not any(existing is loan for existing in self.loans):
            raise LibraryError("Loan does not belong to this library")

        if loan.status == LoanStatus.RETURNED:
            raise LoanNotActive("Loan has already been returned")

        loan.item.return_item()
        loan.status = LoanStatus.RETURNED

    @contextmanager
    def transaction(self) -> Iterator[None]:
        """Restore library state if an operation fails."""
        saved_items = self.items.copy()
        saved_readers = self.readers.copy()
        saved_loans = self.loans.copy()

        item_states = [
            (item, item.status, item.updated_at)
            for item in saved_items
        ]
        loan_states = [
            (loan, loan.status)
            for loan in saved_loans
        ]

        try:
            yield
        except Exception:
            self.items[:] = saved_items
            self.readers[:] = saved_readers
            self.loans[:] = saved_loans

            for item, status, updated_at in item_states:
                item.status = status
                item.updated_at = updated_at

            for loan, status in loan_states:
                loan.status = status

            raise


def main() -> None:
    library = Library()

    book = Book("Why We Sleep", "Matthew Walker")
    magazine = Magazine("Science Weekly", 12)
    reader = Reader("Aibek")

    library.add_item(book)
    library.add_item(magazine)
    library.add_reader(reader)

    print(book.description())
    print(magazine.description())

    with library.transaction():
        loan = library.lend(book, reader)

    print(f"Borrowed: {book.title}")
    print(f"Status: {book.status.value}")

    with library.transaction():
        library.return_loan(loan)

    print(f"Returned: {book.title}")
    print(f"Status: {book.status.value}")

    with library.transaction():
        active_loan = library.lend(book, reader)

    try:
        with library.transaction():
            library.lend(book, reader)
    except BookNotAvailable as error:
        print(f"Handled error: {error}")

    try:
        with library.transaction():
            library.lend(magazine, reader)
            library.lend(book, reader)
    except BookNotAvailable:
        print("Transaction failed; changes were rolled back")

    assert magazine.status == ItemStatus.AVAILABLE
    assert len(library.loans) == 2
    print(f"Magazine after rollback: {magazine.status.value}")

    with library.transaction():
        library.return_loan(active_loan)

    print("Demo completed")


if __name__ == "__main__":
    main()