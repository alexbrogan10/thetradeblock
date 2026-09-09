from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import settings

app = FastAPI(
    title="The Trade Block API",
    description=(
        "NFL trade and asset-exchange decision-support API. Provides "
        "explainable player valuation, draft-pick valuation, and trade "
        "analysis. This is an independent project and is not affiliated "
        "with the NFL or any NFL team. DEMO DATA is clearly labeled and "
        "is not official NFL data."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/api/health")
def health():
    return {"status": "ok", "demo_mode": settings.demo_mode}
