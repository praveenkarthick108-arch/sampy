from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Book(Base):
    __tablename__ = "books"

    book_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    isbn = Column(String(20), unique=True, nullable=False)
    availability_status = Column(String(20), default="available")

    transactions = relationship("Transaction", back_populates="book", cascade="all, delete-orphan")


class Borrower(Base):
    __tablename__ = "borrowers"

    borrower_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    borrower_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)

    transactions = relationship("Transaction", back_populates="borrower", cascade="all, delete-orphan")


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey("books.book_id"), nullable=False)
    borrower_id = Column(Integer, ForeignKey("borrowers.borrower_id"), nullable=False)
    borrow_date = Column(DateTime, default=datetime.utcnow)
    return_date = Column(DateTime, nullable=True)
    status = Column(String(20), default="borrowed")

    book = relationship("Book", back_populates="transactions")
    borrower = relationship("Borrower", back_populates="transactions")


# ── Phase 2: ETL Analytics Tables ─────────────────────────────────────────────

class ETLRunLog(Base):
    __tablename__ = "etl_run_log"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    run_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="running")  # running | success | failed
    records_extracted = Column(Integer, nullable=True)
    records_after_transform = Column(Integer, nullable=True)
    books_loaded = Column(Integer, nullable=True)
    popular_books_loaded = Column(Integer, nullable=True)
    category_rows_loaded = Column(Integer, nullable=True)
    monthly_rows_loaded = Column(Integer, nullable=True)
    overdue_rows_loaded = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    duration_seconds = Column(Float, nullable=True)


class AnalyticsPopularBook(Base):
    __tablename__ = "analytics_popular_books"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    book_isbn = Column(String(20))
    book_title = Column(String(255))
    author = Column(String(255))
    category = Column(String(100))
    total_borrows = Column(Integer, default=0)
    distinct_borrowers = Column(Integer, default=0)
    last_borrowed = Column(DateTime, nullable=True)
    etl_run_id = Column(Integer, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)


class AnalyticsCategoryBorrowing(Base):
    __tablename__ = "analytics_category_borrowing"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category = Column(String(100))
    total_borrows = Column(Integer, default=0)
    unique_books = Column(Integer, default=0)
    unique_borrowers = Column(Integer, default=0)
    avg_borrow_days = Column(Float, nullable=True)
    etl_run_id = Column(Integer, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)


class AnalyticsMonthlyTrend(Base):
    __tablename__ = "analytics_monthly_trends"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    year_month = Column(String(7))   # e.g. "2024-03"
    total_borrows = Column(Integer, default=0)
    total_returns = Column(Integer, default=0)
    net_active = Column(Integer, default=0)
    etl_run_id = Column(Integer, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)


class AnalyticsOverdueTransaction(Base):
    __tablename__ = "analytics_overdue_transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    source_txn_id = Column(Integer)
    book_isbn = Column(String(20))
    book_title = Column(String(255))
    borrower_email = Column(String(255))
    borrower_name = Column(String(255))
    borrow_date = Column(DateTime)
    days_overdue = Column(Integer)
    overdue_severity = Column(String(20))  # mild | moderate | severe
    etl_run_id = Column(Integer, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)
