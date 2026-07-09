import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app import schemas, security, services
from app.database import get_db, SessionLocal
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


@router.post("/report", status_code=status.HTTP_202_ACCEPTED)
def request_library_report(
    background_tasks: BackgroundTasks,
    current_librarian: schemas.MemberResponse = Depends(security.get_current_librarian)
):
    """Triggers report compilation in the background (Librarians only)."""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{timestamp}.txt"
    
    # Register the background task to run off-request
    background_tasks.add_task(
        services.generate_library_report_task,
        db_session_factory=SessionLocal,
        report_filename=filename
    )
    
    return {
        "status": "Report generation started in the background",
        "filename": filename
    }


@router.get("/reports/{filename}")
def download_library_report(
    filename: str,
    current_librarian: schemas.MemberResponse = Depends(security.get_current_librarian)
):
    """Allows downloading a generated report file directly (Librarians only)."""
    # Prevent directory traversal vulnerability
    safe_filename = os.path.basename(filename)
    filepath = os.path.join("reports", safe_filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report file not found."
        )
        
    return FileResponse(
        path=filepath,
        media_type="text/plain",
        filename=safe_filename
    )
