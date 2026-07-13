import enum
import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum as SqlEnum
from sqlalchemy.orm import relationship
from app.database import Base


class LoanStatus(str, enum.Enum):
    ACTIVE = "Active"
    RETURNED = "Returned"


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

    @property
    def book_title(self) -> str:
        return self.book.title if self.book else ""

    @property
    def member_name(self) -> str:
        return self.member.name if self.member else ""

    @property
    def borrowed_at(self):
        return self.loan_date

    @property
    def returned_at(self):
        return self.return_date

    def __repr__(self):
        return f"<Loan(id={self.id}, book_id={self.book_id}, member_id={self.member_id}, status='{self.status.value}')>"
