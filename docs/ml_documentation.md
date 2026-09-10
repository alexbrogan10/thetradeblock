# Machine Learning — Status and Plan

Every score The Trade Block shows is either a **transparent, documented
statistical formula** (player valuation, draft-pick valuation, trade
assessment, Team Needs, Competitive Window, Team Fit — see the other
methodology docs) or a **clearly-separate, versioned ML model** that
supports the platform without replacing those transparent scores
(Section 38: "ML should support the platform rather than dominate it").
Nothing here silently swaps a heuristic for an ML prediction.

## Shipped: Player Similarity via KNN (Phase 4)

`backend/app/analytics/player_similarity.py` uses scikit-learn's
`NearestNeighbors` (cosine metric) over a standardized feature vector
(age, performance score, projection score, age-curve position, contract
AAV, years remaining), restricted to players at the same position.
Output is always framed as "has a similar statistical and contractual
profile," never a prediction that one player will become another.

## Shipped: Player Performance Projection via RandomForest (Phase 5)

`scripts/train_performance_projection.py` trains a
`RandomForestRegressor` (scikit-learn, 200 trees, max depth 6, wrapped
in a `Pipeline` with a `OneHotEncoder` for position) to predict a
player's **next**-season performance score from features known as of
the prior season: age, position, prior performance score, prior
availability, and current contract terms.

**This is separate from, and does not replace,** the transparent
heuristic projection used inside the core Player Trade Value score
(`docs/valuation_methodology.md`). It is exposed as an additional,
opt-in signal at `GET /api/players/{id}/projection`, clearly labeled
with its own model version and a note that it is a model estimate, not
a validated prediction.

**Leakage prevention**: every feature is something knowable *before*
the target season; the target season's own stats are never used as a
feature for that same season. `backend/app/ml/features.py` is the single
shared implementation of feature extraction, used by both the training
script and the runtime inference module (`app/ml/performance_projection.py`)
so there is exactly one definition of what each feature means.

**Evaluation** (recorded per-run in the `model_versions` table and shown
on `/model-versions`): MAE, RMSE, and R² on a held-out test split, plus
`n_train`/`n_test` sample counts. Feature importances from the fitted
forest are surfaced alongside every prediction.

**Documented limitations** (also stored on the model version row, not
just here):
- Trained on a single synthetic season-to-season transition per player
  (the demo dataset's 2024→2025 pair) — not validated against
  real-world outcomes.
- Uses each player's *current* contract as a proxy for their contract
  situation at prediction time, since this dataset has no historical
  contract table.
- The train/test split is a random hold-out, not a season-based split,
  because only one transition exists per player in this demo dataset.
  **A real deployment with multiple seasons per player must use a
  season-based split** to avoid leakage (see below) — this is called
  out explicitly so the shortcut here is never mistaken for the general
  rule.

## Shipped: Model Versioning (Phase 5, Section 39)

Every model — heuristic or ML — is registered in the `model_versions`
table with its features, parameters/weights, evaluation metrics (empty
for heuristics, since a fixed formula has nothing to "evaluate" against
without real outcome data), dataset version, and limitations. This
satisfies Section 39's example format ("Player Valuation Model,
Version: 1.0, Date: 2026") uniformly across every model in the app, not
just the ML one. See `/model-versions` in the UI or
`GET /api/ml/model-versions`.

## Shipped: Trade Matching (Phase 5, Section 38)

`GET /api/team/{id}/trade-matches` automatically runs the Trade Finder
(Section 23) against every position the Team Needs Engine currently
grades Critical or Major Need, so "which players analytically fit this
team's needs" never requires the user to already know which position to
search. It deliberately reuses the exact same Team Fit scoring as manual
Trade Finder searches and Trade Center analysis — there is only one
definition of "fit" in the app.

## Roadmap: Trade Outcome Analysis

Not yet built. If/when enough historical trade data exists (real or a
much larger synthetic set), a Logistic Regression or Gradient Boosting
classifier could explore relationships between trade characteristics and
subsequent outcomes, evaluated with ROC-AUC/precision/recall. The
current synthetic historical-trade dataset (55 trades) is too small and
too randomly generated for this to produce a meaningful model — building
it now would create the appearance of insight without the substance.

## Data leakage prevention (binding for any future model)

- A projection model may only use statistics from seasons *before* the
  prediction date. Never include the target season's own stats as a
  feature.
- Train/validation splits must be **season-based**, not randomly
  shuffled at the player-season row level, once multiple seasons per
  player are available — to avoid leaking a player's future performance
  into their own past-season training row via shared identity features.
- Every trained model must record: features used, target definition,
  training period, validation method, and evaluation metrics
  (Section 39 — Model Versioning), and that record travels with any
  trade scenario computed using it (Section 40 — Auditability).

## What will never happen

- A model prediction will never be presented as a fact or a guarantee.
- No model will be trained on or claim access to proprietary NFL data.
- An ML prediction will never silently replace a transparent heuristic
  score without a clearly separate, labeled surface for it.
