"""FastAPI application composition root."""

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.academic_periods.routes import router as academic_periods_router
from app.auth.routes import router as auth_router
from app.core.config import get_settings
from app.core.error_handlers import register_error_handlers
from app.enrollments.routes import router as enrollments_router
from app.grades.routes import router as grades_router
from app.reports.routes import router as reports_router
from app.subjects.routes import router as subjects_router
from app.users.routes import role_router, router as users_router

settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
register_error_handlers(app)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(role_router)
api_router.include_router(subjects_router)
api_router.include_router(academic_periods_router)
api_router.include_router(enrollments_router)
api_router.include_router(grades_router)
api_router.include_router(reports_router)
app.include_router(api_router)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Return process health without exposing internal details."""

    return {"status": "ok"}
