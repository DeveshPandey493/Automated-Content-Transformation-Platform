from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.db.models.dataset import Dataset, DatasetDocument
from app.schemas.dataset import DatasetResponse, DatasetDocumentResponse
from app.services.dataset.service import DatasetService

router = APIRouter(prefix="/datasets", tags=["Datasets"])

@router.get("", response_model=List[DatasetResponse])
def list_datasets(db: Session = Depends(get_db)):
    datasets = db.scalars(select(Dataset)).all()
    if not datasets:
        # Auto-seed benchmark
        seeded = DatasetService.seed_benchmark_dataset(db)
        datasets = [seeded]
    return datasets

@router.post("/seed", response_model=DatasetResponse)
def seed_dataset(db: Session = Depends(get_db)):
    dataset = DatasetService.seed_benchmark_dataset(db)
    return dataset

@router.get("/{dataset_id}", response_model=DatasetResponse)
def get_dataset(dataset_id: str, db: Session = Depends(get_db)):
    dataset = db.get(Dataset, dataset_id)
    if not dataset:
        dataset = DatasetService.seed_benchmark_dataset(db)
    return dataset
