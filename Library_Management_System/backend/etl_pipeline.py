"""
ETL Pipeline — Library Management System Phase 2
Extract → Transform → Load using Pandas

Run standalone : python backend/etl_pipeline.py
Run via API    : POST /analytics/run-etl
"""

import os
import sys
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Allow standalone execution from any directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from sqlalchemy.orm import Session

import models
from database import SessionLocal, engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [ETL] %(message)s")
log = logging.getLogger(__name__)

DATASETS_DIR = Path(__file__).parent.parent / "datasets"
OVERDUE_DAYS = 14  # library borrow period policy


# ─────────────────────────────────────────────────────────────────────────────
# EXTRACT
# ─────────────────────────────────────────────────────────────────────────────

def extract() -> dict:
    """Read raw CSVs from datasets/ folder. Returns dict of DataFrames."""
    files = {
        "books":        DATASETS_DIR / "books_catalog.csv",
        "borrowers":    DATASETS_DIR / "borrowers_list.csv",
        "transactions": DATASETS_DIR / "transactions_history.csv",
    }
    for key, path in files.items():
        if not path.exists():
            raise FileNotFoundError(
                f"Dataset not found: {path}\n"
                f"Expected datasets/ folder at: {DATASETS_DIR}"
            )

    raw = {}
    for key, path in files.items():
        df = pd.read_csv(path, dtype=str)
        log.info(f"Extracted {key}: {len(df)} rows from {path.name}")
        raw[key] = df

    return raw


# ─────────────────────────────────────────────────────────────────────────────
# TRANSFORM
# ─────────────────────────────────────────────────────────────────────────────

