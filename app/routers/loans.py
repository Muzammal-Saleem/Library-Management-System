import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel
from typing import List, Optional
from celery.result import AsyncResult

from app import schemas, security, services
from app.database import get_db
from app.models import MemberRole, Loan, LoanStatus
from app.celery_app import celery_app
from app.tasks import generate_library_report_task

router = APIRouter(
    prefix="/loans",
    tags=["loans"]
)

class BookReturnRequest(BaseModel):
    book_id: int


@router.get("/", response_model=List[schemas.LoanResponse])
def list_loans(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: schemas.MemberResponse = Depends(security.get_current_user)
):
    query = db.query(Loan).options(joinedload(Loan.book), joinedload(Loan.member))
    
    if status == "active":
        query = query.filter(Loan.status == LoanStatus.ACTIVE)
    elif status == "returned":
        query = query.filter(Loan.status == LoanStatus.RETURNED)

    if current_user.role == MemberRole.MEMBER:
        query = query.filter(Loan.member_id == current_user.id)
        
    return query.order_by(Loan.loan_date.desc()).all()


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

    if current_user.role != MemberRole.LIBRARIAN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Librarians are allowed to return books."
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
    current_librarian: schemas.MemberResponse = Depends(security.get_current_librarian)
):
    """Triggers report compilation asynchronously via Celery (Librarians only)."""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{timestamp}.txt"
    
    # Trigger the Celery task
    task = generate_library_report_task.delay(filename)
    
    return {
        "status": "processing",
        "task_id": task.id,
        "filename": filename
    }


@router.get("/report/status/{task_id}")
def get_report_status(
    task_id: str,
    current_librarian: schemas.MemberResponse = Depends(security.get_current_librarian)
):
    """Checks the status of a report compilation task (Librarians only)."""
    res = AsyncResult(task_id, app=celery_app)
    
    response_data = {
        "task_id": task_id,
        "status": res.status,  # PENDING, STARTED, SUCCESS, FAILURE
    }
    
    if res.status == "SUCCESS":
        response_data["result"] = res.result
    elif res.status == "FAILURE":
        response_data["error"] = str(res.result)
        
    return response_data


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
