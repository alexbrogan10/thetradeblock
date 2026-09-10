# Team Fit, Team Needs, Competitive Window, and Roster Impact Methodology

Implementation: `backend/app/analytics/team_needs.py`,
`backend/app/analytics/competitive_window.py`,
`backend/app/analytics/team_fit.py`,
`backend/app/analytics/roster_impact.py`.

As of Phase 2, these are the **full engines** described in Sections
17–20 of the product spec (the Phase 1 MVP shipped simplified
placeholders; this document previously described those and has been
updated).

## Team Needs Engine (Section 18)

For every position on a 14-position depth chart, `evaluate_team_needs`
computes a 0–100 need score from signals already available elsewhere in
the app — never public rankings or invented scouting opinions:

- **No player at the position** → automatic Critical Need (100).
- **Starter quality** — the best current valuation at the position; a
  below-average starter raises the need score.
- **Depth** — a lone starter with no backup raises the score; weak
  backup depth raises it further.
- **Contract expiration** — a good starter entering the final year of
  his contract raises near-term need.
- **Succession risk** — an aging (30+) starter with no promising (≤25,
  competent) backup raises *future* need even if current need is low.

Scores map to five labels: Critical Need (≥75), Major Need (≥55),
Moderate Need (≥35), Minor Need (≥15), Strong Position (below 15).
`GET /api/team/{id}/needs` exposes this with a plain-language reason for
every position.

## Competitive Window (Section 20)

`classify_team_timeline` scores a team 0–100 on a Rebuilding ↔ Win Now
axis from three signals: an on-the-fly **team strength** proxy (average
valuation of the best player at every position the team fields), roster
**age distribution** (veteran vs. young concentration), and **future
draft capital** relative to the rest of the league (percentile rank).
The score maps to five labels: Rebuilding, Developing, Competitive,
Contender, Win Now. `GET /api/team/{id}/timeline` exposes the score,
each contributing metric, and plain-language reasons.

This intentionally does **not** use actual win-loss records (not
modeled in this dataset) or claim insider knowledge of a team's actual
plans — it is a transparent proxy, and is labeled as such everywhere it
appears.

## Team Fit Engine (Section 17)

`compute_team_fit` combines three factors for a specific
player-to-team pairing:

| Factor | Weight | Source |
|---|---|---|
| Positional need | 55% | Team Needs Engine score at the player's position |
| Age/timeline alignment | 30% | Distance from the age a team at this Competitive Window classification typically targets |
| Contract-length fit | 15% | Whether the contract's remaining term suits the team's timeline (a rebuild benefits from a longer, cheaper deal; a win-now team is less sensitive to length but wary of a long, immovable commitment) |

Every score returns a plain-language explanation (Section 17's example:
"Team A receives a higher fit score because..."), used directly in the
Trade Center's "Team Fit Explanation" panel.

## Roster Impact (Section 19)

`compute_roster_impact` computes a depth-aware 0–100 "positional
strength" score — dominated by the best player at the position, with a
smaller contribution from the second-best and a small bonus for further
depth — for every position touched by a hypothetical trade, before and
after. This is embedded directly in every trade analysis
(`roster_impact` on each side) and available standalone via
`GET /api/team/{id}/roster-impact?players_out=...&players_in=...`.

## What's still simplified

- Scheme compatibility is not modeled (no scheme data exists in the
  dataset) — Team Fit explanations do not claim to know a team's scheme.
- Competitive Window does not use real win-loss records.
- Contract-length fit is a heuristic, not a cap-modeling system (see
  `docs/limitations.md`).
