"""Player Similarity (Section 25).

Uses scikit-learn's k-nearest-neighbors over a standardized feature
vector (age, performance, projection, age-curve position, contract AAV,
years remaining) within the same position, restricted to players of the
same position group since cross-position comparisons aren't meaningful.

Explanations always say a comparable player "has a similar statistical
and contractual profile" -- never that one player "will become" another
(Rule 56 #13; Section 25's explicit example).
"""
from dataclasses import dataclass

import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from sqlalchemy.orm import Session

from app.analytics.player_valuation import compute_position_average_aav, evaluate_player
from app.models.contract import Contract
from app.models.player import Player
from app.models.player_statistic import PlayerStatistic


@dataclass
class SimilarPlayer:
    player_id: int
    name: str
    position: str
    team: str | None
    age: int
    valuation: float
    similarity_pct: float
    explanation: str


def find_similar_players(db: Session, player_id: int, top_n: int = 5) -> list[SimilarPlayer]:
    target = db.get(Player, player_id)
    if target is None:
        raise ValueError(f"Player {player_id} does not exist.")

    candidates = (
        db.query(Player)
        .filter(Player.position == target.position, Player.status == "active")
        .all()
    )
    if len(candidates) < 2:
        return []

    league_avg_aav = compute_position_average_aav(db)

    feature_rows = []
    meta = []
    for player in candidates:
        seasons = db.query(PlayerStatistic).filter(PlayerStatistic.player_id == player.id).all()
        contract = db.query(Contract).filter(Contract.player_id == player.id).first()
        valuation = evaluate_player(player, seasons, contract, league_avg_aav)
        feature_rows.append(
            [
                player.age,
                valuation.performance_score,
                valuation.projection_score,
                valuation.age_score,
                contract.annual_value if contract else 0.0,
                contract.years_remaining if contract else 0.0,
            ]
        )
        meta.append((player, valuation))

    X = StandardScaler().fit_transform(np.array(feature_rows, dtype=float))
    target_idx = next(i for i, (p, _) in enumerate(meta) if p.id == player_id)

    k = min(top_n + 1, len(candidates))
    nn = NearestNeighbors(n_neighbors=k, metric="cosine").fit(X)
    distances, indices = nn.kneighbors([X[target_idx]])

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        player, valuation = meta[idx]
        if player.id == player_id:
            continue
        similarity_pct = max(0.0, round((1 - dist) * 100, 1))
        results.append(
            SimilarPlayer(
                player_id=player.id,
                name=player.name,
                position=player.position,
                team=player.team.abbreviation if player.team else None,
                age=player.age,
                valuation=valuation.valuation,
                similarity_pct=similarity_pct,
                explanation=(
                    f"{player.name} has a similar statistical and contractual profile "
                    f"(age, production trajectory, and contract terms) to {target.name}."
                ),
            )
        )

    results.sort(key=lambda r: r.similarity_pct, reverse=True)
    return results[:top_n]
