from sqlalchemy import DateTime, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ModelVersion(Base):
    """Section 39 - Model Versioning.

    A record of a specific trained/configured model version so that a
    trade scenario computed with it remains auditable even after the
    model changes (Section 40).
    """

    __tablename__ = "model_versions"

    id: Mapped[int] = mapped_column(primary_key=True)
    model_name: Mapped[str] = mapped_column(String(64), nullable=False)
    version: Mapped[str] = mapped_column(String(32), nullable=False)
    training_date: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    features: Mapped[list] = mapped_column(JSON, default=list)
    parameters: Mapped[dict] = mapped_column(JSON, default=dict)
    evaluation_metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    dataset_version: Mapped[str] = mapped_column(String(64), default="")
    limitations: Mapped[list] = mapped_column(JSON, default=list)
