from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import sys

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).parent
sys.path.append(str(BACKEND_DIR))

from database.database import init_db
from routers.inspections import router as inspections_router

app = FastAPI(
    title="Legal Metrology (Packaged Commodities) Compliance Checking Platform",
    description="Automated compliance assessment system under Legal Metrology (Packaged Commodities) Rules, 2011 - DoCA, Ministry of Consumer Affairs",
    version="2.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database tables
@app.on_event("startup")
def startup_event():
    init_db()

# Mount Static Directories
UPLOAD_DIR = BACKEND_DIR / "uploads"
REPORT_DIR = BACKEND_DIR / "reports"
FRONTEND_DIR = BACKEND_DIR.parent / "frontend"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)
FRONTEND_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
app.mount("/reports", StaticFiles(directory=str(REPORT_DIR)), name="reports")

# Register Routers
app.include_router(inspections_router)

# Serve Web Application Frontend
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")