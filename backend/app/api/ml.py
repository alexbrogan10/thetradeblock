"""Model Versioning (Section 39) read API."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.model_version import ModelVersion
from app.schemas.ml import ModelVersionOut

router = APIRouter(prefix="/api/ml", tags=["ml"])


@router.get("/model-versions", response_model=list[ModelVersionOut])
def list_model_versions(db: Session = Depends(get_db)):
    versions = db.query(ModelVersion).order_by(ModelVersion.model_name).all()
    return [
        {
            "id": v.id,
            "model_name": v.model_name,
            "version": v.version,
            "training_date": v.training_date.isoformat() if hasattr(v.training_date, "isoformat") else str(v.training_date),
            "features": v.features,
            "parameters": v.parameters,
            "evaluation_metrics": v.evaluation_metrics,
            "dataset_version": v.dataset_version,
            "limitations": v.limitations,
        }
        for v in versions
    ]
