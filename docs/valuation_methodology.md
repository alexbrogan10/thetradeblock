# Player Trade Value Methodology

Implementation: `backend/app/analytics/player_valuation.py` and
`backend/app/analytics/position_tables.py`.

## What the score is — and is not

The **Player Trade Value Score** (0–100) is an *estimated organizational
asset value*, built from a transparent statistical formula. It is:

- **Not** a fantasy-football score.
- **Not** a claim about a player's real-world market price.
- **Not** derived from proprietary scouting reports.

It is a documented, reproducible combination of eight components, each
independently visible in the API response (`PlayerValuationOut`).

## Components and default weights

| Component | Weight | What it measures |
|---|---|---|
| Recent Performance | 20% | Position-specific production in the most recent season on file. |
| Projected Performance | 20% | Recent performance adjusted by the direction the age curve is heading. |
| Age | 15% | A bell curve centered on a position-specific "peak age." |
| Position Value | 10% | Static, documented assumption about positional market value. |
| Contract Efficiency | 15% | Estimated pay relative to production, vs. league-average pay at the position. |
| Availability | 5% | Games played / games possible over the seasons on file. |
| Positional Scarcity | 10% | Static, documented assumption about replacement difficulty. |
| Trajectory | 5% | Year-over-year change in the production score (needs 2+ seasons). |

**Weights are configuration, not code.** They live in
`backend/app/config.py` (`weight_*` settings) and can be changed via
environment variables without touching the analytics code.

## Position-specific production

Different positions use different stat keys and normalization
thresholds (`PRODUCTION_WEIGHTS` in `position_tables.py`) — a QB's score
is never computed with a WR's formula. Offensive line positions
intentionally use only availability/starts, **not** fabricated
pass-blocking or pressure-rate grades, because this project does not
claim access to that kind of proprietary charting data (Rule: Section
56, #16).

## Handling missing data

- No statistics on file → performance score defaults to a neutral 50,
  and a note is attached (`"No recent statistical data available..."`),
  and confidence is reduced.
- No contract on file → contract score defaults to a neutral 50, and a
  note is attached; confidence is reduced.
- Fewer than 2 seasons on file → trajectory defaults to neutral (50);
  the model does not guess a trend from a single data point.

## Confidence

Confidence (15–95%) increases with the amount of underlying data
available (recent stats, multiple seasons, contract data, availability
history) and is **capped below 100%** — the model never claims
certainty (Section 42, Rule: Section 56 #9).

## Explainability

Every valuation returns `positive_drivers` and `negative_drivers` —
plain-language statements tied to the component that produced them
(e.g., "Strong recent on-field production," "Contract cost is high
relative to production"). This is what powers the "Why is this player
valued at X?" view (Section 41).

## Known limitations

See `docs/limitations.md`. In short: this is a heuristic statistical
model tuned for transparency, not a machine-learned projection system
(that is a Phase 5 roadmap item), and all default thresholds/weights are
starting assumptions that should be revisited against real data.
