import enum
import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SqlEnum
from sqlalchemy.orm import relationship
from app.database import Base


class BookStatus(str, enum.Enum):
    AVAILABLE = "Available"
    LOANED = "Loaned"


class LoanStatus(str, enum.Enum):
    ACTIVE = "Active"
    RETURNED = "Returned"


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    isbn = Column(String(20), unique=True, index=True, nullable=False)
    status = Column(
        SqlEnum(BookStatus, name="book_status_enum", values_callable=lambda obj: [e.value for e in obj]),
        default=BookStatus.AVAILABLE,
        nullable=False,
    )

    # Relationships
    loans = relationship("Loan", back_populates="book", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}', status='{self.status.value}')>"


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    registration_date = Column(
        DateTime, default=datetime.datetime.utcnow, nullable=False
    )

    # Relationships
    loans = relationship("Loan", back_populates="member", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Member(id={self.id}, name='{self.name}', email='{self.email}')>"


class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    loan_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    return_date = Column(DateTime, nullable=True)
    status = Column(
        SqlEnum(LoanStatus, name="loan_status_enum", values_callable=lambda obj: [e.value for e in obj]),
        default=LoanStatus.ACTIVE,
        nullable=False,
    )

    # Relationships
    book = relationship("Book", back_populates="loans")
    member = relationship("Member", back_populates="loans")

    def __repr__(self):
        return f"<Loan(id={self.id}, book_id={self.book_id}, member_id={self.member_id}, status='{self.status.value}')>"
