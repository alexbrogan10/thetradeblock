#!/usr/bin/env python3
"""Generates synthetic DEMO DATA for The Trade Block.

*** DEMO DATA -- NOT OFFICIAL NFL DATA ***

Every player, contract, statistic, and draft-pick record produced by this
script is entirely synthetic (fictional names, randomly generated within
realistic ranges using a fixed seed for reproducibility). Team names,
abbreviations, conferences, and divisions are public information about
the league's structure, not proprietary data.

Nothing produced here should ever be presented as real NFL statistics,
contracts, or trades. See data/raw/README.md for full documentation of
sources, fields, and limitations (Section 35/36).

Run: python scripts/generate_demo_data.py
Output: data/raw/{teams,players,player_stats,contracts,draft_picks}.csv
"""
import random
from pathlib import Path

import pandas as pd

random.seed(20260101)

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "data" / "raw"

TEAMS = [
    ("Buffalo Bills", "BUF", "AFC", "East"),
    ("Miami Dolphins", "MIA", "AFC", "East"),
    ("New England Patriots", "NE", "AFC", "East"),
    ("New York Jets", "NYJ", "AFC", "East"),
    ("Baltimore Ravens", "BAL", "AFC", "North"),
    ("Cincinnati Bengals", "CIN", "AFC", "North"),
    ("Cleveland Browns", "CLE", "AFC", "North"),
    ("Pittsburgh Steelers", "PIT", "AFC", "North"),
    ("Houston Texans", "HOU", "AFC", "South"),
    ("Indianapolis Colts", "IND", "AFC", "South"),
    ("Jacksonville Jaguars", "JAX", "AFC", "South"),
    ("Tennessee Titans", "TEN", "AFC", "South"),
    ("Denver Broncos", "DEN", "AFC", "West"),
    ("Kansas City Chiefs", "KC", "AFC", "West"),
    ("Las Vegas Raiders", "LV", "AFC", "West"),
    ("Los Angeles Chargers", "LAC", "AFC", "West"),
    ("Dallas Cowboys", "DAL", "NFC", "East"),
    ("New York Giants", "NYG", "NFC", "East"),
    ("Philadelphia Eagles", "PHI", "NFC", "East"),
    ("Washington Commanders", "WAS", "NFC", "East"),
    ("Chicago Bears", "CHI", "NFC", "North"),
    ("Detroit Lions", "DET", "NFC", "North"),
    ("Green Bay Packers", "GB", "NFC", "North"),
    ("Minnesota Vikings", "MIN", "NFC", "North"),
    ("Atlanta Falcons", "ATL", "NFC", "South"),
    ("Carolina Panthers", "CAR", "NFC", "South"),
    ("New Orleans Saints", "NO", "NFC", "South"),
    ("Tampa Bay Buccaneers", "TB", "NFC", "South"),
    ("Arizona Cardinals", "ARI", "NFC", "West"),
    ("Los Angeles Rams", "LAR", "NFC", "West"),
    ("San Francisco 49ers", "SF", "NFC", "West"),
    ("Seattle Seahawks", "SEA", "NFC", "West"),
]

# Fictional name pools -- deliberately generic so generated combinations
# are not intended to reference any real person.
FIRST_NAMES = [
    "Marcus", "Jalen", "Trevor", "Devon", "Caleb", "Elijah", "Xavier", "Malik",
    "Tyson", "Bryce", "Cooper", "Dante", "Isaiah", "Jaxon", "Kellen", "Landon",
    "Mason", "Nolan", "Omar", "Preston", "Quinton", "Reggie", "Sterling", "Trent",
    "Vaughn", "Wesley", "Yusuf", "Zane", "Aiden", "Brandt", "Cyrus", "Deshawn",
]
LAST_NAMES = [
    "Whitfield", "Osei", "Brantley", "Calloway", "Donnell", "Ekstrom", "Farrow",
    "Greenidge", "Holloway", "Ibarra", "Jarrell", "Kowalski", "Larkspur", "Munoz",
    "Northcutt", "Obioma", "Pemberton", "Quintela", "Ridgeway", "Sowande",
    "Tarleton", "Underhill", "Vantrease", "Winslow", "Yarbrough", "Zeleny",
]

POSITION_TEMPLATE = [
    ("QB", 1), ("RB", 2), ("WR", 3), ("TE", 1),
    ("OT", 2), ("IOL", 1), ("EDGE", 2), ("DT", 1),
    ("LB", 2), ("CB", 2), ("S", 1), ("K", 1),
]

AGE_RANGE = {
    "QB": (23, 38), "RB": (21, 31), "WR": (21, 33), "TE": (22, 34),
    "OT": (22, 36), "IOL": (22, 36), "EDGE": (21, 34), "DT": (22, 35),
    "LB": (21, 34), "CB": (21, 33), "S": (21, 34), "K": (23, 40),
}

