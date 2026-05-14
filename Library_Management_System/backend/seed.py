"""
Seed the database with sample books, borrowers, and transactions.
Called automatically on first startup when the DB is empty.
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import models


BOOKS = [
    # Technology
    {"title": "Clean Code",                    "author": "Robert C. Martin",    "category": "Technology",  "isbn": "978-0-13-110362-7"},
    {"title": "The Pragmatic Programmer",      "author": "Andrew Hunt",         "category": "Technology",  "isbn": "978-0-13-595705-9"},
    {"title": "Design Patterns",               "author": "Gang of Four",        "category": "Technology",  "isbn": "978-0-20-163361-5"},
    {"title": "You Don't Know JS",             "author": "Kyle Simpson",        "category": "Technology",  "isbn": "978-1-49-190552-6"},
    {"title": "Python Crash Course",           "author": "Eric Matthes",        "category": "Technology",  "isbn": "978-1-59-327603-4"},
    # Science
    {"title": "A Brief History of Time",       "author": "Stephen Hawking",     "category": "Science",     "isbn": "978-0-55-305340-1"},
    {"title": "Cosmos",                        "author": "Carl Sagan",          "category": "Science",     "isbn": "978-0-34-533943-4"},
    {"title": "The Gene",                      "author": "Siddhartha Mukherjee","category": "Science",     "isbn": "978-1-47-673710-4"},
    # Management & Self-Help
    {"title": "Atomic Habits",                 "author": "James Clear",         "category": "Self-Help",   "isbn": "978-0-73-521129-2"},
    {"title": "Good to Great",                 "author": "Jim Collins",         "category": "Management",  "isbn": "978-0-06-662099-2"},
    {"title": "Deep Work",                     "author": "Cal Newport",         "category": "Self-Help",   "isbn": "978-1-45-554849-3"},
    # History & Society
    {"title": "Sapiens",                       "author": "Yuval Noah Harari",   "category": "History",     "isbn": "978-0-06-231609-7"},
    {"title": "The Art of War",                "author": "Sun Tzu",             "category": "History",     "isbn": "978-1-59-030171-2"},
    # Fiction
    {"title": "To Kill a Mockingbird",         "author": "Harper Lee",          "category": "Fiction",     "isbn": "978-0-06-112008-4"},
    {"title": "1984",                          "author": "George Orwell",       "category": "Fiction",     "isbn": "978-0-45-228423-4"},
    {"title": "The Alchemist",                 "author": "Paulo Coelho",        "category": "Fiction",     "isbn": "978-0-06-231500-7"},
    {"title": "Harry Potter and the Sorcerer's Stone", "author": "J.K. Rowling","category": "Fiction",     "isbn": "978-0-43-970818-8"},
    # Data & Analytics
    {"title": "Data Science from Scratch",     "author": "Joel Grus",          "category": "Data Science", "isbn": "978-1-49-194113-9"},
    {"title": "Storytelling with Data",        "author": "Cole Nussbaumer",    "category": "Data Science", "isbn": "978-1-11-922751-2"},
    {"title": "The Signal and the Noise",      "author": "Nate Silver",        "category": "Data Science", "isbn": "978-0-14-312508-2"},
]

BORROWERS = [
    {"borrower_name": "Alice Johnson",   "email": "alice.johnson@example.com",  "phone": "+91 9876543210"},
    {"borrower_name": "Bob Williams",    "email": "bob.williams@example.com",   "phone": "+91 9845678901"},
    {"borrower_name": "Carol Davis",     "email": "carol.davis@example.com",    "phone": "+91 9812345678"},
    {"borrower_name": "David Kumar",     "email": "david.kumar@example.com",    "phone": "+91 9765432109"},
    {"borrower_name": "Eve Patel",       "email": "eve.patel@example.com",      "phone": "+91 9754321098"},
    {"borrower_name": "Frank Thomas",   "email": "frank.thomas@example.com",   "phone": "+91 9743210987"},
]

# (book_index, borrower_index, days_ago_borrowed, days_ago_returned_or_None)
# None = still borrowed
TRANSACTIONS = [
    # Returned transactions (history)
    (0,  0, 45, 30),   # Clean Code — Alice returned
    (1,  1, 40, 25),   # Pragmatic Programmer — Bob returned
    (11, 2, 35, 20),   # Sapiens — Carol returned
    (8,  3, 30, 15),   # Atomic Habits — David returned
    (14, 4, 25, 12),   # 1984 — Eve returned
    (6,  5, 20, 8),    # Cosmos — Frank returned
    (0,  2, 18, 5),    # Clean Code — Carol returned (borrowed again)
    (9,  0, 15, 4),    # Good to Great — Alice returned
    (13, 1, 12, 3),    # To Kill a Mockingbird — Bob returned
    (17, 5, 10, 2),    # Data Science from Scratch — Frank returned

    # Currently borrowed (no return date)
    (2,  0, 7,  None), # Design Patterns — Alice (still out)
    (5,  1, 5,  None), # A Brief History of Time — Bob (still out)
    (10, 2, 4,  None), # Deep Work — Carol (still out)
    (15, 3, 3,  None), # The Alchemist — David (still out)
    (16, 4, 2,  None), # Harry Potter — Eve (still out)
    (18, 5, 1,  None), # Storytelling with Data — Frank (still out)
]


def seed(db: Session) -> None:
    """Insert all seed data. Safe to call only when DB is empty."""
    now = datetime.utcnow()

    # ── Books ─────────────────────────────────────────────────────────────────
    book_objs = []
    for b in BOOKS:
        obj = models.Book(**b, availability_status="available")
        db.add(obj)
        book_objs.append(obj)
    db.flush()  # assign IDs without committing

    # ── Borrowers ─────────────────────────────────────────────────────────────
    borrower_objs = []
    for br in BORROWERS:
        obj = models.Borrower(**br)
        db.add(obj)
        borrower_objs.append(obj)
    db.flush()

    # ── Transactions ──────────────────────────────────────────────────────────
    for book_idx, borrower_idx, days_borrowed, days_returned in TRANSACTIONS:
        borrow_date  = now - timedelta(days=days_borrowed)
        return_date  = (now - timedelta(days=days_returned)) if days_returned is not None else None
        status       = "returned" if return_date else "borrowed"

        txn = models.Transaction(
            book_id     = book_objs[book_idx].book_id,
            borrower_id = borrower_objs[borrower_idx].borrower_id,
            borrow_date = borrow_date,
            return_date = return_date,
            status      = status,
        )
        db.add(txn)

        # Mark currently-borrowed books as unavailable
        if status == "borrowed":
            book_objs[book_idx].availability_status = "borrowed"

    db.commit()
    print("  [seed] Sample data loaded: "
          f"{len(BOOKS)} books, {len(BORROWERS)} borrowers, {len(TRANSACTIONS)} transactions.")
