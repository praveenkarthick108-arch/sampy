# Library Management System

A full-stack web application for managing library books, borrowers, and transactions — with ETL-powered analytics.

**Stack:** React 18 (CDN + Babel) · FastAPI · SQLite · SQLAlchemy · Pandas · Tailwind CSS (CDN)

> **No Node.js required.** React is loaded via CDN and JSX is transpiled in the browser by Babel Standalone. FastAPI serves both the API and the frontend.

---

## Quick Start

```
python run.py
```

Then open **http://localhost:8000** in your browser.

That's it. The script automatically activates the virtual environment and starts the server.

> First run installs all Python dependencies automatically.

---

## Prerequisites

- Python 3.9+ (already installed)
- Internet connection (to load React, Tailwind, Recharts from CDN on first visit)

---

## How It Works

```
Browser  ──▶  http://localhost:8000         ← React SPA (index.html)
Browser  ──▶  http://localhost:8000/static/app.js  ← React app (JSX, Babel transpiles it live)
Browser  ──▶  http://localhost:8000/books/  ← FastAPI REST API
```

- FastAPI serves `frontend/index.html` at `/`
- FastAPI mounts `frontend/` as static files at `/static`
- `index.html` loads React 18, Babel, Tailwind, Recharts and Axios from CDN
- `app.js` contains the full React SPA (JSX transpiled by Babel in the browser)
- API calls go to the same server (no CORS issues, no proxy needed)

---

## Features

| Page | Features |
|------|---------|
| Dashboard | Stats cards, bar chart, pie chart, recent transactions |
| Books | Add · Edit · Delete · Live search · Filter by status |
| Borrowers | Add · Edit · Delete · Borrowing history per borrower |
| Transactions | Borrow · Return · Filter by status (all/borrowed/returned) |
| Search | Real-time debounced search by title/author/ISBN + category filter |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/books/` | List all books |
| POST | `/books/` | Add book |
| PUT | `/books/{id}` | Update book |
| DELETE | `/books/{id}` | Delete book |
| GET | `/books/categories` | List distinct categories |
| GET | `/borrowers/` | List all borrowers |
| POST | `/borrowers/` | Add borrower |
| PUT | `/borrowers/{id}` | Update borrower |
| DELETE | `/borrowers/{id}` | Delete borrower |
| GET | `/borrowers/{id}/transactions` | Borrower history |
| GET | `/transactions` | All transactions |
| POST | `/borrow` | Borrow a book |
| POST | `/return` | Return a book |
| GET | `/search?q=&category=` | Search books |
| GET | `/dashboard` | Dashboard stats |
| GET | `/docs` | Interactive API docs (Swagger UI) |

---

## Project Structure

```
Library_Management_System/
├── run.py                    ← Single command to start everything
├── backend/
│   ├── main.py               ← FastAPI app + serves frontend
│   ├── database.py           ← SQLite engine (library.db)
│   ├── models.py             ← SQLAlchemy ORM models
│   ├── schemas.py            ← Pydantic schemas
│   ├── crud.py               ← All database operations
│   ├── routers/
│   │   ├── books.py
│   │   ├── borrowers.py
│   │   └── transactions.py
│   └── requirements.txt
└── frontend/
    ├── index.html            ← Loads React + CDN dependencies
    └── app.js                ← Full React SPA (JSX, no build step)
