from fastapi import APIRouter

from app.api import dashboard, draft_picks, players, team, teams, trades

api_router = APIRouter()
api_router.include_router(teams.router)
api_router.include_router(players.router)
api_router.include_router(draft_picks.router)
api_router.include_router(trades.router)
api_router.include_router(dashboard.router)
api_router.include_router(team.router)
