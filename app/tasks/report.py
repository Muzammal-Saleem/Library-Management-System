import os
import time
from datetime import datetime
from app.celery_app import celery_app
from app.database import SessionLocal
from app.models import Book, BookStatus, Member, Loan, LoanStatus


@celery_app.task(name="app.tasks.report.generate_library_report_task")
def generate_library_report_task(report_filename: str) -> str:
    """Celery background task to generate a library summary report with an artificial delay."""
    print(f"Background Task: Starting report generation for {report_filename}...")
    
    # Artificial delay of 4 seconds as requested by the user
    print("Background Task: Simulating 4-second delay...")
    time.sleep(4)
    
    db = SessionLocal()
    try:
        # Query all records
        books = db.query(Book).all()
        members = db.query(Member).all()
        active_loans = db.query(Loan).filter(Loan.status == LoanStatus.ACTIVE).all()
        
        # Calculate stats
        total_books = len(books)
        loaned_books = sum(1 for b in books if b.status == BookStatus.LOANED)
        available_books = total_books - loaned_books
        
        # Ensure reports folder exists
        os.makedirs("reports", exist_ok=True)
        
        # Write report data to file
        report_path = os.path.join("reports", report_filename)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("==================================================\n")
            f.write("       LIBRARY SYSTEM STATUS REPORT               \n")
            f.write("==================================================\n\n")
            f.write(f"Generated at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n")
            
            f.write("--- CATALOG SUMMARY ---\n")
            f.write(f"Total Cataloged Books: {total_books}\n")
            f.write(f"Available for Loan  : {available_books}\n")
            f.write(f"Currently Loaned     : {loaned_books}\n")
            f.write(f"Registered Members   : {len(members)}\n\n")
            
            f.write("--- ACTIVE LOANS ---\n")
            if not active_loans:
                f.write("No active checkouts currently.\n")
            else:
                for idx, loan in enumerate(active_loans, 1):
                    f.write(f"{idx}. Loan ID: {loan.id}\n")
                    f.write(f"   Book: '{loan.book.title}' (ISBN: {loan.book.isbn})\n")
                    f.write(f"   Borrowed By: {loan.member.name} (ID: {loan.member.id}, Email: {loan.member.email})\n")
                    f.write(f"   Checked Out on: {loan.loan_date.strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n")
                    
            f.write("==================================================\n")
            f.write("Report completed successfully.\n")
            
        print(f"Background Task: Report {report_filename} successfully saved.")
        return f"Report {report_filename} generated successfully."
        
    except Exception as e:
        error_msg = f"Error generating report {report_filename}: {e}"
        print(f"Background Task Error: {error_msg}")
        raise e
    finally:
        db.close()
