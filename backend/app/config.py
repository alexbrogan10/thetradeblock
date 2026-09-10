"""Application configuration.

Values are read from environment variables (see .env.example at the repo
root). Nothing here should ever hold real credentials.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", protected_namespaces=())

    database_url: str = (
        "postgresql+psycopg2://tradeblock:tradeblock@localhost:5432/tradeblock"
    )
    app_env: str = "development"
    demo_mode: bool = True
    player_valuation_model_version: str = "player-valuation-v1.0"
    draft_pick_model_version: str = "draft-pick-traditional-v1.0"

    # Where trained ML artifacts (Section 38/39) live. Relative default
    # assumes the backend runs from backend/ with the repo checked out
    # normally ("../models" -> <repo root>/models). Docker Compose
    # overrides this to /models with a matching volume mount, since the
    # backend container's build context is backend/ alone.
    model_dir: str = "../models"

    # Player Value Score component weights (Section 10). These are the
    # starting assumptions called out in the product spec and are
    # intentionally configurable rather than hard-coded constants scattered
    # through the analytics code.
    weight_recent_performance: float = 0.20
    weight_projected_performance: float = 0.20
    weight_age: float = 0.15
    weight_position_value: float = 0.10
    weight_contract_efficiency: float = 0.15
    weight_availability: float = 0.05
    weight_positional_scarcity: float = 0.10
    weight_trajectory: float = 0.05


settings = Settings()
