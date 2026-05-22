import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import engine, SessionLocal, get_db
import models
import crud
import schemas
import seed
from routers import books, borrowers, transactions, analytics

models.Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-seed sample data on first run (only when DB is empty)
    db = SessionLocal()
    try:
        if db.query(models.Book).count() == 0:
            print("  [startup] Empty database detected — loading sample data…")
            seed.seed(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="Library Management System API",
    description="REST API for the Library Management System — Phase 2 (ETL & Analytics)",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(books.router)
app.include_router(borrowers.router)
app.include_router(transactions.router)
app.include_router(analytics.router)


# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.get("/dashboard", response_model=schemas.DashboardStats, tags=["Dashboard"])
def dashboard(db=__import__("fastapi").Depends(get_db)):
    return crud.get_dashboard_stats(db)


# ── Serve React frontend (CDN-based, no Node.js required) ────────────────────

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/", include_in_schema=False)
@app.get("/app", include_in_schema=False)
async def serve_frontend():
    index = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.isfile(index):
        return FileResponse(index)
    return {"message": "Library Management System API", "docs": "/docs"}
