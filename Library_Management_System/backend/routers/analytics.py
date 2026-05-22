from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException

import models
import schemas
from database import get_db

router = APIRouter(prefix="/analytics", tags=["Analytics"])


# ── Popular Books ─────────────────────────────────────────────────────────────

@router.get("/popular-books", response_model=List[schemas.PopularBookItem])
def get_popular_books(limit: int = 20, db=Depends(get_db)):
    rows = (
        db.query(models.AnalyticsPopularBook)
        .order_by(models.AnalyticsPopularBook.total_borrows.desc())
        .limit(limit)
        .all()
    )
    return rows


# ── Category Borrowing Trends ────────────────────────────────────────────────

@router.get("/category-trends", response_model=List[schemas.CategoryBorrowItem])
def get_category_trends(db=Depends(get_db)):
    rows = (
        db.query(models.AnalyticsCategoryBorrowing)
        .order_by(models.AnalyticsCategoryBorrowing.total_borrows.desc())
        .all()
    )
    return rows


# ── Monthly Borrowing Trends ──────────────────────────────────────────────────

@router.get("/monthly-trends", response_model=List[schemas.MonthlyTrendItem])
def get_monthly_trends(months: int = 12, db=Depends(get_db)):
    rows = (
        db.query(models.AnalyticsMonthlyTrend)
        .order_by(models.AnalyticsMonthlyTrend.year_month.asc())
        .all()
    )
    if months and len(rows) > months:
        rows = rows[-months:]
    return rows


# ── Overdue Transactions ──────────────────────────────────────────────────────

@router.get("/overdue", response_model=List[schemas.OverdueItem])
def get_overdue(severity: Optional[str] = None, db=Depends(get_db)):
    query = db.query(models.AnalyticsOverdueTransaction)
    if severity:
        query = query.filter(
            models.AnalyticsOverdueTransaction.overdue_severity == severity.lower()
        )
    rows = query.order_by(
        models.AnalyticsOverdueTransaction.days_overdue.desc()
    ).all()
    return rows


# ── Run ETL Pipeline ──────────────────────────────────────────────────────────

@router.post("/run-etl", response_model=schemas.ETLRunLogResponse)
def run_etl_endpoint(db=Depends(get_db)):
    # Guard: reject if a run is already in progress (started < 5 min ago)
    five_min_ago = datetime.utcnow() - timedelta(minutes=5)
    running = (
        db.query(models.ETLRunLog)
        .filter(
            models.ETLRunLog.status == "running",
            models.ETLRunLog.run_at >= five_min_ago,
        )
        .first()
    )
    if running:
        raise HTTPException(
            status_code=409,
            detail="ETL pipeline is already running. Please wait for it to finish.",
        )

    # Import here to avoid circular imports at module load time
    from etl_pipeline import run_etl
    result = run_etl(db)
    return result


# ── ETL Status ────────────────────────────────────────────────────────────────

@router.get("/etl-status", response_model=schemas.ETLStatusResponse)
def get_etl_status(db=Depends(get_db)):
    total_runs = db.query(models.ETLRunLog).count()
    last_run = (
        db.query(models.ETLRunLog)
        .order_by(models.ETLRunLog.id.desc())
        .first()
    )
    data_loaded = db.query(models.AnalyticsPopularBook).count() > 0
    return schemas.ETLStatusResponse(
        total_runs=total_runs,
        last_run=last_run,
        data_loaded=data_loaded,
    )
