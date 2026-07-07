from app.database import SessionLocal
from app.models import Book, Member, BookStatus


def seed_data():
    db = SessionLocal()
    try:
        print("Starting database seeding...")

        # Test books
        books_data = [
            {
                "title": "Clean Code",
                "author": "Robert C. Martin",
                "isbn": "9780132350884",
            },
            {
                "title": "The Pragmatic Programmer",
                "author": "Andrew Hunt",
                "isbn": "9780135957059",
            },
            {
                "title": "Designing Data-Intensive Applications",
                "author": "Martin Kleppmann",
                "isbn": "9781449373320",
            },
        ]

        # Test members
        members_data = [
            {"name": "John Doe", "email": "john@example.com"},
            {"name": "Jane Smith", "email": "jane@example.com"},
        ]

        # Seed Books
        for book_info in books_data:
            existing_book = (
                db.query(Book).filter(Book.isbn == book_info["isbn"]).first()
            )
            if not existing_book:
                book = Book(
                    title=book_info["title"],
                    author=book_info["author"],
                    isbn=book_info["isbn"],
                    status=BookStatus.AVAILABLE,
                )
                db.add(book)
                print(f"Seeded book: '{book.title}'")
            else:
                print(f"Book with ISBN {book_info['isbn']} already exists. Skipping.")

        # Seed Members
        for member_info in members_data:
            existing_member = (
                db.query(Member).filter(Member.email == member_info["email"]).first()
            )
            if not existing_member:
                member = Member(
                    name=member_info["name"], email=member_info["email"]
                )
                db.add(member)
                print(f"Seeded member: '{member.name}'")
            else:
                print(
                    f"Member with email {member_info['email']} already exists. Skipping."
                )

        db.commit()
        print("Database seeding completed successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
