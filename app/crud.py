from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import Book, BookStatus, Member, Loan, LoanStatus


# Book CRUD
def add_book(db: Session, title: str, author: str, isbn: str) -> Book:
    db_book = Book(title=title, author=author, isbn=isbn, status=BookStatus.AVAILABLE)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def get_books(db: Session):
    return db.query(Book).order_by(Book.id).all()


def search_books(db: Session, query: str):
    search_pattern = f"%{query}%"
    return (
        db.query(Book)
        .filter(
            or_(
                Book.title.ilike(search_pattern),
                Book.author.ilike(search_pattern),
                Book.isbn.ilike(search_pattern),
            )
        )
        .all()
    )


def remove_book(db: Session, book_id: int) -> bool:
    book = db.query(Book).filter(Book.id == book_id).first()
    if book:
        db.delete(book)
        db.commit()
        return True
    return False


# Member CRUD
def register_member(db: Session, name: str, email: str) -> Member:
    existing = db.query(Member).filter(Member.email == email).first()
    if existing:
        raise ValueError(f"Member with email '{email}' already registered.")

    db_member = Member(name=name, email=email)
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


def get_member(db: Session, member_id: int) -> Member:
    return db.query(Member).filter(Member.id == member_id).first()


# Loan CRUD
def borrow_book(db: Session, book_id: int, member_id: int) -> Loan:
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise ValueError(f"Book with ID {book_id} does not exist.")

    if book.status == BookStatus.LOANED:
        raise ValueError(
            f"Book '{book.title}' is already checked out (loaned) by another member."
        )

    member = get_member(db, member_id)
    if not member:
        raise ValueError(f"Member with ID {member_id} does not exist.")

    # Create the loan record
    loan = Loan(book_id=book_id, member_id=member_id, status=LoanStatus.ACTIVE)
    # Update book status to Loaned
    book.status = BookStatus.LOANED

    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


def return_book(db: Session, book_id: int) -> Loan:
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise ValueError(f"Book with ID {book_id} does not exist.")

    # Find the active loan for this book
    loan = (
        db.query(Loan)
        .filter(Loan.book_id == book_id, Loan.status == LoanStatus.ACTIVE)
        .first()
    )
    if not loan:
        raise ValueError(f"No active loan record found for book ID {book_id}.")

    # Update loan info
    loan.status = LoanStatus.RETURNED
    loan.return_date = datetime.utcnow()

    # Make the book available again
    book.status = BookStatus.AVAILABLE

    db.commit()
    db.refresh(loan)
    return loan
