from pydantic import BaseModel, ConfigDict


class ModelVersionOut(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    id: int
    model_name: str
    version: str
    training_date: str
    features: list
    parameters: dict
    evaluation_metrics: dict
    dataset_version: str
    limitations: list


class FeatureImportanceOut(BaseModel):
    feature: str
    importance: float


class MLProjectionOut(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    available: bool
    predicted_performance_score: float | None = None
    top_features: list[FeatureImportanceOut] = []
    model_version: str | None = None
    note: str
