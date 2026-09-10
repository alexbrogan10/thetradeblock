import os

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg2://tradeblock:tradeblock@localhost:5432/tradeblock_test",
)

import pytest  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.database.base import Base  # noqa: E402
from app.database.session import get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models.contract import Contract  # noqa: E402
from app.models.draft_pick import DraftPick  # noqa: E402
from app.models.player import Player  # noqa: E402
from app.models.player_statistic import PlayerStatistic  # noqa: E402
from app.models.team import Team  # noqa: E402
import app.models as _all_models  # noqa: E402,F401  (registers every model on Base.metadata)

TEST_DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def _create_schema():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def clean_between_tests():
    yield
    session = TestSessionLocal()
    try:
        # Delete in reverse dependency order so FK constraints never block
        # cleanup, no matter which models a given test happened to touch.
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
    finally:
        session.close()


@pytest.fixture
def db_session():
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    from fastapi.testclient import TestClient

    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def make_team(db_session):
    counter = {"n": 0}

    def _make(**kwargs):
        counter["n"] += 1
        defaults = dict(
            name=f"Test Team {counter['n']}",
            abbreviation=f"T{counter['n']}",
            conference="AFC",
            division="East",
        )
        defaults.update(kwargs)
        team = Team(**defaults)
        db_session.add(team)
        db_session.commit()
        db_session.refresh(team)
        return team

    return _make


@pytest.fixture
def make_player(db_session):
    counter = {"n": 0}

    def _make(team, position="WR", age=26, **kwargs):
        counter["n"] += 1
        defaults = dict(
            name=f"Test Player {counter['n']}",
            position=position,
            team_id=team.id if team else None,
            age=age,
            experience=max(0, age - 22),
            status="active",
        )
        defaults.update(kwargs)
        player = Player(**defaults)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        return player

    return _make


@pytest.fixture
def make_contract(db_session):
    def _make(player, **kwargs):
        defaults = dict(
            player_id=player.id,
            years_remaining=3,
            annual_value=10.0,
            guaranteed_money=15.0,
            cap_hit=8.0,
            contract_status="signed",
        )
        defaults.update(kwargs)
        contract = Contract(**defaults)
        db_session.add(contract)
        db_session.commit()
        return contract

    return _make


@pytest.fixture
def make_stats(db_session):
    def _make(player, season=2025, games=17, games_started=17, stats=None):
        stat = PlayerStatistic(
            player_id=player.id,
            season=season,
            games=games,
            games_started=games_started,
            stats=stats or {},
        )
        db_session.add(stat)
        db_session.commit()
        return stat

    return _make


@pytest.fixture
def make_pick(db_session):
    def _make(year, round_, current_team, original_team=None, overall_pick=None):
        pick = DraftPick(
            year=year,
            round=round_,
            overall_pick=overall_pick,
            original_team_id=(original_team or current_team).id,
            current_team_id=current_team.id,
            estimated_value=0.0,
        )
        db_session.add(pick)
        db_session.commit()
        db_session.refresh(pick)
        return pick

    return _make
