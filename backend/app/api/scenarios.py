"""Trade Simulator persistence + Scenario Comparison (Sections 26-27)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.analytics.trade_engine import TradeValidationError, analyze_trade
from app.config import settings
from app.database.session import get_db
from app.models.team import Team
from app.models.trade_scenario import ScenarioAsset, TradeScenario
from app.schemas.scenario import (
    ScenarioCompareRequest,
    ScenarioComparisonRowOut,
    ScenarioDetailOut,
    ScenarioSaveRequest,
    ScenarioSummaryOut,
)

router = APIRouter(prefix="/api/trades/scenarios", tags=["scenarios"])


@router.post("", response_model=ScenarioSummaryOut)
def save_scenario(request: ScenarioSaveRequest, db: Session = Depends(get_db)):
    try:
        result = analyze_trade(db, request.team_a, request.team_b)
    except TradeValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    model_version = f"{result['player_valuation_model_version']}+{result['draft_pick_model_version']}"
    scenario = TradeScenario(
        name=request.name,
        team_a_id=request.team_a.team_id,
        team_b_id=request.team_b.team_id,
        model_version=model_version,
        assumptions={"performance_multiplier": 1.0, "pick_model": "average"},
        recommendation=result,
        confidence=result["confidence"],
    )
    db.add(scenario)
    db.flush()

    team_a_side = result["team_a"]
    for asset in team_a_side["gives"]:
        db.add(
            ScenarioAsset(
                scenario_id=scenario.id,
                asset_type=asset["asset_type"],
                asset_id=asset["asset_id"],
                team_from_id=request.team_a.team_id,
                team_to_id=request.team_b.team_id,
                estimated_value=asset["value"],
            )
        )
    for asset in team_a_side["receives"]:
        db.add(
            ScenarioAsset(
                scenario_id=scenario.id,
                asset_type=asset["asset_type"],
                asset_id=asset["asset_id"],
                team_from_id=request.team_b.team_id,
                team_to_id=request.team_a.team_id,
                estimated_value=asset["value"],
            )
        )
    db.commit()
    db.refresh(scenario)

    return _summary(scenario)


def _summary(scenario: TradeScenario) -> dict:
    rec = scenario.recommendation
    return {
        "id": scenario.id,
        "name": scenario.name,
        "team_a_name": rec["team_a"]["team_name"],
        "team_b_name": rec["team_b"]["team_name"],
        "team_a_assessment": rec["team_a"]["assessment"],
        "team_b_assessment": rec["team_b"]["assessment"],
        "confidence": scenario.confidence,
        "model_version": scenario.model_version,
        "created_at": scenario.created_at.isoformat() if hasattr(scenario.created_at, "isoformat") else str(scenario.created_at),
    }


@router.get("", response_model=list[ScenarioSummaryOut])
def list_scenarios(db: Session = Depends(get_db)):
    scenarios = db.query(TradeScenario).order_by(TradeScenario.created_at.desc()).all()
    return [_summary(s) for s in scenarios]


@router.get("/{scenario_id}", response_model=ScenarioDetailOut)
def get_scenario(scenario_id: int, db: Session = Depends(get_db)):
    scenario = db.get(TradeScenario, scenario_id)
    if scenario is None:
        raise HTTPException(status_code=404, detail="Scenario not found")
    rec = scenario.recommendation
    return {
        **rec,
        "id": scenario.id,
        "name": scenario.name,
        "created_at": scenario.created_at.isoformat() if hasattr(scenario.created_at, "isoformat") else str(scenario.created_at),
    }


@router.delete("/{scenario_id}")
def delete_scenario(scenario_id: int, db: Session = Depends(get_db)):
    scenario = db.get(TradeScenario, scenario_id)
    if scenario is None:
        raise HTTPException(status_code=404, detail="Scenario not found")
    db.delete(scenario)
    db.commit()
    return {"status": "deleted", "id": scenario_id}


@router.post("/compare", response_model=list[ScenarioComparisonRowOut])
def compare_scenarios(request: ScenarioCompareRequest, db: Session = Depends(get_db)):
    if len(request.scenario_ids) < 2:
        raise HTTPException(status_code=400, detail="Provide at least two scenario ids to compare.")

    rows = []
    for scenario_id in request.scenario_ids:
        scenario = db.get(TradeScenario, scenario_id)
        if scenario is None:
            raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")

        rec = scenario.recommendation
        side = None
        if rec["team_a"]["team_id"] == request.perspective_team_id:
            side = rec["team_a"]
        elif rec["team_b"]["team_id"] == request.perspective_team_id:
            side = rec["team_b"]

        if side is None:
            rows.append(
                {
                    "scenario_id": scenario.id,
                    "name": scenario.name,
                    "applicable": False,
                    "note": "This scenario does not involve the selected perspective team.",
                }
            )
            continue

        rows.append(
            {
                "scenario_id": scenario.id,
                "name": scenario.name,
                "applicable": True,
                "assessment": side["assessment"],
                "asset_value_delta": side["asset_value_delta"],
                "draft_capital_delta": side["draft_capital_delta"],
                "financial_impact": side["financial_impact"],
                "roster_fit_score": side["roster_fit_score"],
                "risk_level": side["risk_level"],
                "timeline_alignment": side["timeline_alignment"],
                "confidence": scenario.confidence,
            }
        )
    return rows
