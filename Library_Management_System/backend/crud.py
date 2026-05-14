from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
import models
import schemas


# ── Books ─────────────────────────────────────────────────────────────────────

def get_books(db: Session, skip: int = 0, limit: int = 200) -> List[models.Book]:
    return db.query(models.Book).offset(skip).limit(limit).all()


def get_book(db: Session, book_id: int) -> Optional[models.Book]:
    return db.query(models.Book).filter(models.Book.book_id == book_id).first()


def get_book_by_isbn(db: Session, isbn: str) -> Optional[models.Book]:
    return db.query(models.Book).filter(models.Book.isbn == isbn).first()


def create_book(db: Session, book: schemas.BookCreate) -> models.Book:
    db_book = models.Book(**book.model_dump(), availability_status="available")
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def update_book(db: Session, book_id: int, book_update: schemas.BookUpdate) -> Optional[models.Book]:
    db_book = get_book(db, book_id)
    if not db_book:
        return None
    for key, value in book_update.model_dump(exclude_unset=True).items():
        setattr(db_book, key, value)
    db.commit()
    db.refresh(db_book)
    return db_book


def delete_book(db: Session, book_id: int) -> bool:
    db_book = get_book(db, book_id)
    if not db_book:
        return False
    db.delete(db_book)
    db.commit()
    return True


def search_books(db: Session, query: str = "", category: str = "") -> List[models.Book]:
    q = db.query(models.Book)
    if query:
        q = q.filter(
            or_(
                models.Book.title.ilike(f"%{query}%"),
                models.Book.author.ilike(f"%{query}%"),
                models.Book.isbn.ilike(f"%{query}%"),
            )
        )
    if category:
        q = q.filter(models.Book.category.ilike(f"%{category}%"))
    return q.all()


def get_categories(db: Session) -> List[str]:
    rows = db.query(models.Book.category).distinct().all()
    return sorted({r[0] for r in rows if r[0]})


# ── Borrowers ─────────────────────────────────────────────────────────────────

def get_borrowers(db: Session, skip: int = 0, limit: int = 200) -> List[models.Borrower]:
    return db.query(models.Borrower).offset(skip).limit(limit).all()


def get_borrower(db: Session, borrower_id: int) -> Optional[models.Borrower]:
    return db.query(models.Borrower).filter(models.Borrower.borrower_id == borrower_id).first()


def get_borrower_by_email(db: Session, email: str) -> Optional[models.Borrower]:
    return db.query(models.Borrower).filter(models.Borrower.email == email).first()


def create_borrower(db: Session, borrower: schemas.BorrowerCreate) -> models.Borrower:
    db_borrower = models.Borrower(**borrower.model_dump())
    db.add(db_borrower)
    db.commit()
    db.refresh(db_borrower)
    return db_borrower


def update_borrower(db: Session, borrower_id: int, update: schemas.BorrowerUpdate) -> Optional[models.Borrower]:
    db_borrower = get_borrower(db, borrower_id)
    if not db_borrower:
        return None
    for key, value in update.model_dump(exclude_unset=True).items():
        setattr(db_borrower, key, value)
    db.commit()
    db.refresh(db_borrower)
    return db_borrower


def delete_borrower(db: Session, borrower_id: int) -> bool:
    db_borrower = get_borrower(db, borrower_id)
    if not db_borrower:
        return False
    db.delete(db_borrower)
    db.commit()
    return True


# ── Transactions ──────────────────────────────────────────────────────────────

def get_active_transaction_for_book(db: Session, book_id: int) -> Optional[models.Transaction]:
    return db.query(models.Transaction).filter(
        models.Transaction.book_id == book_id,
        models.Transaction.status == "borrowed",
    ).first()


def borrow_book(db: Session, book_id: int, borrower_id: int) -> models.Transaction:
    book = get_book(db, book_id)
    book.availability_status = "borrowed"
    txn = models.Transaction(
        book_id=book_id,
        borrower_id=borrower_id,
        borrow_date=datetime.utcnow(),
        status="borrowed",
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn


def return_book(db: Session, transaction_id: int) -> Optional[models.Transaction]:
    txn = db.query(models.Transaction).filter(
        models.Transaction.transaction_id == transaction_id,
        models.Transaction.status == "borrowed",
    ).first()
    if not txn:
        return None
    txn.return_date = datetime.utcnow()
    txn.status = "returned"
    book = get_book(db, txn.book_id)
    if book:
        book.availability_status = "available"
    db.commit()
    db.refresh(txn)
    return txn


def get_transactions(db: Session, skip: int = 0, limit: int = 200) -> List[models.Transaction]:
    return (
        db.query(models.Transaction)
        .order_by(models.Transaction.borrow_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_borrower_transactions(db: Session, borrower_id: int) -> List[models.Transaction]:
    return (
        db.query(models.Transaction)
        .filter(models.Transaction.borrower_id == borrower_id)
        .order_by(models.Transaction.borrow_date.desc())
        .all()
    )


# ── Dashboard ─────────────────────────────────────────────────────────────────

def get_dashboard_stats(db: Session) -> dict:
    total_books = db.query(func.count(models.Book.book_id)).scalar() or 0
    available_books = (
        db.query(func.count(models.Book.book_id))
        .filter(models.Book.availability_status == "available")
        .scalar() or 0
    )
    borrowed_books = (
        db.query(func.count(models.Book.book_id))
        .filter(models.Book.availability_status == "borrowed")
        .scalar() or 0
    )
    total_borrowers = db.query(func.count(models.Borrower.borrower_id)).scalar() or 0
    total_transactions = db.query(func.count(models.Transaction.transaction_id)).scalar() or 0
    active_transactions = (
        db.query(func.count(models.Transaction.transaction_id))
        .filter(models.Transaction.status == "borrowed")
        .scalar() or 0
    )
    recent_transactions = (
        db.query(models.Transaction)
        .order_by(models.Transaction.borrow_date.desc())
        .limit(5)
        .all()
    )
    return {
        "total_books": total_books,
        "available_books": available_books,
        "borrowed_books": borrowed_books,
        "total_borrowers": total_borrowers,
        "total_transactions": total_transactions,
        "active_transactions": active_transactions,
        "recent_transactions": recent_transactions,
    }
