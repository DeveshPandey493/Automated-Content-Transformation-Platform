from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.core.exceptions import AppException
from app.db.session import init_db
from app.api.routes.health import router as health_router
from app.api.routes.documents import router as documents_router
from app.api.routes.models import router as models_router
from app.api.routes.transformations import router as transformations_router
from app.api.routes.verification import router as verification_router
from app.api.routes.evaluations import router as evaluations_router
from app.api.routes.datasets import router as datasets_router
from app.api.routes.exports import router as exports_router
from app.api.routes.versioning import router as versioning_router

logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info(f"Starting {settings.APP_NAME} in '{settings.APP_ENV}' mode...")
    # Initialize database tables
    try:
        init_db()
    except Exception as e:
        logger.error(f"Database initialization error: {e}", exc_info=True)
    yield
    logger.info("Shutting down application...")

def create_application() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        description="SIH 2026: Gen AI Platform for Automated Content Transformation with Factual Verification and Grounded Benchmarking.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom Exception Handlers
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.detail,
                    "extra": exc.extra
                }
            }
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception on {request.method} {request.url}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An internal server error occurred. Please check server logs."
                }
            }
        )

    # Include Routes
    app.include_router(health_router, prefix="/api")
    app.include_router(documents_router, prefix="/api")
    app.include_router(models_router, prefix="/api")
    app.include_router(transformations_router, prefix="/api")
    app.include_router(verification_router, prefix="/api")
    app.include_router(evaluations_router, prefix="/api")
    app.include_router(datasets_router, prefix="/api")
    app.include_router(exports_router, prefix="/api")
    app.include_router(versioning_router, prefix="/api")

    @app.get("/")
    def root():
        return {
            "name": settings.APP_NAME,
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/api/health"
        }

    return app

app = create_application()

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.APP_DEBUG)