def transform(raw: dict) -> dict:
    """Clean data and compute 4 analytics DataFrames."""
    today = datetime.utcnow().date()

    # ── Books ─────────────────────────────────────────────────────────────────
    books = raw["books"].copy()
    books["isbn"] = books["isbn"].str.strip()
    books["title"] = books["title"].str.strip()
    books["author"] = books["author"].str.strip()
    books["category"] = books["category"].str.strip()
    before = len(books)
    books = books.dropna(subset=["isbn", "title"])
    books = books.drop_duplicates(subset=["isbn"], keep="first")
    log.info(f"Books: {before} → {len(books)} after cleaning")

    # ── Borrowers ─────────────────────────────────────────────────────────────
    borrowers = raw["borrowers"].copy()
    for col in ["borrower_name", "email", "phone"]:
        if col in borrowers.columns:
            borrowers[col] = borrowers[col].str.strip()
    before = len(borrowers)
    borrowers = borrowers.dropna(subset=["email"])
    borrowers = borrowers.drop_duplicates(subset=["email"], keep="first")
    log.info(f"Borrowers: {before} → {len(borrowers)} after cleaning")

    # ── Transactions ──────────────────────────────────────────────────────────
    txn = raw["transactions"].copy()

    # Drop rows where both isbn and borrower_email are null
    txn = txn.dropna(subset=["isbn", "borrower_email"], how="all")

    # Fill missing status
    txn["return_date"] = txn["return_date"].replace("", None)
    txn["status"] = txn.apply(
        lambda r: "returned" if pd.notna(r.get("return_date")) else "borrowed",
        axis=1
    )

    # Parse dates
    txn["borrow_date"] = pd.to_datetime(txn["borrow_date"], errors="coerce")
    txn["return_date"] = pd.to_datetime(txn["return_date"], errors="coerce")

    # Drop rows with unparseable borrow_date
    before = len(txn)
    txn = txn.dropna(subset=["borrow_date"])

    # Dedup on transaction_id, keep last
    if "transaction_id" in txn.columns:
        txn["transaction_id"] = pd.to_numeric(txn["transaction_id"], errors="coerce")
        txn = txn.drop_duplicates(subset=["transaction_id"], keep="last")

    log.info(f"Transactions: {before} → {len(txn)} after cleaning")

    # ── Analytics: Popular Books ───────────────────────────────────────────────
    pop = (
        txn.groupby("isbn")
        .agg(
            total_borrows=("isbn", "count"),
            distinct_borrowers=("borrower_email", "nunique"),
            last_borrowed=("borrow_date", "max"),
        )
        .reset_index()
    )
    pop = pop.merge(
        books[["isbn", "title", "author", "category"]],
        on="isbn",
        how="left",
    )
    pop = pop.rename(columns={"isbn": "book_isbn", "title": "book_title"})
    pop = pop.sort_values("total_borrows", ascending=False)
    log.info(f"Popular books computed: {len(pop)} rows")

    # ── Analytics: Category Borrowing ─────────────────────────────────────────
    txn_with_cat = txn.merge(books[["isbn", "category"]], on="isbn", how="left")
    txn_with_cat["category"] = txn_with_cat["category"].fillna("Unknown")

    cat = (
        txn_with_cat.groupby("category")
        .agg(
            total_borrows=("isbn", "count"),
            unique_books=("isbn", "nunique"),
            unique_borrowers=("borrower_email", "nunique"),
        )
        .reset_index()
    )

    # Average borrow days for returned books
    returned = txn_with_cat[txn_with_cat["status"] == "returned"].copy()
    returned["borrow_days"] = (
        returned["return_date"] - returned["borrow_date"]
    ).dt.days
    returned = returned[returned["borrow_days"] >= 0]
    avg_days = returned.groupby("category")["borrow_days"].mean().reset_index()
    avg_days.columns = ["category", "avg_borrow_days"]

    cat = cat.merge(avg_days, on="category", how="left")
    cat = cat.sort_values("total_borrows", ascending=False)
    log.info(f"Category borrowing computed: {len(cat)} rows")

    # ── Analytics: Monthly Trends ─────────────────────────────────────────────
    txn["borrow_month"] = txn["borrow_date"].dt.strftime("%Y-%m")
    borrows_by_month = (
        txn.groupby("borrow_month")
        .size()
        .reset_index(name="total_borrows")
        .rename(columns={"borrow_month": "year_month"})
    )

    returned_txn = txn[txn["return_date"].notna()].copy()
    returned_txn["return_month"] = returned_txn["return_date"].dt.strftime("%Y-%m")
    returns_by_month = (
        returned_txn.groupby("return_month")
        .size()
        .reset_index(name="total_returns")
        .rename(columns={"return_month": "year_month"})
    )

    monthly = borrows_by_month.merge(returns_by_month, on="year_month", how="outer")
    monthly["total_borrows"] = monthly["total_borrows"].fillna(0).astype(int)
    monthly["total_returns"] = monthly["total_returns"].fillna(0).astype(int)
    monthly["net_active"] = monthly["total_borrows"] - monthly["total_returns"]
    monthly = monthly.sort_values("year_month")
    log.info(f"Monthly trends computed: {len(monthly)} rows")

    # ── Analytics: Overdue Transactions ───────────────────────────────────────
    active_txn = txn[
        (txn["status"] == "borrowed") & txn["return_date"].isna()
    ].copy()
    active_txn["days_held"] = (
        pd.Timestamp(today) - active_txn["borrow_date"]
    ).dt.days
    overdue = active_txn[active_txn["days_held"] > OVERDUE_DAYS].copy()
    overdue["days_overdue"] = overdue["days_held"] - OVERDUE_DAYS

    def severity(d):
        if d <= 7:
            return "mild"
        elif d <= 21:
            return "moderate"
        return "severe"

    overdue["overdue_severity"] = overdue["days_overdue"].apply(severity)

    # Join books and borrowers for display names
    overdue = overdue.merge(
        books[["isbn", "title", "author"]],
        on="isbn",
        how="left",
    )
    overdue = overdue.merge(
        borrowers[["email", "borrower_name"]],
        left_on="borrower_email",
        right_on="email",
        how="left",
    )
    overdue = overdue.rename(columns={"isbn": "book_isbn", "title": "book_title"})
    overdue["book_title"] = overdue["book_title"].fillna("Unknown")
    overdue["borrower_name"] = overdue["borrower_name"].fillna(overdue["borrower_email"])
    overdue = overdue.sort_values("days_overdue", ascending=False)
    log.info(f"Overdue transactions computed: {len(overdue)} rows")

    return {
        "transactions": txn,
        "books": books,
        "borrowers": borrowers,
        "popular_books": pop,
        "category_borrowing": cat,
        "monthly_trends": monthly,
        "overdue": overdue,
    }


