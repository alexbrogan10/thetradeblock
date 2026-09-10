# The Trade Block

**NFL Trade & Asset-Exchange Decision-Support Platform**

> Independent project disclaimer: This is not affiliated with, endorsed
> by, or built using proprietary data from the NFL or any NFL team. All
> data in the default configuration is **synthetic demo data** —
> clearly labeled throughout the app — not real NFL statistics,
> contracts, or trades.

The Trade Block is one application in a larger conceptual **Front
Office Analytics Suite** (see below). It focuses exclusively on trade
and asset-exchange intelligence: turning a hypothetical NFL trade into a
structured, explainable organizational decision.

```
Data → Analytics → Model → Recommendation → Explanation
```

## Problem Statement

Front offices evaluating a trade need to weigh far more than "who has
the better player": contract cost, positional need, roster depth,
competitive timeline, draft capital, and risk all matter — and the same
player can be a great fit for one team and a poor one for another.
The Trade Block exists to make that multi-factor evaluation explicit,
transparent, and reproducible, instead of collapsing it into a single
"win/loss" grade.

## Product Philosophy

There is no universally correct NFL trade. This application will never
say a trade is objectively correct — only things like *"Model favors
Team A," "Potentially favorable," "Strong roster fit,"* or *"Model
identifies a potential value discrepancy."* Every output includes a
confidence percentage and an explicit "what could change this"
explanation. This is **decision support, not automated decision-making.**

## Key Features (Phase 1 — MVP, shipped)

- **Front Office Dashboard** — highest-value players, positions
  commanding value, teams with notable draft capital, model alerts, and
  potential trade-value discrepancies.
- **Trade Center** — select two teams, add any number of players and/or
  current or future draft picks to each side, and get a full two-sided
  analysis.
- **Explainable Player Trade Value** — a transparent 0–100 score built
  from eight documented components (performance, projection, age,
  position, contract efficiency, availability, scarcity, trajectory),
  computed with position-specific logic.
- **Draft Pick Valuation** — three independent valuation curves
  (Traditional / Historical / Expected Value) shown side by side, with
  a model-agreement indicator, rather than pretending one chart is
  correct.
- **Trade Analysis** — per-team asset value, roster fit, draft capital
  delta, financial/cap impact, risk (Low/Moderate/High with drivers and
  mitigators), timeline alignment, opportunity cost notes, an overall
  qualitative assessment, and confidence — all with an expandable "Why?"
  and "What could change this?" for every trade side.

