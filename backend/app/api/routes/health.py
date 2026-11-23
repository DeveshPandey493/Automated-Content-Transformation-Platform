import torch
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db, get_active_engine_name
from app.core.config import get_settings

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    settings = get_settings()
    engine_name = get_active_engine_name()
    
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    gpu_available = torch.cuda.is_available()
    gpu_name = torch.cuda.get_device_name(0) if gpu_available else None
    gpu_vram_gb = round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2) if gpu_available else 0.0

    return {
        "status": "ok",
        "app_name": settings.APP_NAME,
        "app_env": settings.APP_ENV,
        "database": db_status,
        "database_engine": engine_name,
        "gpu": {
            "available": gpu_available,
            "device_name": gpu_name,
            "total_vram_gb": gpu_vram_gb
        },
        "groq_configured": bool(settings.GROQ_API_KEY)
    }
