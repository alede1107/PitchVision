import sqlite3

connection = sqlite3.connect("pitchvision.db")

connection.execute(
    "CREATE TABLE IF NOT EXISTS facts (id INTEGER PRIMARY KEY, team TEXT, category TEXT, text TEXT)"
)
connection.execute(
    "CREATE TABLE IF NOT EXISTS reports (id INTEGER PRIMARY KEY, home TEXT, away TEXT, scoreline TEXT, body TEXT)"
)
connection.commit()
