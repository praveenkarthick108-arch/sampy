from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import crud
import schemas
from database import get_db

router = APIRouter(tags=["Transactions"])


@router.get("/transactions", response_model=List[schemas.TransactionResponse])
def list_transactions(skip: int = 0, limit: int = 200, db: Session = Depends(get_db)):
    return crud.get_transactions(db, skip=skip, limit=limit)


@router.post("/borrow", response_model=schemas.TransactionResponse, status_code=status.HTTP_201_CREATED)
def borrow_book(req: schemas.BorrowRequest, db: Session = Depends(get_db)):
    book = crud.get_book(db, req.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.availability_status != "available":
        raise HTTPException(status_code=400, detail="Book is not available for borrowing")
    borrower = crud.get_borrower(db, req.borrower_id)
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")
    return crud.borrow_book(db, req.book_id, req.borrower_id)


@router.post("/return", response_model=schemas.TransactionResponse)
def return_book(req: schemas.ReturnRequest, db: Session = Depends(get_db)):
    txn = crud.return_book(db, req.transaction_id)
    if not txn:
        raise HTTPException(
            status_code=400,
            detail="Transaction not found or book already returned",
        )
    return txn


@router.get("/search", response_model=List[schemas.Book])
def search_books(q: str = "", category: str = "", db: Session = Depends(get_db)):
    return crud.search_books(db, query=q, category=category)
