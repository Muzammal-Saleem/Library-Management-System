from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import schemas, security, services
from app.database import get_db
from app.models import Member

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
    return db.query(Member).order_by(Member.id).all()
