from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import schemas, security, services
from app.database import get_db
from app.models import Member

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/signup", response_model=schemas.MemberResponse, status_code=status.HTTP_201_CREATED)
def signup(member: schemas.MemberCreate, db: Session = Depends(get_db)):
    hashed_pwd = security.get_password_hash(member.password)
    try:
        return services.register_member(
            db,
            name=member.name,
            email=member.email,
            hashed_password=hashed_pwd
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2 uses the 'username' parameter to pass the login identifier (which is email in our case)
    member = db.query(Member).filter(Member.email == form_data.username).first()
    
    if not member or not security.verify_password(form_data.password, member.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate token payload
    access_token = security.create_access_token(
        data={"sub": member.email, "role": member.role.value}
    )
    return {"access_token": access_token, "token_type": "bearer"}
