import sqlite3

connection = sqlite3.connect("pitchvision.db")

# Facts are stored per match (home + away), tagged with which team they are
# about, plus a timestamp - so the app remembers context across queries.
connection.execute(
    "CREATE TABLE IF NOT EXISTS facts (id INTEGER PRIMARY KEY, home TEXT, away TEXT, team TEXT, category TEXT, text TEXT, created TEXT)"
)
connection.execute(
    "CREATE TABLE IF NOT EXISTS reports (id INTEGER PRIMARY KEY, home TEXT, away TEXT, scoreline TEXT, body TEXT, created TEXT)"
)

connection.execute("DELETE FROM facts")
connection.execute("DELETE FROM reports")
connection.commit()


def add_fact(home, away, team, category, text):
    connection.execute(
        "INSERT INTO facts (home, away, team, category, text, created) VALUES (?, ?, ?, ?, ?, datetime('now'))",
        (home, away, team, category, text),
    )
    connection.commit()


def get_facts(home, away):
    return connection.execute(
        "SELECT team, category, text, created FROM facts WHERE home = ? AND away = ? ORDER BY id",
        (home, away),
    ).fetchall()


def save_report(home, away, scoreline, body):
    connection.execute(
        "INSERT INTO reports (home, away, scoreline, body, created) VALUES (?, ?, ?, ?, datetime('now'))",
        (home, away, scoreline, body),
    )
    connection.commit()


def get_reports(team):
    return connection.execute(
        "SELECT home, away, scoreline, created FROM reports WHERE home = ? OR away = ? ORDER BY id DESC",
        (team, team),
    ).fetchall()