used_names = set()


def unique_name():
    while True:
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        if name not in used_names:
            used_names.add(name)
            return name


def gen_stats(position: str, talent: float, season_factor: float) -> dict:
    """talent in [0,1] roughly maps to player quality; season_factor adds
    year-to-year variance so trajectory can be computed."""
    t = max(0.05, min(1.3, talent * season_factor))
    if position == "QB":
        return {
            "games": random.randint(10, 17),
            "games_started": random.randint(8, 17),
            "pass_yards": round(2400 + 3200 * t),
            "pass_td": round(14 + 28 * t),
            "interceptions": round(max(2, 16 - 10 * t)),
            "completion_pct": round(58 + 12 * t, 1),
            "rush_yards": round(50 + 350 * t * random.random()),
            "epa_per_play": round(-0.05 + 0.30 * t, 3),
        }
    if position == "RB":
        return {
            "games": random.randint(9, 17),
            "games_started": random.randint(4, 17),
            "rush_yards": round(350 + 1250 * t),
            "yards_per_carry": round(3.4 + 1.8 * t, 1),
            "rush_td": round(2 + 12 * t),
            "rec_yards": round(80 + 500 * t * random.random()),
            "receptions": round(10 + 55 * t * random.random()),
            "yards_after_contact_per_att": round(1.5 + 2.2 * t, 1),
        }
    if position == "WR":
        return {
            "games": random.randint(9, 17),
            "games_started": random.randint(3, 17),
            "receptions": round(25 + 90 * t),
            "targets": round(40 + 130 * t),
            "rec_yards": round(300 + 1200 * t),
            "rec_td": round(1 + 10 * t),
            "yards_per_reception": round(9.5 + 6.5 * t, 1),
        }
    if position == "TE":
        return {
            "games": random.randint(9, 17),
            "games_started": random.randint(3, 17),
            "receptions": round(15 + 65 * t),
            "targets": round(25 + 90 * t),
            "rec_yards": round(150 + 750 * t),
            "rec_td": round(1 + 7 * t),
            "yards_per_reception": round(8.5 + 5.5 * t, 1),
        }
    if position in ("OT", "IOL"):
        games = random.randint(8, 17)
        return {
            "games": games,
            "games_started": round(games * min(1.0, 0.5 + 0.5 * t)),
        }
    if position == "EDGE":
        return {
            "games": random.randint(9, 17),
            "games_started": random.randint(3, 17),
            "sacks": round(2 + 10 * t, 1),
            "tackles_for_loss": round(3 + 12 * t),
            "qb_hits": round(5 + 20 * t),
            "forced_fumbles": round(0 + 3 * t),
            "tackles": round(15 + 45 * t),
        }
    if position == "DT":
        return {
            "games": random.randint(9, 17),
            "games_started": random.randint(3, 17),
            "sacks": round(1 + 6 * t, 1),
            "tackles_for_loss": round(2 + 10 * t),
            "tackles": round(20 + 50 * t),
            "qb_hits": round(3 + 12 * t),
        }
    if position == "LB":
        return {
            "games": random.randint(9, 17),
            "games_started": random.randint(3, 17),
            "tackles": round(40 + 95 * t),
            "tackles_for_loss": round(2 + 9 * t),
            "sacks": round(0 + 4 * t, 1),
            "interceptions": round(0 + 2 * t * random.random()),
            "passes_defended": round(1 + 6 * t),
        }
    if position == "CB":
        return {
            "games": random.randint(9, 17),
            "games_started": random.randint(3, 17),
            "interceptions": round(0 + 4 * t * random.random()),
            "passes_defended": round(3 + 12 * t),
            "tackles": round(20 + 55 * t),
            "forced_fumbles": round(0 + 2 * t * random.random()),
        }
    if position == "S":
        return {
            "games": random.randint(9, 17),
            "games_started": random.randint(3, 17),
            "tackles": round(30 + 75 * t),
            "interceptions": round(0 + 3 * t * random.random()),
            "passes_defended": round(2 + 8 * t),
            "forced_fumbles": round(0 + 2 * t * random.random()),
        }
    if position == "K":
        return {
            "games": random.randint(14, 17),
            "games_started": 0,
            "fg_pct": round(0.75 + 0.20 * t, 2),
            "long": round(45 + 15 * t),
            "fg_made": round(18 + 14 * t),
        }
    return {"games": random.randint(10, 17), "games_started": 0}


