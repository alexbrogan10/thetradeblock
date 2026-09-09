# Team Fit, Risk, and Timeline Methodology (Phase 1 Basic Versions)

Implementation: `backend/app/analytics/trade_engine.py`.

The full Team Fit Engine, Team Needs Engine, and Competitive Window
classifier described in the product spec (Sections 17–20) are **Phase 2
roadmap items**. Phase 1 ships intentionally simplified versions of each
so the Trade Center can still surface roster-fit, risk, and timeline
signals end-to-end.

## Roster Fit (basic)

For each player a team would receive, the engine counts how many active
players the receiving team already has at that position (excluding
players leaving in the same trade). More existing depth → lower fit
score; a position with no depth → higher fit score. A small adjustment
is applied for player age. This captures "does this fill a hole?" but
does **not** yet account for scheme fit, starter-vs-backup quality, or
projected future need — those require the full Team Needs Engine.

## Risk (basic)

Risk is the average of four already-computed valuation sub-scores,
inverted, across the players a team would receive:

- Age curve risk (inverse of age score)
- Contract commitment risk (inverse of contract efficiency score)
- Availability risk (inverse of availability score)
- Valuation uncertainty (inverse of the player's own confidence score)

This reuses the player valuation model's own components rather than
introducing a second, separate risk model — every risk driver traces
back to a number already shown elsewhere in the app.

## Timeline Alignment (basic proxy)

The team's active roster average age is used as a simple proxy for
"win-now" (≥27) vs. "developing" (<27) leaning, and incoming assets are
scored against that leaning. This is a placeholder for the full
Competitive Window classifier (Section 20), which will incorporate QB
situation, draft capital, and contract commitments once Phase 2 lands.

## Why "basic" is disclosed explicitly

Per Rule 56 (#5, #17), the app must clearly distinguish what it actually
computes from what it doesn't yet. Anywhere these basic versions are
shown, the accompanying docs/UI text says so, so a front-office user does
not mistake a Phase 1 heuristic for the full modeled engine.
