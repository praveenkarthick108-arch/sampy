from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import crud
import schemas
from database import get_db

router = APIRouter(prefix="/borrowers", tags=["Borrowers"])


@router.get("/", response_model=List[schemas.Borrower])
def list_borrowers(skip: int = 0, limit: int = 200, db: Session = Depends(get_db)):
    return crud.get_borrowers(db, skip=skip, limit=limit)


@router.get("/{borrower_id}", response_model=schemas.Borrower)
def get_borrower(borrower_id: int, db: Session = Depends(get_db)):
    b = crud.get_borrower(db, borrower_id)
    if not b:
        raise HTTPException(status_code=404, detail="Borrower not found")
    return b


@router.get("/{borrower_id}/transactions", response_model=List[schemas.TransactionResponse])
def get_borrower_transactions(borrower_id: int, db: Session = Depends(get_db)):
    if not crud.get_borrower(db, borrower_id):
        raise HTTPException(status_code=404, detail="Borrower not found")
    return crud.get_borrower_transactions(db, borrower_id)


@router.post("/", response_model=schemas.Borrower, status_code=status.HTTP_201_CREATED)
def create_borrower(borrower: schemas.BorrowerCreate, db: Session = Depends(get_db)):
    if not borrower.borrower_name.strip():
        raise HTTPException(status_code=400, detail="Name cannot be empty")
    if crud.get_borrower_by_email(db, borrower.email):
        raise HTTPException(status_code=400, detail="A borrower with this email already exists")
    return crud.create_borrower(db, borrower)


@router.put("/{borrower_id}", response_model=schemas.Borrower)
def update_borrower(borrower_id: int, borrower: schemas.BorrowerUpdate, db: Session = Depends(get_db)):
    if borrower.email:
        existing = crud.get_borrower_by_email(db, borrower.email)
        if existing and existing.borrower_id != borrower_id:
            raise HTTPException(status_code=400, detail="Another borrower with this email already exists")
    updated = crud.update_borrower(db, borrower_id, borrower)
    if not updated:
        raise HTTPException(status_code=404, detail="Borrower not found")
    return updated


@router.delete("/{borrower_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_borrower(borrower_id: int, db: Session = Depends(get_db)):
    borrower = crud.get_borrower(db, borrower_id)
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")
    active = any(t.status == "borrowed" for t in borrower.transactions)
    if active:
        raise HTTPException(status_code=400, detail="Cannot delete a borrower who has unreturned books")
    if not crud.delete_borrower(db, borrower_id):
        raise HTTPException(status_code=404, detail="Borrower not found")
