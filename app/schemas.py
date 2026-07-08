from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from app.models import BookStatus, LoanStatus, MemberRole


# Book Schemas
class BookBase(BaseModel):
    title: str
    author: str
    isbn: str


class BookCreate(BookBase):
    pass


class BookResponse(BookBase):
    id: int
    status: BookStatus

    model_config = ConfigDict(from_attributes=True)


# Member Schemas
class MemberBase(BaseModel):
    name: str
    email: str


class MemberCreate(MemberBase):
    password: str  # Required for account creation


class MemberResponse(MemberBase):
    id: int
    role: MemberRole
    registration_date: datetime

    model_config = ConfigDict(from_attributes=True)


# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[MemberRole] = None


# Loan Schemas
class LoanBase(BaseModel):
    book_id: int
    member_id: int


class LoanCreate(LoanBase):
    pass


class LoanResponse(LoanBase):
    id: int
    loan_date: datetime
    return_date: Optional[datetime] = None
    status: LoanStatus

    model_config = ConfigDict(from_attributes=True)
