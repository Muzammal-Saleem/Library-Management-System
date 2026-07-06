from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app import crud, schemas
from app.database import get_db

router = APIRouter(
    prefix="/loans",
    tags=["loans"]
)

class BookReturnRequest(BaseModel):
    book_id: int

@router.post("/borrow", response_model=schemas.LoanResponse, status_code=status.HTTP_201_CREATED)
def borrow_book(loan: schemas.LoanCreate, db: Session = Depends(get_db)):
    try:
        return crud.borrow_book(db, book_id=loan.book_id, member_id=loan.member_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/return", response_model=schemas.LoanResponse, status_code=status.HTTP_200_OK)
def return_book(req: BookReturnRequest, db: Session = Depends(get_db)):
    try:
        return crud.return_book(db, book_id=req.book_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