See the [Development Roadmap](#development-roadmap) below for what's
planned in Phases 2–6 (Team Intelligence, Advanced Trade Analytics,
Historical Analytics, Machine Learning, Production Polish).

## Screenshots

**Front Office Dashboard**

Executive-style overview: highest-value players, positions commanding
trade value, teams by draft capital, model alerts, and value
discrepancies.

**Trade Center**

Select teams and assets on both sides, then get a full two-sided,
explainable trade analysis with confidence and risk breakdowns.

*(Run the app locally via Docker Compose below to see it live — the UI
is intentionally styled like professional front-office analytics
software, not a fan trade machine.)*

## Technology Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy, Pydantic |
| Database | PostgreSQL |
| Analytics | Pandas, NumPy |
| ML (planned, Phase 5) | scikit-learn |
| Frontend | React, TypeScript, Vite, Tailwind CSS |
| Visualization | Recharts |
| Infrastructure | Docker, Docker Compose |

## Architecture

See [`docs/architecture.md`](docs/architecture.md) for the full data-flow
diagram and rationale. In short: ingestion (CSV → PostgreSQL) is fully
decoupled from analytics (`backend/app/analytics/`), which is decoupled
from presentation (FastAPI → React). A real/licensed data source can
replace the demo CSVs without touching analytics or frontend code.

## Database Schema (Phase 1)

`teams`, `players`, `player_statistics` (position-specific stats in a
documented JSON column), `contracts`, `draft_picks`, `player_valuations`.
See `backend/app/models/` for the SQLAlchemy definitions and
`data/raw/README.md` for field documentation. (`historical_trades`,
`trade_assets`, `trade_scenarios`, `scenario_assets`, `team_needs`, and
`team_rosters` are modeled in the product spec for later phases and are
not yet part of the Phase 1 schema.)

## Methodology Docs

- [`docs/valuation_methodology.md`](docs/valuation_methodology.md) — Player Trade Value Score
- [`docs/draft_capital_methodology.md`](docs/draft_capital_methodology.md) — Draft-pick valuation
- [`docs/team_fit_methodology.md`](docs/team_fit_methodology.md) — Roster fit, risk, timeline (Phase 1 basic versions)
- [`docs/risk_methodology.md`](docs/risk_methodology.md) — Trade risk
- [`docs/opportunity_cost_methodology.md`](docs/opportunity_cost_methodology.md) — Opportunity cost
- [`docs/ml_documentation.md`](docs/ml_documentation.md) — ML status and plan
- [`docs/data_sources.md`](docs/data_sources.md) — Data provenance
- [`docs/limitations.md`](docs/limitations.md) — What this system does not do

## Example Trade Analysis

```
POST /api/trades/analyze
{
  "team_a": {"team_id": 5, "player_ids": [78], "draft_pick_ids": []},
  "team_b": {"team_id": 6, "player_ids": [97], "draft_pick_ids": [229]}
}
```

Response (abridged):

```
TEAM A (Baltimore Ravens)
  Receives: Aiden Yarbrough (RB) [54.1], 2027 Round 1 (future) [845.4 pts]
  Gives:    Aiden Brantley (RB) [56.9]
  Asset Value Delta: +22.8   Roster Fit: 85.0   Risk: Low
  Assessment: Favorable

TEAM B (Cincinnati Bengals)
  Receives: Aiden Brantley (RB) [56.9]
  Gives:    Aiden Yarbrough (RB) [54.1], 2027 Round 1 (future) [845.4 pts]
  Asset Value Delta: -22.8  Roster Fit: 90.0   Risk: Low
  Assessment: Potentially Favorable

Overall Confidence: 76.7%
Disclaimer: Decision support only. Not a claim of objective correctness,
proprietary NFL data, or an actual front-office system.
```

## Installation & Running Locally

### Option A — Docker Compose (recommended)

```bash
cp .env.example .env
docker compose up -d --build         # starts db + backend + frontend
docker compose run --rm seed         # generates + loads demo data (first run)
docker compose run --rm train        # trains the ML projection model (optional; see Phase 5)
```

- API: http://localhost:8000 (OpenAPI docs at `/docs`)
- Frontend: http://localhost:5173

To regenerate demo data with different values, run
`python scripts/generate_demo_data.py` before `docker compose run --rm seed`.
A pre-trained model is committed at
`models/player_performance_projection_v1.joblib`, so `docker compose run
--rm train` is only needed after re-seeding with different data.

### Option B — Run backend/frontend directly

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg2://tradeblock:tradeblock@localhost:5432/tradeblock
python ../scripts/generate_demo_data.py   # from repo root, or adjust path
python ../scripts/seed_demo_data.py
python ../scripts/train_performance_projection.py   # optional: trains the ML projection model
uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## API Documentation

FastAPI serves interactive OpenAPI docs at `/docs` once the backend is
running. Key endpoints:

```
GET  /api/teams
GET  /api/teams/{id}
GET  /api/players?team_id=&position=
GET  /api/players/{id}                 # includes valuation + explanation
GET  /api/players/{id}/similar         # Player Similarity (KNN)
GET  /api/players/{id}/projection      # ML Performance Projection
GET  /api/draft-picks?team_id=&year=
GET  /api/draft-picks/{id}/valuation   # Traditional/Historical/Expected breakdown
POST /api/trades/analyze
POST /api/trades/sensitivity           # Sensitivity Analysis + What Would Change This?
POST /api/trades/finder                # Trade Finder
POST /api/trades/scenarios             # Save a Trade Simulator scenario
GET  /api/trades/scenarios             # List saved scenarios
POST /api/trades/scenarios/compare     # Scenario Comparison
GET  /api/team/{id}/needs              # Team Needs Engine
GET  /api/team/{id}/timeline           # Competitive Window
GET  /api/team/{id}/draft-capital      # Draft Capital Dashboard
GET  /api/team/{id}/roster-impact      # Before/after positional strength
GET  /api/team/{id}/trade-matches      # Trade Matching (auto Trade Finder per need)
GET  /api/historical-trades/comparable # Historical Trade Database search
GET  /api/analytics/dashboard          # Front Office Dashboard data
GET  /api/analytics/value-discrepancies
GET  /api/ml/model-versions            # Model Versioning
```

## Testing

```bash
cd backend
export DATABASE_URL=postgresql+psycopg2://tradeblock:tradeblock@localhost:5432/tradeblock_test
python -m pytest tests/ -v
```

85 tests cover player valuation (including missing-data and extreme-value
edge cases), draft-pick valuation, the trade engine (multi-asset trades,
duplicate/invalid assets, same-team rejection, missing contract data,
future picks), Team Needs/Fit/Competitive Window/Roster Impact, trade
scenarios and comparison, sensitivity analysis, the discrepancy finder
and trade finder, historical trades and player similarity, the ML
projection model, and the full API layer.

## Deployment

The project is structured so the same three services (db, backend,
frontend) map onto any of these without code changes:

- **Docker Compose** (any host / AWS / Azure): `docker-compose.yml` is
  the source of truth — see Installation above.
- **Render**: `render.yaml` at the repo root is a ready-to-use
  [Blueprint](https://render.com/docs/blueprint-spec) — a managed
  Postgres instance, the FastAPI backend (native Python runtime), and
  the frontend as a static build. Connect the repo in the Render
  dashboard and it provisions all three.
- **Railway**: create a service per Dockerfile (`backend/Dockerfile`,
  `frontend/Dockerfile`) plus a Postgres plugin, and set the same
  environment variables as `.env.example`.

After the first deploy on any platform, run the data pipeline once
(`scripts/generate_demo_data.py` then `scripts/seed_demo_data.py`) —
`models/player_performance_projection_v1.joblib` is committed, so
`scripts/train_performance_projection.py` is only needed after
re-seeding with different data.

## Limitations

See [`docs/limitations.md`](docs/limitations.md). In short: all demo data
is synthetic; contract/cap modeling is simplified; Team Fit/Risk/Timeline
are Phase 1 "basic" versions of the full engines; no ML is in the
critical path yet.

## Development Roadmap

- ✅ **Phase 1 — MVP**: PostgreSQL, FastAPI, React/TypeScript, Docker,
  core schema, player & draft-pick valuation, Trade Center, executive
  dashboard.
- ✅ **Phase 2 — Team Intelligence**: full Team Needs Engine
  (`GET /api/team/{id}/needs`), full Team Fit Engine (need + timeline +
  contract fit), Competitive Window classifier
  (`GET /api/team/{id}/timeline`), Roster Impact before/after
  (`GET /api/team/{id}/roster-impact`, also embedded per trade side),
  Draft Capital Dashboard page (`GET /api/analytics/draft-capital`),
  and detailed Contract Impact (this-year + ~3yr outlook) embedded in
  every trade analysis.
- ✅ **Phase 3 — Advanced Trade Analytics**: Trade Simulator with saved
  scenarios (`/scenarios`, frozen at save time per Section 40), Scenario
  Comparison (`POST /api/trades/scenarios/compare`), Trade Value
  Discrepancy Finder as a first-class page (`/value-discrepancies`),
  Trade Finder (`/trade-finder`) with acquisition-cost estimation,
  Sensitivity Analysis + "What Would Change This?" embedded in the
  Trade Center.
- ✅ **Phase 4 — Historical Analytics**: synthetic Historical Trade
  Database with comparable-trade search
  (`/historical-trades`, `GET /api/historical-trades/comparable`), and
  Player Similarity via scikit-learn KNN (`GET /api/players/{id}/similar`).
- ✅ **Phase 5 — Machine Learning**: leakage-safe Player Performance
  Projection (scikit-learn RandomForestRegressor,
  `scripts/train_performance_projection.py`,
  `GET /api/players/{id}/projection` with feature importance), Model
  Versioning for every model — heuristic and ML — with evaluation
  metrics and documented limitations (`/model-versions`), and Trade
  Matching (`GET /api/team/{id}/trade-matches`) that automatically runs
  the Trade Finder against every Critical/Major-Need position.
- ✅ **Phase 6 — Production Polish**: Executive Trade Report exportable
  as JSON, CSV, or print-to-PDF directly from the Trade Center; a
  Players browse page with team/position/name filtering; N+1 query
  fixes across the dashboard, discrepancy finder, Team Needs, and
  Competitive Window (bulk player valuation instead of per-player
  queries); a `render.yaml` Blueprint for one-click Render deployment
  (Docker Compose already covers self-hosted/AWS/Azure/Railway).

## Front Office Analytics Suite

The Trade Block is designed to run standalone but fits into a larger
conceptual suite of independent applications, each with its own
repository:

| App | Focus |
|---|---|
| The Draft Room | Draft and prospect intelligence |
| **The Trade Block** | Player, pick, and asset exchange decisions *(this repo)* |
| Roster Architect | Roster construction and long-term planning |
| The Cap Room | Contracts and salary-cap strategy |
| The Talent Room | Scouting and talent evaluation |

This repository intentionally does not implement the other four —
see `docs/architecture.md` for the integration seam left for a future
Draft Room connection.

## License

See [`LICENSE`](LICENSE).
