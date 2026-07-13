import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, books, members, loans
from app.database import check_connection

app = FastAPI(
    title="Library Management System API",
    description="A Web API to manage books, members, and book loans.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    os.makedirs("reports", exist_ok=True)

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


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("API_IP", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run("app.main:app", host=host, port=port, reload=False)