```

---

## Database Schema

**books** — `book_id` · `title` · `author` · `category` · `isbn` · `availability_status`

**borrowers** — `borrower_id` · `borrower_name` · `email` · `phone`

**transactions** — `transaction_id` · `book_id` · `borrower_id` · `borrow_date` · `return_date` · `status`

---

---

# Phase 2 — ETL Pipeline & Analytics

Phase 2 extends the Library Management System with a full ETL pipeline using Python and Pandas. It introduces analytics-ready database tables, a new Analytics dashboard page, and 6 new API endpoints.

**Added to stack:** Pandas · ETL Pipeline · Analytics Tables

---

## What's New in Phase 2

| Area | What Changed |
|---|---|
| Datasets | 3 CSV files in `datasets/` (60 books, 25 borrowers, 180 transactions) |
| ETL Pipeline | `backend/etl_pipeline.py` — Extract → Transform → Load with Pandas |
| Analytics Tables | 4 new SQLite tables for analytics + ETL run log |
| Analytics API | 6 new endpoints under `/analytics/` |
| Frontend | New **Analytics** page with 4 chart tabs + ETL control panel |
| README | Phase-by-phase documentation (this section) |

---

## Dataset Structure (`datasets/` folder)

| File | Rows | Description |
|---|---|---|
| `books_catalog.csv` | 60 | Full book catalog (isbn, title, author, category, publisher, year_published) |
| `borrowers_list.csv` | 25 | Borrower records (borrower_name, email, phone, membership_date) |
| `transactions_history.csv` | 180 | Historical borrow/return events spanning Jan 2024 – May 2026 |

The transactions dataset includes 150 returned records and 30 currently-borrowed records (including 20+ overdue books), enabling all four analytics features.

---

## ETL Workflow

The ETL pipeline implements three clearly separated stages:

```
datasets/*.csv
      │
      ▼
┌─────────────┐
│   EXTRACT   │  pd.read_csv() — reads all 3 CSV files, logs row counts
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  TRANSFORM  │  Pandas cleaning:
│             │    • Drop nulls on key fields (isbn, email, borrow_date)
│             │    • Deduplicate (isbn, email, transaction_id)
│             │    • Parse + coerce dates
│             │    • Fill missing status from return_date presence
│             │  Analytics computation:
│             │    • popular_books   — groupby isbn, count borrows
│             │    • category_stats  — join books, groupby category
│             │    • monthly_trends  — extract year-month, pivot borrows vs returns
│             │    • overdue         — filter status=borrowed, age > 14 days
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    LOAD     │  SQLAlchemy:
│             │    • Seed main tables (books, borrowers) — query-first, no duplicates
│             │    • Reload analytics tables — delete-all + bulk_insert in one txn
│             │    • Log run in etl_run_log (status, counts, duration)
└─────────────┘
```

**Overdue policy:** A transaction is overdue when `status = borrowed` and `(today − borrow_date) > 14 days`.

| Severity | Days Past Due |
|---|---|
| Mild | 1–7 days |
| Moderate | 8–21 days |
| Severe | > 21 days |

---

## Running the ETL Pipeline

**Option 1 — Via the UI (recommended):**

1. Start the server: `python run.py`
2. Open `http://localhost:8000` → click **Analytics** in the sidebar
3. Click **Run ETL Pipeline** — the button shows a spinner while running
4. All 4 chart tabs auto-refresh when complete

**Option 2 — Standalone script:**

```
python backend/etl_pipeline.py
```

Output example:
```
============================================================
  Library Management System — ETL Pipeline
============================================================

  ETL Run #1 — SUCCESS
  Duration          : 1.24s
  Records extracted : 265
  After transform   : 261
  Books seeded      : 40
  Popular books     : 60
  Category rows     : 10
  Monthly rows      : 18
  Overdue rows      : 23
============================================================
```

---

## Analytics Features

The **Analytics** page has 4 tabs:

| Tab | Chart Type | What It Shows |
|---|---|---|
| Popular Books | Horizontal bar chart + table | Top 20 most borrowed books, distinct borrower count, last borrowed date |
| Categories | Pie chart + table | Borrows per category, unique books/borrowers, avg borrow duration |
| Monthly Trends | Dual-line chart | Borrows vs returns per month (up to 18 months) |
| Overdue | Filterable table | Books overdue > 14 days with severity badges (Mild / Moderate / Severe) |

---

## New API Endpoints (Phase 2)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/analytics/popular-books?limit=20` | Most borrowed books |
| GET | `/analytics/category-trends` | Category-wise borrowing stats |
| GET | `/analytics/monthly-trends?months=12` | Monthly borrowing trends |
| GET | `/analytics/overdue?severity=moderate` | Overdue transaction analysis |
| POST | `/analytics/run-etl` | Trigger ETL pipeline |
| GET | `/analytics/etl-status` | Last ETL run info + data_loaded flag |

All GET endpoints return `[]` when no ETL data has been loaded yet (never 404).

---

## Updated Project Structure

```
Library_Management_System/
├── run.py
├── datasets/                          ← NEW (Phase 2)
│   ├── books_catalog.csv              ← 60 books across 10 categories
│   ├── borrowers_list.csv             ← 25 borrowers
│   └── transactions_history.csv       ← 180 borrow/return records
├── backend/
│   ├── main.py                        ← Updated: analytics router registered
│   ├── database.py
│   ├── models.py                      ← Updated: 5 new analytics models
│   ├── schemas.py                     ← Updated: 6 new Pydantic schemas
│   ├── crud.py
│   ├── etl_pipeline.py                ← NEW: Extract → Transform → Load
│   ├── seed.py
│   ├── requirements.txt               ← Updated: added pandas
│   └── routers/
│       ├── books.py
│       ├── borrowers.py
│       ├── transactions.py
│       └── analytics.py               ← NEW: 6 analytics endpoints
└── frontend/
    ├── index.html
    └── app.js                         ← Updated: Analytics page + charts
```

---

## Analytics Database Schema (Phase 2)

**etl_run_log** — `id` · `run_at` · `status` · `records_extracted` · `records_after_transform` · `books_loaded` · `popular_books_loaded` · `category_rows_loaded` · `monthly_rows_loaded` · `overdue_rows_loaded` · `error_message` · `duration_seconds`

**analytics_popular_books** — `id` · `book_isbn` · `book_title` · `author` · `category` · `total_borrows` · `distinct_borrowers` · `last_borrowed` · `etl_run_id` · `updated_at`

**analytics_category_borrowing** — `id` · `category` · `total_borrows` · `unique_books` · `unique_borrowers` · `avg_borrow_days` · `etl_run_id` · `updated_at`

**analytics_monthly_trends** — `id` · `year_month` · `total_borrows` · `total_returns` · `net_active` · `etl_run_id` · `updated_at`

**analytics_overdue_transactions** — `id` · `source_txn_id` · `book_isbn` · `book_title` · `borrower_email` · `borrower_name` · `borrow_date` · `days_overdue` · `overdue_severity` · `etl_run_id` · `updated_at`
