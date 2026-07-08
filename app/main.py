from fastapi import FastAPI
from app.routers import auth, books, members, loans
from app.database import check_connection

app = FastAPI(
    title="Library Management System API",
    description="A Web API to manage books, members, and book loans.",
    version="1.0.0"
)

# Include resource routers
app.include_router(auth.router)
app.include_router(books.router)
app.include_router(members.router)
app.include_router(loans.router)

@app.get("/", tags=["health"])
def health_check():
    db_healthy = check_connection()
    return {
        "status": "online",
        "database": "connected" if db_healthy else "disconnected",
        "docs_url": "/docs"
    }