# ─────────────────────────────────────────────────────────────────────────────
# LOAD
# ─────────────────────────────────────────────────────────────────────────────

def load(transformed: dict, db: Session, run_id: int) -> dict:
    """Seed main tables and reload all 4 analytics tables."""
    now = datetime.utcnow()
    counts = {}

    # ── Seed main tables (query-first to avoid duplicates) ────────────────────
    books_df = transformed["books"]
    books_added = 0
    for _, row in books_df.iterrows():
        existing = db.query(models.Book).filter_by(isbn=row["isbn"]).first()
        if not existing:
            db.add(models.Book(
                title=row.get("title", ""),
                author=row.get("author", ""),
                category=row.get("category", ""),
                isbn=row["isbn"],
                availability_status="available",
            ))
            books_added += 1
    counts["books"] = books_added

    borrowers_df = transformed["borrowers"]
    borrowers_added = 0
    for _, row in borrowers_df.iterrows():
        existing = db.query(models.Borrower).filter_by(email=row["email"]).first()
        if not existing:
            db.add(models.Borrower(
                borrower_name=row.get("borrower_name", ""),
                email=row["email"],
                phone=row.get("phone", ""),
            ))
            borrowers_added += 1
    counts["borrowers"] = borrowers_added

    db.flush()  # ensure books/borrowers are written before analytics

    # ── Reload analytics tables (truncate + bulk insert in one transaction) ───
    for model in [
        models.AnalyticsPopularBook,
        models.AnalyticsCategoryBorrowing,
        models.AnalyticsMonthlyTrend,
        models.AnalyticsOverdueTransaction,
    ]:
        db.query(model).delete()

    # Popular books
    pop_records = []
    for _, row in transformed["popular_books"].iterrows():
        pop_records.append({
            "book_isbn":          str(row.get("book_isbn", "")),
            "book_title":         str(row.get("book_title", "Unknown")),
            "author":             str(row.get("author", "")),
            "category":           str(row.get("category", "")),
            "total_borrows":      int(row.get("total_borrows", 0)),
            "distinct_borrowers": int(row.get("distinct_borrowers", 0)),
            "last_borrowed":      row["last_borrowed"] if pd.notna(row.get("last_borrowed")) else None,
            "etl_run_id":         run_id,
            "updated_at":         now,
        })
    db.bulk_insert_mappings(models.AnalyticsPopularBook, pop_records)
    counts["popular_books"] = len(pop_records)

    # Category borrowing
    cat_records = []
    for _, row in transformed["category_borrowing"].iterrows():
        avg = row.get("avg_borrow_days")
        cat_records.append({
            "category":         str(row.get("category", "")),
            "total_borrows":    int(row.get("total_borrows", 0)),
            "unique_books":     int(row.get("unique_books", 0)),
            "unique_borrowers": int(row.get("unique_borrowers", 0)),
            "avg_borrow_days":  float(avg) if pd.notna(avg) else None,
            "etl_run_id":       run_id,
            "updated_at":       now,
        })
    db.bulk_insert_mappings(models.AnalyticsCategoryBorrowing, cat_records)
    counts["category"] = len(cat_records)

    # Monthly trends
    month_records = []
    for _, row in transformed["monthly_trends"].iterrows():
        month_records.append({
            "year_month":    str(row.get("year_month", "")),
            "total_borrows": int(row.get("total_borrows", 0)),
            "total_returns": int(row.get("total_returns", 0)),
            "net_active":    int(row.get("net_active", 0)),
            "etl_run_id":    run_id,
            "updated_at":    now,
        })
    db.bulk_insert_mappings(models.AnalyticsMonthlyTrend, month_records)
    counts["monthly"] = len(month_records)

    # Overdue
    overdue_records = []
    for idx, row in transformed["overdue"].iterrows():
        src_id = row.get("transaction_id")
        overdue_records.append({
            "source_txn_id":   int(src_id) if pd.notna(src_id) else idx,
            "book_isbn":       str(row.get("book_isbn", "")),
            "book_title":      str(row.get("book_title", "Unknown")),
            "borrower_email":  str(row.get("borrower_email", "")),
            "borrower_name":   str(row.get("borrower_name", "")),
            "borrow_date":     row["borrow_date"],
            "days_overdue":    int(row.get("days_overdue", 0)),
            "overdue_severity": str(row.get("overdue_severity", "mild")),
            "etl_run_id":      run_id,
            "updated_at":      now,
        })
    db.bulk_insert_mappings(models.AnalyticsOverdueTransaction, overdue_records)
    counts["overdue"] = len(overdue_records)

    db.commit()
    log.info(f"Loaded: books={counts['books']}, borrowers={counts['borrowers']}, "
             f"popular={counts['popular_books']}, categories={counts['category']}, "
             f"monthly={counts['monthly']}, overdue={counts['overdue']}")
    return counts


