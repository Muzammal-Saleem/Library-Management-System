from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app import schemas, security, services
from app.database import get_db
from app.models import MemberRole, Loan, LoanStatus

router = APIRouter(
    prefix="/loans",
    tags=["loans"]
)

class BookReturnRequest(BaseModel):
    book_id: int

@router.post("/borrow", response_model=schemas.LoanResponse, status_code=status.HTTP_201_CREATED)
def borrow_book(
    loan: schemas.LoanCreate,
    db: Session = Depends(get_db),
    current_user: schemas.MemberResponse = Depends(security.get_current_user)
):
    # Business authorization rules:
    # Members can only borrow books for themselves.
    # Librarians can borrow books for anyone.
    if current_user.role == MemberRole.MEMBER and current_user.id != loan.member_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Members can only borrow books for themselves. To borrow for another user, you must be a Librarian."
        )

    try:
        return services.borrow_book(db, book_id=loan.book_id, member_id=loan.member_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/return", response_model=schemas.LoanResponse, status_code=status.HTTP_200_OK)
def return_book(
    req: BookReturnRequest,
    db: Session = Depends(get_db),
    current_user: schemas.MemberResponse = Depends(security.get_current_user)
):
    # Business authorization rules:
    # Members can only return books that they borrowed themselves.
    # Librarians can return any book.
    active_loan = db.query(Loan).filter(
        Loan.book_id == req.book_id,
        Loan.status == LoanStatus.ACTIVE
    ).first()

    if not active_loan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No active loan record found for book ID {req.book_id}."
        )

    if current_user.role == MemberRole.MEMBER and active_loan.member_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Members can only return books that they checked out themselves."
        )

    try:
        return services.return_book(db, book_id=req.book_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
