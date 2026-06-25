import sqlite3

import db
import mock_data
from predict import predictScore


def fresh_db():
    # Use an in-memory database so tests never touch pitchvision.db.
    db.connection = sqlite3.connect(":memory:")
    db.connection.execute(
        "CREATE TABLE facts (id INTEGER PRIMARY KEY, home TEXT, away TEXT, team TEXT, category TEXT, text TEXT, created TEXT)"
    )
    db.connection.execute(
        "CREATE TABLE reports (id INTEGER PRIMARY KEY, home TEXT, away TEXT, scoreline TEXT, body TEXT, created TEXT)"
    )
    db.connection.commit()


def test_add_fact():
    fresh_db()
    db.add_fact("Spain", "Brazil", "Spain", "Injury", "Striker injured")
    facts = db.get_facts("Spain", "Brazil")
    assert len(facts) == 1
    assert facts[0][0] == "Spain"       # team the fact is about
    assert facts[0][1] == "Injury"      # category
    assert facts[0][2] == "Striker injured"


def test_save_report():
    fresh_db()
    db.save_report("Spain", "Brazil", "Spain 1-2 Brazil", "report body")
    reports = db.get_reports("Brazil")
    assert len(reports) == 1
    assert reports[0][2] == "Spain 1-2 Brazil"


def test_predict_score():
    # A negative factor (injury, 0.88) should lower the score.
    assert predictScore(3.0, ["Injury"]) <= predictScore(3.0, [])
    # The score is always clamped to 0-4.
    assert predictScore(99, []) == 4
    assert predictScore(-5, []) == 0


def test_mock_strength():
    # A known team has a real strength; an unknown one falls back to 1.0.
    assert mock_data.mockStrength("Spain") > 0
    assert mock_data.mockStrength("Narnia") == 1.0
