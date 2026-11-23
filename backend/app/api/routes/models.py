from typing import List
from fastapi import APIRouter, status
from app.ml.registry import get_model_registry
from app.schemas.model import ModelMetadataResponse

router = APIRouter(prefix="/models", tags=["Models"])

@router.get("", response_model=List[ModelMetadataResponse])
def list_models():
    registry = get_model_registry()
    return registry.list_models()

@router.get("/{model_id:path}", response_model=ModelMetadataResponse)
def get_model_info(model_id: str):
    registry = get_model_registry()
    model = registry.get_model(model_id)
    return model.get_metadata()

@router.post("/{model_id:path}/unload")
def unload_model(model_id: str):
    registry = get_model_registry()
    registry.unload_model(model_id)
    return {"status": "unloaded", "model_id": model_id}
