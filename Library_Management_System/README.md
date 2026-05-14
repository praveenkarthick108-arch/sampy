# Library Management System — Phase 1

A full-stack web application for managing library books, borrowers, and transactions.

**Stack:** React 18 (CDN + Babel) · FastAPI · SQLite · SQLAlchemy · Tailwind CSS (CDN)

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
