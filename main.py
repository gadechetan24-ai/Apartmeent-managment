from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.database import engine, Base
from app.models import models  # noqa – ensures models are registered
from app.routers import users, buildings, apartments, payments, maintenance, dashboard

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Apartment Management System",
    description="Full-stack apartment management with JWT auth",
    version="1.0.0",
)

# ── CORS ──────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routers ───────────────────────────────────────────
app.include_router(users.router)
app.include_router(buildings.router)
app.include_router(apartments.router)
app.include_router(payments.router)
app.include_router(maintenance.router)
app.include_router(dashboard.router)

# ── Static Files & Templates ──────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(BASE_DIR, "static")
templates_dir = os.path.join(BASE_DIR, "templates")

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


from fastapi.responses import FileResponse

@app.get("/")
def serve_login():
    return FileResponse(os.path.join(templates_dir, "login.html"))

@app.get("/register")
def serve_register():
    return FileResponse(os.path.join(templates_dir, "register.html"))

@app.get("/dashboard")
def serve_dashboard():
    return FileResponse(os.path.join(templates_dir, "dashboard.html"))


@app.get("/health")
def health():
    return {"status": "ok", "app": "Apartment Management System"}
