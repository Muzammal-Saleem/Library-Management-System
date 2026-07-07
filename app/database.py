import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

# Retrieve database connection parameters from environment variables
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres_password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "library")

# Construct connection URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create engine
engine = create_engine(DATABASE_URL)

# SessionLocal class for creating new sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our declarative models
Base = declarative_base()


def get_db():
    """Helper to get a database session and close it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_connection():
    """Simple check to verify database connection is healthy."""
    try:
        # Try to connect and execute a simple query
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Database connection check: SUCCESSFUL!")
        return True
    except Exception as e:
        print(f"Database connection check: FAILED! ({e})")
        return False
