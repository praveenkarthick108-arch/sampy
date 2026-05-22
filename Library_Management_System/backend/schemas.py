from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


# ── Book ──────────────────────────────────────────────────────────────────────

class BookBase(BaseModel):
    title: str
    author: str
    category: str
    isbn: str


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
    isbn: Optional[str] = None
    availability_status: Optional[str] = None


class Book(BookBase):
    book_id: int
    availability_status: str

    model_config = {"from_attributes": True}


# ── Borrower ──────────────────────────────────────────────────────────────────

class BorrowerBase(BaseModel):
    borrower_name: str
    email: str
    phone: str


class BorrowerCreate(BorrowerBase):
    pass


class BorrowerUpdate(BaseModel):
    borrower_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class Borrower(BorrowerBase):
    borrower_id: int

    model_config = {"from_attributes": True}


# ── Transaction ───────────────────────────────────────────────────────────────

class BorrowRequest(BaseModel):
    book_id: int
    borrower_id: int


class ReturnRequest(BaseModel):
    transaction_id: int


class TransactionResponse(BaseModel):
    transaction_id: int
    book_id: int
    borrower_id: int
    borrow_date: datetime
    return_date: Optional[datetime] = None
    status: str
    book: Optional[Book] = None
    borrower: Optional[Borrower] = None

    model_config = {"from_attributes": True}


# ── Dashboard ─────────────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_books: int
    available_books: int
    borrowed_books: int
    total_borrowers: int
    total_transactions: int
    active_transactions: int
    recent_transactions: List[TransactionResponse]


# ── Phase 2: Analytics Schemas ────────────────────────────────────────────────

class PopularBookItem(BaseModel):
    book_isbn: str
    book_title: str
    author: str
    category: str
    total_borrows: int
    distinct_borrowers: int
    last_borrowed: Optional[datetime] = None

    model_config = {"from_attributes": True}


class CategoryBorrowItem(BaseModel):
    category: str
    total_borrows: int
    unique_books: int
    unique_borrowers: int
    avg_borrow_days: Optional[float] = None

    model_config = {"from_attributes": True}


class MonthlyTrendItem(BaseModel):
    year_month: str
    total_borrows: int
    total_returns: int
    net_active: int

    model_config = {"from_attributes": True}


class OverdueItem(BaseModel):
    source_txn_id: int
    book_isbn: str
    book_title: str
    borrower_email: str
    borrower_name: str
    borrow_date: datetime
    days_overdue: int
    overdue_severity: str

    model_config = {"from_attributes": True}


class ETLRunLogResponse(BaseModel):
    id: int
    run_at: datetime
    status: str
    records_extracted: Optional[int] = None
    records_after_transform: Optional[int] = None
    books_loaded: Optional[int] = None
    popular_books_loaded: Optional[int] = None
    category_rows_loaded: Optional[int] = None
    monthly_rows_loaded: Optional[int] = None
    overdue_rows_loaded: Optional[int] = None
    error_message: Optional[str] = None
    duration_seconds: Optional[float] = None

    model_config = {"from_attributes": True}


class ETLStatusResponse(BaseModel):
    total_runs: int
    last_run: Optional[ETLRunLogResponse] = None
    data_loaded: bool
