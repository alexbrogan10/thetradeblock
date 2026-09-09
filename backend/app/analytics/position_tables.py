"""Static, transparent assumptions used by the valuation models.

These tables are *modeling assumptions*, not measured facts. They exist so
the rest of the analytics code has a single, documented place to look when
explaining "why" a score came out the way it did (Section 41 -
Explainability). Every number here is configurable and should be revisited
as real data becomes available -- see docs/valuation_methodology.md.
"""

POSITION_GROUP = {
    "QB": "QB",
    "RB": "RB",
    "WR": "WR",
    "TE": "TE",
    "OT": "OL",
    "IOL": "OL",
    "EDGE": "EDGE",
    "DT": "DT",
    "LB": "LB",
    "CB": "CB",
    "S": "S",
    "K": "SPEC",
    "P": "SPEC",
    "LS": "SPEC",
}

# Relative positional value on the open market (0-100). Reflects the
# general premium NFL front offices place on certain positions, not any
# individual player's talent.
POSITION_VALUE = {
    "QB": 100,
    "EDGE": 90,
    "WR": 85,
    "CB": 84,
    "OT": 80,
    "S": 68,
    "DT": 70,
    "IOL": 64,
    "LB": 63,
    "TE": 62,
    "RB": 52,
    "K": 30,
    "P": 24,
    "LS": 14,
}

# Positional scarcity (0-100): how difficult the position is to replace
# with a comparable starter league-wide. Related to, but distinct from,
# positional value.
POSITIONAL_SCARCITY = {
    "QB": 96,
    "EDGE": 88,
    "OT": 82,
    "CB": 80,
    "WR": 70,
    "S": 62,
    "DT": 66,
    "IOL": 58,
    "LB": 55,
    "TE": 60,
    "RB": 40,
    "K": 20,
    "P": 18,
    "LS": 12,
}

# Age curve parameters (peak age, sigma) per position group, used to build
# a bell-shaped age score. Wider sigma == career value declines more
# gradually around the peak.
AGE_CURVE = {
    "QB": (29, 6.5),
    "RB": (25, 3.0),
    "WR": (27, 4.0),
    "TE": (27, 4.5),
    "OL": (28, 5.0),
    "EDGE": (27, 4.5),
    "DT": (27, 4.5),
    "LB": (26, 4.0),
    "CB": (26, 4.0),
    "S": (27, 4.5),
    "SPEC": (30, 9.0),
}

# Per-position stat normalization: maps a stat key to a "star level"
# threshold (roughly a Pro-Bowl caliber season) used only to scale a raw
# counting stat into a 0-100 production index. These thresholds are
# normalization assumptions applied to whatever stats are supplied (real
# or demo) -- they do not invent statistics.
PRODUCTION_WEIGHTS = {
    "QB": {
        "pass_yards": (4800, 0.25),
        "pass_td": (38, 0.25),
        "completion_pct": (68, 0.15),
        "interceptions_inv": (8, 0.15),  # fewer is better, handled specially
        "rush_yards": (400, 0.10),
        "epa_per_play": (0.20, 0.10),
    },
    "RB": {
        "rush_yards": (1400, 0.30),
        "yards_per_carry": (4.8, 0.15),
        "rush_td": (12, 0.20),
        "rec_yards": (450, 0.15),
        "receptions": (55, 0.10),
        "yards_after_contact_per_att": (3.2, 0.10),
    },
    "WR": {
        "receptions": (95, 0.20),
        "rec_yards": (1300, 0.30),
        "rec_td": (10, 0.20),
        "yards_per_reception": (14.5, 0.15),
        "targets": (140, 0.15),
    },
    "TE": {
        "receptions": (70, 0.30),
        "rec_yards": (850, 0.35),
        "rec_td": (7, 0.25),
        "yards_per_reception": (11.5, 0.10),
    },
    "OL": {
        "games_started_ratio": (1.0, 1.0),
    },
    "EDGE": {
        "sacks": (12, 0.35),
        "tackles_for_loss": (14, 0.25),
        "qb_hits": (20, 0.20),
        "forced_fumbles": (3, 0.10),
        "tackles": (55, 0.10),
    },
    "DT": {
        "sacks": (7, 0.30),
        "tackles_for_loss": (12, 0.25),
        "tackles": (55, 0.25),
        "qb_hits": (14, 0.20),
    },
    "LB": {
        "tackles": (110, 0.35),
        "tackles_for_loss": (10, 0.20),
        "sacks": (4, 0.15),
        "interceptions": (2, 0.15),
        "passes_defended": (6, 0.15),
    },
    "CB": {
        "interceptions": (4, 0.30),
        "passes_defended": (14, 0.35),
        "tackles": (60, 0.20),
        "forced_fumbles": (2, 0.15),
    },
    "S": {
        "tackles": (85, 0.30),
        "interceptions": (3, 0.30),
        "passes_defended": (9, 0.25),
        "forced_fumbles": (2, 0.15),
    },
    "K": {
        "fg_pct": (0.93, 0.6),
        "long": (58, 0.2),
        "fg_made": (30, 0.2),
    },
    "P": {
        "avg_punt_yards": (47.5, 0.6),
        "punts_inside_20_pct": (0.45, 0.4),
    },
    "LS": {},
}
