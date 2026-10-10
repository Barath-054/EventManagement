import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.config import settings
from backend.database import engine, Base, SessionLocal
from backend.seed_data import seed_database
from backend.routers import (
    auth_router, categories_router, services_router,
    packages_router, events_router, recommendations_router,
    quotations_router, payments_router, bookings_router,
    admin_router, reviews_router, meta_router
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables and seed sample Coimbatore data
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Smart AI-powered event planning and budget management platform customized for Coimbatore, Tamil Nadu, India.",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API Routers
app.include_router(auth_router.router)
app.include_router(categories_router.router)
app.include_router(services_router.router)
app.include_router(packages_router.router)
app.include_router(events_router.router)
app.include_router(recommendations_router.router)
app.include_router(quotations_router.router)
app.include_router(payments_router.router)
app.include_router(bookings_router.router)
app.include_router(admin_router.router)
app.include_router(reviews_router.router)
app.include_router(meta_router.router)

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "app": settings.PROJECT_NAME,
        "location": f"{settings.CITY}, {settings.STATE}, {settings.COUNTRY}",
        "version": settings.VERSION
    }

# Mount static frontend files
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(frontend_dir, "index.html"))
