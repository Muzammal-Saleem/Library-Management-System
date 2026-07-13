import enum
from sqlalchemy import Column, Integer, String, Enum as SqlEnum
from sqlalchemy.orm import relationship
from app.database import Base


class BookStatus(str, enum.Enum):
    AVAILABLE = "Available"
    LOANED = "Loaned"


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
    quantity = Column(Integer, default=1, nullable=False)

    # Relationships
    loans = relationship("Loan", back_populates="book", cascade="all, delete-orphan")

    @property
    def available_count(self) -> int:
        active_loans = sum(1 for loan in self.loans if loan.status == "Active")
        return max(0, self.quantity - active_loans)

    @property
    def total_count(self) -> int:
        return self.quantity

    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}', status='{self.status.value}')>"
