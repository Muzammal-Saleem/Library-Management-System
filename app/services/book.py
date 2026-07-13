from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import Book, BookStatus


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