# ─────────────────────────────────────────────────────────────────────────────
# ORCHESTRATOR
# ─────────────────────────────────────────────────────────────────────────────

def run_etl(db: Session) -> models.ETLRunLog:
    """Full ETL run. Creates a log entry, runs Extract → Transform → Load."""
    # Ensure tables exist (safe to call multiple times)
    models.Base.metadata.create_all(bind=engine)

    run_log = models.ETLRunLog(status="running", run_at=datetime.utcnow())
    db.add(run_log)
    db.commit()
    db.refresh(run_log)

    start = time.time()
    try:
        raw = extract()
        total_extracted = sum(len(df) for df in raw.values())
        run_log.records_extracted = total_extracted

        transformed = transform(raw)
        run_log.records_after_transform = len(transformed["transactions"])

        counts = load(transformed, db, run_log.id)

        run_log.status = "success"
        run_log.books_loaded = counts.get("books", 0)
        run_log.popular_books_loaded = counts.get("popular_books", 0)
        run_log.category_rows_loaded = counts.get("category", 0)
        run_log.monthly_rows_loaded = counts.get("monthly", 0)
        run_log.overdue_rows_loaded = counts.get("overdue", 0)
        run_log.duration_seconds = round(time.time() - start, 3)
        db.commit()
        db.refresh(run_log)
        log.info(f"ETL run #{run_log.id} completed in {run_log.duration_seconds}s")

    except Exception as exc:
        run_log.status = "failed"
        run_log.error_message = str(exc)
        run_log.duration_seconds = round(time.time() - start, 3)
        try:
            db.commit()
        except Exception:
            db.rollback()
        log.error(f"ETL run #{run_log.id} FAILED: {exc}")
        raise

    return run_log


# ─────────────────────────────────────────────────────────────────────────────
# STANDALONE ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  Library Management System — ETL Pipeline")
    print("=" * 60)
    db = SessionLocal()
    try:
        result = run_etl(db)
        print(f"\n  ETL Run #{result.id} — {result.status.upper()}")
        print(f"  Duration          : {result.duration_seconds}s")
        print(f"  Records extracted : {result.records_extracted}")
        print(f"  After transform   : {result.records_after_transform}")
        print(f"  Books seeded      : {result.books_loaded}")
        print(f"  Popular books     : {result.popular_books_loaded}")
        print(f"  Category rows     : {result.category_rows_loaded}")
        print(f"  Monthly rows      : {result.monthly_rows_loaded}")
        print(f"  Overdue rows      : {result.overdue_rows_loaded}")
        if result.error_message:
            print(f"  Error             : {result.error_message}")
        print("=" * 60)
    finally:
        db.close()
