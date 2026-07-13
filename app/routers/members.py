from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import schemas, security, services
from app.database import get_db
from app.models import Member, Loan

router = APIRouter(
    prefix="/members",
    tags=["members"]
)

@router.post("/", response_model=schemas.MemberResponse, status_code=status.HTTP_201_CREATED)
def register_member(
    member: schemas.MemberCreate,
    db: Session = Depends(get_db),
    current_librarian: schemas.MemberResponse = Depends(security.get_current_librarian)
):
    hashed_pwd = security.get_password_hash(member.password)
    try:
        return services.register_member(db, name=member.name, email=member.email, hashed_password=hashed_pwd)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[schemas.MemberResponse])
def get_all_members(
    db: Session = Depends(get_db),
    current_librarian: schemas.MemberResponse = Depends(security.get_current_librarian)
):
    return db.query(Member).filter(Member.is_active).order_by(Member.id).all()

@router.delete("/{member_id}")
def delete_member(
    member_id: int,
    db: Session = Depends(get_db),
    current_librarian: schemas.MemberResponse = Depends(security.get_current_librarian)
):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found."
        )
    member.is_active = False
    db.commit()
    return {"detail": "Member account successfully deactivated."}

@router.get("/{member_id}/history", response_model=List[schemas.LoanResponse])
def get_member_history(
    member_id: int,
    db: Session = Depends(get_db),
    current_librarian: schemas.MemberResponse = Depends(security.get_current_librarian)
):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found."
        )
    from sqlalchemy.orm import joinedload
    return db.query(Loan).filter(Loan.member_id == member_id).options(
        joinedload(Loan.book),
        joinedload(Loan.member)
    ).order_by(Loan.loan_date.desc()).all()
