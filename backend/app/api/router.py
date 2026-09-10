from fastapi import APIRouter

from app.api import dashboard, draft_picks, finder, players, scenarios, team, teams, trades

api_router = APIRouter()
api_router.include_router(teams.router)
api_router.include_router(players.router)
api_router.include_router(draft_picks.router)
api_router.include_router(trades.router)
api_router.include_router(dashboard.router)
api_router.include_router(team.router)
api_router.include_router(scenarios.router)
api_router.include_router(finder.router)
