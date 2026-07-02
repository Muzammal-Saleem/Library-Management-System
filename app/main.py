import os
import psycopg2


def main():
    print("Library Management System CLI is running!")
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "postgres"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres")
        )
        print("Database connection check: SUCCESSFUL!")
        conn.close()
    except Exception as e:
        print(f"Database connection check: FAILED! ({e})")


if __name__ == "__main__":
    main()
