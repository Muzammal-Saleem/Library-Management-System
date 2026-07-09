from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Book, BookStatus, Loan, LoanStatus
from app.services.member import get_member


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
