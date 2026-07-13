from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app import schemas, security, services
from app.database import get_db
from app.models import Book, BookStatus, Loan, LoanStatus

router = APIRouter(
    prefix="/books",
    tags=["books"]
)

@router.post("/", response_model=schemas.BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(
    book: schemas.BookCreate,
    db: Session = Depends(get_db),
    current_librarian: schemas.MemberResponse = Depends(security.get_current_librarian)
):
    return services.add_book(db, title=book.title, author=book.author, isbn=book.isbn)

@router.get("/", response_model=List[schemas.BookResponse])
def read_books(search: Optional[str] = None, db: Session = Depends(get_db)):
    if search:
        return services.search_books(db, query=search)
    return services.get_books(db)

@router.delete("/{book_id}")
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_librarian: schemas.MemberResponse = Depends(security.get_current_librarian)
):
    success = services.remove_book(db, book_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found."
        )
    return {"detail": "Book successfully deleted."}

@router.post("/{book_id}/restack", response_model=schemas.BookResponse)
def restack_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_librarian: schemas.MemberResponse = Depends(security.get_current_librarian)
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found."
        )
    book.quantity += 1
    
    # Update status to Available if it was Loaned (quantity is now > active_loans)
    active_loans = db.query(Loan).filter(Loan.book_id == book_id, Loan.status == LoanStatus.ACTIVE).count()
    if active_loans < book.quantity:
        book.status = BookStatus.AVAILABLE
        
    db.commit()
    db.refresh(book)
    return book

@router.post("/{book_id}/destack", response_model=schemas.BookResponse)
def destack_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_librarian: schemas.MemberResponse = Depends(security.get_current_librarian)
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found."
        )
    active_loans = db.query(Loan).filter(Loan.book_id == book_id, Loan.status == LoanStatus.ACTIVE).count()
    if book.quantity <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot reduce quantity below 1. Delete the book instead."
        )
    if book.quantity <= active_loans:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot reduce quantity below the number of active loans."
        )
    book.quantity -= 1
    
    # Update status to Loaned if quantity is now equal to active_loans
    if active_loans >= book.quantity:
        book.status = BookStatus.LOANED
        
    db.commit()
    db.refresh(book)
    return book
