# Limitations

This document exists so results are never mistaken for more than they
are (Section 56, throughout).

## Data limitations

- The bundled demo dataset is entirely synthetic. It is useful for
  exercising every code path end-to-end, but it is **not evidence about
  any real player, contract, or trade**.
- No advanced tracking metrics (Next Gen Stats-style separation, PFF-style
  grades, blocking win rates) are included or fabricated. Offensive line
  evaluation in particular is limited to availability/starts because no
  reliable blocking metric is present in the dataset.
- Contract modeling is simplified: no proration schedule, void years,
  option bonuses, or June-1 designations. Dead-cap figures are a
  documented heuristic (`docs/team_fit_methodology.md`), not real cap
  accounting.

## Model limitations

- Player valuation is a transparent statistical formula, not a
  validated predictive model. Its weights and normalization thresholds
  are starting assumptions (explicitly configurable) and have not been
  fit against real outcome data.
- Draft-pick valuation curves are original approximations of publicly
  known chart *shapes*, not a reproduction of any specific real team's
  proprietary chart, and not a claim of historical accuracy.
- Team Fit, Risk, and Timeline Alignment in Phase 1 are intentionally
  "basic" placeholder versions of the full engines described in the
  product roadmap (Section 17-20); see `docs/team_fit_methodology.md`.
- No machine learning is in the current critical path — see
  `docs/ml_documentation.md` for what's planned and why it's deferred.

## Things this application will never claim

- That any trade is objectively correct or incorrect.
- That it has access to proprietary NFL data or any real team's internal
  systems.
- That a model output is a fact rather than a probabilistic, confidence-scored
  estimate.
- That it can replace professional scouting or football operations
  judgment.

## Scope limitations (by design)

The Trade Block intentionally does not attempt to be a roster-construction
tool, a cap-management tool, or a scouting platform — see the "Front
Office Analytics Suite" concept in the root README for where those
concerns are intended to live instead.
