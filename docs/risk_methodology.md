# Trade Risk Methodology

See `docs/team_fit_methodology.md#risk-basic` for the current
implementation, and `backend/app/analytics/trade_engine.py::_risk_assessment`
for the code.

## Levels

Risk is expressed as **Low / Moderate / High**, never a bare number
without context, and the response always includes:

- `risk_drivers`: which factors pushed risk up (age curve, contract
  commitment, availability history, valuation uncertainty)
- `risk_mitigators`: which factors are working in the team's favor

## What this explicitly avoids (Rule 56, #22 / product spec Section 22)

- Players are never labeled "busts" or given a failure probability.
- Risk is about the *trade*, not a judgment about a person's career.
- A high-risk trade is not labeled "bad" — risk is one input to the
  overall qualitative assessment, not a verdict on its own.

## Roadmap

A full Phase 3 Risk Analysis will add: positional risk profiles (e.g.,
RB touch-volume risk), draft-pick bust-rate uncertainty by round, and
asset-concentration risk (too much value riding on one asset).
