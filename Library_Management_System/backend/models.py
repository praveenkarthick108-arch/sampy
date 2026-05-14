from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
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
