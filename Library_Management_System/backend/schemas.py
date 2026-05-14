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
