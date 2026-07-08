from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app import schemas, security, services
from app.database import get_db

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