def gen_contract(position: str, talent: float, age: int):
    position_base_aav = {
        "QB": 28.0, "EDGE": 18.0, "WR": 16.0, "CB": 15.0, "OT": 14.0,
        "DT": 12.0, "S": 10.5, "IOL": 9.5, "LB": 9.0, "TE": 8.5, "RB": 6.5,
        "K": 3.5,
    }
    base = position_base_aav.get(position, 6.0)
    aav = round(base * (0.35 + 1.15 * talent) * random.uniform(0.85, 1.15), 2)
    years_remaining = random.randint(0, 5)
    guaranteed = round(aav * random.uniform(0.3, 0.85) * min(years_remaining, 3), 2)
    cap_hit = round(aav * random.uniform(0.7, 1.3), 2)
    status = "signed"
    if years_remaining == 0:
        status = "expiring"
    return years_remaining, aav, guaranteed, cap_hit, status


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    teams_rows = []
    for i, (name, abbr, conf, div) in enumerate(TEAMS, start=1):
        teams_rows.append({"id": i, "name": name, "abbreviation": abbr, "conference": conf, "division": div})
    teams_df = pd.DataFrame(teams_rows)

    players_rows, stats_rows, contracts_rows = [], [], []
    player_id = 1
    stat_id = 1
    contract_id = 1

    for team in teams_rows:
        for position, count in POSITION_TEMPLATE:
            for _ in range(count):
                talent = random.betavariate(2.2, 2.5)  # skewed distribution of quality
                lo, hi = AGE_RANGE[position]
                age = random.randint(lo, hi)
                name = unique_name()
                players_rows.append(
                    {
                        "id": player_id,
                        "name": name,
                        "position": position,
                        "team_id": team["id"],
                        "age": age,
                        "height_in": random.randint(69, 79),
                        "weight_lb": random.randint(180, 330),
                        "experience": max(0, age - 22),
                        "status": "active",
                    }
                )

                for season, season_factor in ((2025, 1.0), (2024, random.uniform(0.75, 1.1))):
                    stats = gen_stats(position, talent, season_factor)
                    stats_rows.append(
                        {
                            "id": stat_id,
                            "player_id": player_id,
                            "season": season,
                            "games": stats.get("games", 0),
                            "games_started": stats.get("games_started", 0),
                            "stats_json": stats,
                        }
                    )
                    stat_id += 1

                years_remaining, aav, guaranteed, cap_hit, status = gen_contract(position, talent, age)
                contracts_rows.append(
                    {
                        "id": contract_id,
                        "player_id": player_id,
                        "years_remaining": years_remaining,
                        "annual_value": aav,
                        "guaranteed_money": guaranteed,
                        "cap_hit": cap_hit,
                        "contract_status": status,
                    }
                )
                contract_id += 1
                player_id += 1

    players_df = pd.DataFrame(players_rows)
    stats_df = pd.DataFrame(stats_rows)
    contracts_df = pd.DataFrame(contracts_rows)

    # Draft picks: current year (2026, slotted 1-32 per round) + two future
    # years (2027, 2028) with no overall slot yet assigned. A handful of
    # picks are reassigned to a different current_team to simulate pick
    # trading activity that already occurred, feeding the draft-capital
    # dashboard with team-to-team variance.
    draft_rows = []
    pick_id = 1
    for year, slotted in ((2026, True), (2027, False), (2028, False)):
        for round_ in range(1, 8):
            for slot, team in enumerate(teams_rows, start=1):
                overall_pick = (round_ - 1) * 32 + slot if slotted else None
                draft_rows.append(
                    {
                        "id": pick_id,
                        "year": year,
                        "round": round_,
                        "overall_pick": overall_pick,
                        "original_team_id": team["id"],
                        "current_team_id": team["id"],
                    }
                )
                pick_id += 1

    # Simulate ~40 already-completed pick trades by reassigning current_team_id.
    movable = [r for r in draft_rows if r["round"] <= 5]
    for r in random.sample(movable, 40):
        other = random.choice([t for t in teams_rows if t["id"] != r["original_team_id"]])
        r["current_team_id"] = other["id"]

    draft_df = pd.DataFrame(draft_rows)

    teams_df.to_csv(RAW_DIR / "teams.csv", index=False)
    players_df.to_csv(RAW_DIR / "players.csv", index=False)
    stats_df.to_csv(RAW_DIR / "player_stats.csv", index=False)
    contracts_df.to_csv(RAW_DIR / "contracts.csv", index=False)
    draft_df.to_csv(RAW_DIR / "draft_picks.csv", index=False)

    print(f"Generated {len(teams_df)} teams, {len(players_df)} players, "
          f"{len(stats_df)} stat lines, {len(contracts_df)} contracts, "
          f"{len(draft_df)} draft picks -> {RAW_DIR}")


if __name__ == "__main__":
    main()
