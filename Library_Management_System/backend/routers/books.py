from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import crud
import schemas
from database import get_db

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("/", response_model=List[schemas.Book])
def list_books(skip: int = 0, limit: int = 200, db: Session = Depends(get_db)):
    return crud.get_books(db, skip=skip, limit=limit)


@router.get("/categories", response_model=List[str])
def list_categories(db: Session = Depends(get_db)):
    return crud.get_categories(db)


@router.get("/{book_id}", response_model=schemas.Book)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = crud.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("/", response_model=schemas.Book, status_code=status.HTTP_201_CREATED)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    if not book.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    if not book.isbn.strip():
        raise HTTPException(status_code=400, detail="ISBN cannot be empty")
    if crud.get_book_by_isbn(db, book.isbn):
        raise HTTPException(status_code=400, detail="A book with this ISBN already exists")
    return crud.create_book(db, book)


@router.put("/{book_id}", response_model=schemas.Book)
def update_book(book_id: int, book: schemas.BookUpdate, db: Session = Depends(get_db)):
    if book.isbn:
        existing = crud.get_book_by_isbn(db, book.isbn)
        if existing and existing.book_id != book_id:
            raise HTTPException(status_code=400, detail="Another book with this ISBN already exists")
    updated = crud.update_book(db, book_id, book)
    if not updated:
        raise HTTPException(status_code=404, detail="Book not found")
    return updated


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    active = crud.get_active_transaction_for_book(db, book_id)
    if active:
        raise HTTPException(status_code=400, detail="Cannot delete a book that is currently borrowed")
    if not crud.delete_book(db, book_id):
        raise HTTPException(status_code=404, detail="Book not found")
