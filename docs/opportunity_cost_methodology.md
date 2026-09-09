# Opportunity Cost Methodology

Implementation: `backend/app/analytics/trade_engine.py` (see the
`opportunity_cost_notes` list built in `build_side`).

## Phase 1 scope

For every draft pick a team gives up, the engine attaches a templated
note naming the concrete alternative uses that pick's optionality
represented: retaining in-house talent, drafting a rookie, packaging the
pick in a future trade, or addressing a different roster need. When
players are given up, a similar note is attached about the value they
could have retained or realized later under different market
conditions.

## What this intentionally does not do

Per Section 21, the model **never predicts which specific player a team
would have drafted** with a surrendered pick — that would overstate the
model's knowledge. It states the category of optionality lost, not a
specific alternative outcome.

## Roadmap

A fuller Phase 3 implementation will connect this to the Draft Capital
Dashboard (showing what a team's *remaining* draft capital looks like
after the trade) and to Scenario Comparison, so a user can directly
compare "trade for Player X" against "keep the pick" as two scenarios.
