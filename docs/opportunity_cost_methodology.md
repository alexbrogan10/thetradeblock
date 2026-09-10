# Opportunity Cost, Sensitivity Analysis & Scenario Tools

Implementation: `backend/app/analytics/trade_engine.py` (opportunity
cost notes), `backend/app/analytics/sensitivity.py` (Sensitivity
Analysis / "What Would Change This?"), `backend/app/api/scenarios.py`
(Trade Simulator persistence + Scenario Comparison), and
`backend/app/analytics/discrepancy.py` /
`backend/app/analytics/trade_finder.py`.

## Opportunity Cost (Section 21)

For every draft pick a team gives up, the engine attaches a templated
note naming the concrete alternative uses that pick's optionality
represented: retaining in-house talent, drafting a rookie, packaging the
pick in a future trade, or addressing a different roster need. The model
**never predicts which specific player** a team would have drafted with
a surrendered pick (Section 21) — it names the category of optionality
lost, not a specific alternative outcome.

## Sensitivity Analysis (Section 28)

Rather than a separate, drift-prone "sensitivity formula," sensitivity
re-runs the *exact same* trade engine (`analyze_trade`) under varied
assumptions:

- **Performance sensitivity**: a `performance_multiplier` (0.9 / 1.0 /
  1.1) scales every involved player's performance and projection scores
  before the rest of the valuation runs, showing whether the assessment
  changes if outcomes come in below/above projection.
- **Draft-pick model sensitivity**: re-runs using each of the
  Traditional / Historical / Expected Value draft-pick curves
  exclusively (instead of their average), surfacing cases where the
  recommendation depends on which methodology is trusted.

This is intentionally a small, fixed set of counterfactuals rather than
a continuous simulation — it answers "does this hold up under a
plausible range of outcomes?" without implying false precision.

## "What Would Change This?" (Section 29)

Generated directly from the sensitivity re-runs: if a multiplier or
pick-model change flips the qualitative assessment, that is surfaced as
a plain-language statement (e.g., *"If performance drops to 90% of
projection, the assessment shifts from 'Favorable' to 'Balanced.'"*).
If nothing tested changes the outcome, the tool says so explicitly
rather than inventing a caveat.

## Trade Simulator & Scenario Comparison (Sections 26-27)

Saving a scenario (`POST /api/trades/scenarios`) runs the ordinary trade
engine once and freezes the **entire result** as JSON on the
`trade_scenarios` row, along with the model version string used. Reading
a saved scenario back (`GET /api/trades/scenarios/{id}`) returns that
frozen JSON — it is **never recomputed** with the current model, so a
scenario saved before a future model change keeps showing the result
that was true when it was saved (Section 40 — Auditability). Comparing
scenarios (`POST /api/trades/scenarios/compare`) extracts the named
perspective team's side from each frozen result and lines them up in one
table, matching Section 27's "Scenario A vs. Scenario B vs. keep
current assets" workflow.

## Value Discrepancy Finder & Trade Finder (Sections 16, 23)

Both reuse the player valuation and Team Fit/Team Needs engines rather
than introducing separate scoring logic:

- The Discrepancy Finder compares a player's analytical value against
  an expected-value-for-cost proxy derived from their own contract
  relative to league-average pay at the position, framed as *"the model
  identifies a potential value discrepancy,"* never a claim of
  objective mispricing.
- The Trade Finder filters candidates at a requested position by
  acquisition-cost ceiling, age preference, and risk tolerance, then
  ranks the remainder by the same Team Fit score used in trade
  analysis — so a "potential target" list and an actual trade analysis
  never disagree about what "good fit" means.
- Acquisition cost ranges (`app/analytics/acquisition_cost.py`) invert
  the Traditional draft-pick curve to express a player's value as an
  approximate pick range (e.g., "Early 2nd Round – Late 2nd Round"),
  explicitly labeled a **model estimate**, never a team's actual asking
  price (Section 15).
