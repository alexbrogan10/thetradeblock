# Machine Learning — Status and Plan

## Phase 1 (current): no ML in the critical path

Every score currently shown by The Trade Block (player valuation,
draft-pick valuation, trade assessment) is produced by a **transparent,
documented statistical/heuristic formula**, not a trained model. This
was a deliberate choice for the MVP: Section 38 of the product spec asks
that ML "support the platform rather than dominate it," and that data
leakage be prevented and every model be documented (features, targets,
training period, validation method, evaluation metrics, limitations).
Shipping a real, validated ML model responsibly takes real historical
data and a proper train/test split by season — which the MVP's
synthetic demo dataset cannot honestly provide (a model trained on
randomly-generated data would have no meaning).

## Where scikit-learn is intended to go (Phase 5 roadmap)

| Model | Purpose | Planned approach |
|---|---|---|
| Player Performance Projection | Predict next-season production from data available *as of* the prediction date | Gradient Boosting / Random Forest regressor per position group |
| Player Similarity | "Players with a similar statistical/contractual profile" | KNN over standardized feature vectors (age, position, production, contract) |
| Trade Outcome Analysis | Explore relationships between trade characteristics and subsequent outcomes, if enough historical trade data exists | Logistic Regression / Gradient Boosting classifier, evaluated with ROC-AUC/precision/recall |

## Data leakage prevention (binding for any future model)

- A projection model may only use statistics from seasons *before* the
  prediction date. Never include the target season's own stats as a
  feature.
- Train/validation splits must be **season-based**, not randomly
  shuffled at the player-season row level, to avoid leaking a player's
  future performance into their own past-season training row via
  shared identity features.
- Every trained model must record: features used, target definition,
  training period, validation method, and evaluation metrics
  (Section 39 — Model Versioning), and that record travels with any
  trade scenario computed using it (Section 40 — Auditability).

## What will never happen

- A model prediction will never be presented as a fact or a guarantee.
- No model will be trained on or claim access to proprietary NFL data.
