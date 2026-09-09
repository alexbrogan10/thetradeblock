# Draft-Pick Valuation Methodology

Implementation: `backend/app/analytics/draft_pick_valuation.py`.

## Three independent curves, shown side-by-side

There is no universally correct draft-value chart — different
methodologies disagree, especially on how much to discount Day 3 picks
relative to top-10 selections. Rather than pick one chart and present it
as authoritative, every pick shows three values:

| Model | Shape | Rationale |
|---|---|---|
| Traditional | Steep early falloff | Approximates the shape of classic pick-trade charts, where top picks carry very high relative value. |
| Historical | Flatter falloff | Approximates published research suggesting realized surplus value is more evenly distributed than trade charts imply. |
| Expected Value | Intermediate | A blended estimate of expected future on-field contribution. |

These are **original, documented formulas** (see the module docstring)
chosen to reproduce the well-known *shape* of public draft-value curves.
They do not reproduce any specific team's proprietary chart, and are not
presented as historically exact.

## Model agreement

The three values' coefficient of variation is mapped to **High /
Moderate / Low** agreement. Early first-round picks tend to show
High/Moderate agreement (all three models value them highly); Day 3
picks often show Low agreement (the models diverge more on marginal
value) — this divergence is itself useful decision-support information.

## Future / unresolved picks

A future draft pick (e.g., "2028 3rd Round Pick") has no assigned
overall slot yet, since it depends on standings that haven't happened.
Rather than guess, the pick is valued at **the midpoint slot of its
round** — an explicit, documented assumption, not a prediction of where
the team will finish.

## Combining with player value

The trade engine converts draft-pick chart points into the same
"comparable asset points" scale as the 0–100 player score using a single
configurable constant, `PICK_POINTS_TO_ASSET_SCALE` (currently 33) — so
an elite #1-overall-caliber pick (~3000 chart points ≈ ~91 asset points)
is roughly comparable to an elite player valuation. This calibration is
a modeling assumption and is intentionally isolated in one place so it
can be revisited.

## Future integration with The Draft Room

The `DraftPickValueBreakdown` schema is structured so a future "Draft
Room" application's own valuation could be substituted or shown
alongside these three (Section 51), without requiring changes to the
Trade Center UI.
