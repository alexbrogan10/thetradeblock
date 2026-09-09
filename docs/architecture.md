# Architecture

The Trade Block is a decision-support application, not an automated
decision-maker. The system is deliberately structured so every number
shown to a user can be traced back to a documented calculation:

```
External Data (or Demo Data)
        |
        v
   data/raw/*.csv
        |
        v   scripts/generate_demo_data.py (demo only)
        |   scripts/seed_demo_data.py
        v
   PostgreSQL  (teams, players, statistics, contracts, draft picks,
                player_valuations)
        |
        v
   backend/app/analytics/  (player valuation, draft-pick valuation,
                             trade engine — pure functions over the DB)
        |
        v
   backend/app/api/  (FastAPI routes, Pydantic schemas)
        |
        v
   frontend/  (React + TypeScript + Tailwind + Recharts)
```

## Why this separation matters

- **Ingestion is separate from analytics.** `scripts/seed_demo_data.py`
  only loads and validates data. It does not decide what a player is
  "worth." That means a real, licensed data source can replace the demo
  CSVs without touching the analytics or API layers (Section 37, 51).
- **Analytics is separate from presentation.** Every score the frontend
  displays is computed in `backend/app/analytics/` and returned through
  a typed Pydantic schema — the frontend never re-derives a number, it
  only renders what the API returns.
- **Nothing is a black box.** `PlayerValuation`, `DraftPickValuation`,
  and the trade engine's output all include component breakdowns and a
  driver list (`positive_drivers` / `negative_drivers`), not just a
  final number.

## Services (Phase 1 / MVP)

| Service | Responsibility |
|---|---|
| `db` (PostgreSQL) | System of record for teams, players, stats, contracts, draft picks, and stored valuation snapshots. |
| `backend` (FastAPI) | REST API, request validation (Pydantic), and the analytics engines. |
| `frontend` (React/Vite) | Front Office Dashboard and Trade Center UI. |

## Relationship to the Front Office Analytics Suite

The Trade Block is one independently-runnable application in a larger
conceptual suite (Section 50). It is built to eventually consume an
imported draft-pick valuation from a sibling "Draft Room" application
without a tight coupling — see `app/schemas/draft_pick.py` and
`docs/draft_capital_methodology.md` for the intended integration seam.

## What Phase 1 does *not* include

Per the phased roadmap (Section 55), this MVP does not yet implement the
full Team Needs Engine, Trade Simulator persistence/scenario comparison,
historical trade database, player similarity (KNN), or ML-based
projection models. See `docs/limitations.md` and the root `README.md`
roadmap section for what's next.
