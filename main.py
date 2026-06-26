import requests
import os
import sys
from datetime import datetime
from google import genai
from google.genai import types
from dotenv import load_dotenv
from functools import lru_cache

import db
import mock_data
from predict import predictScore

## Setting up Gemini API
load_dotenv()

api_key = os.environ["GENAI_KEY"]

client = genai.Client(api_key=api_key)


## Setting up World Cup API

wc_token = os.environ["WC_TOKEN"]
headers = {"Authorization": f"Bearer {wc_token}"}

## Setting up API-Football (an API that uses authorization via a key)
football_headers = {"x-apisports-key": os.environ["FOOTBALL_KEY"]}

@lru_cache
def get_team_info(team):
    try:
        response = requests.get(
            "https://v3.football.api-sports.io/teams",
            headers=football_headers,
            params={"search": team},
            timeout=20,
        )
        info = response.json()["response"][0]["team"]
        return f"{info['name']} (founded {info['founded']}, {info['country']})"
    except Exception:
        return ""

# If the World Cup API is unreachable, fall back to offline demo mode
# instead of crashing on startup.
try:
    games = requests.get("https://worldcup26.ir/get/games", headers=headers, timeout=15).json()["games"]
    teams = requests.get("https://worldcup26.ir/get/teams", headers=headers, timeout=15).json()["teams"]
    stadiums = requests.get("https://worldcup26.ir/get/stadiums", headers=headers, timeout=15).json()["stadiums"]
except Exception:
    print("Could not reach the World Cup API - running in offline demo mode.")
    games, teams, stadiums = [], [], []

valid_teams = set()

LOGO = """
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠺⡶⠛⡿⢿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣠⣴⠶⠞⠛⠻⣍⡑⠒⠦⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⡄⠀⡄⢣⡀⠀⠈⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⣠⠎⡽⠁⠀⢀⣠⡶⠋⠉⠓⠲⠬⣯⡷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀⢙⡵⠀⢀⣵⠴⠞⢉⣹⡏⠉⠐⠒⢦⡀⠀⠀⠀⠀⠀⠀
⢀⡜⣡⠞⠙⠒⠒⣽⠉⠀⠀⠀⠀⠀⠀⢳⠀⠈⢧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣞⠏⣼⣥⡴⠖⠋⠛⠯⠭⠟⠋⠀⠀⠀⣀⠀⢹⣦⡄⠀⠀⠀⠀
⡜⣴⠁⠀⠀⠀⠀⢹⣇⠀⠀⠀⠀⠀⠀⣨⣶⣄⠀⢧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣜⠎⢸⡟⠁⠀⠀⠀⣄⠀⠀⠀⠀⠀⠀⠸⣯⠓⠿⣍⠛⣆⠀⠀⠀
⠁⣾⠀⠀⠀⠀⢀⣾⠟⠛⠲⠦⡄⣴⠋⠁⠀⠉⠻⡎⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣟⢀⣸⠓⠛⠛⠛⠒⢿⣤⡀⠀⠀⠀⠀⠀⢻⡆⠀⠈⡓⡌⢧⡀⠀
⠀⢹⣧⣄⣀⣠⡾⠁⠀⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⡇⠈⠳⢄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠀⠀⠀⠀⠀⠀⠀⠸⣇⠀⠀⠀⠀⠀⠀⠹⡀⠀⠃⢷⠦⣙⡄
⡆⢠⠇⠀⠀⠈⠳⣄⠀⠀⠀⠀⢀⣿⣀⠀⠀⠀⣠⡇⡴⠒⠒⠛⠀⣤⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣦⣤⡤⠴⠶⠶⠶⣷⡄⠂⠀⠀⠈⠀
⠹⣾⣆⠀⠀⠀⠀⠈⢣⠴⠒⠋⠉⠈⠙⢗⡤⠚⠁⣿⡁⠀⠀⠀⠀⠀⠈⠉⠛⠫⠵⣒⡒⠤⢤⣀⣀⠀⠈⢯⢦⣧⡀⠀⠀⠀⠀⠀⢠⠟⠁⠀⢷⠀⠀⠀⠀⢹⣹⠆⠀⠀⠀⠀
⠀⠹⣽⣦⡀⠀⠀⢠⠏⠀⠀⠀⠀⠀⢀⡞⠀⡰⠃⠀⠉⠙⠛⠳⠶⢖⣢⣤⠤⢀⣀⣀⡈⠉⠒⠢⢬⣉⡉⠚⠇⠻⠟⢦⡀⠀⠀⣴⣧⣤⡀⠀⢸⢀⣀⣀⣰⠟⠁⠀⠀⠀⠀⠀
⠀⠀⠈⠻⣝⡒⠒⠾⣦⣄⣀⣀⣀⣀⡸⠶⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠑⠒⠢⠭⢍⣉⡒⠒⠲⠭⠷⠦⠄⠂⠀⢙⣶⠞⠉⠉⠹⣷⡖⠻⣾⡷⣼⠁⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠉⠑⠒⠒⠚⠳⠦⠤⠤⠤⣤⣤⣤⣤⡤⠤⠤⠤⢀⣀⣀⣀⣀⣀⣀⡀⠀⣠⠤⠤⠭⠍⢓⣂⠀⢀⣀⡤⠴⠋⠉⠀⢀⣠⠖⣿⠲⢿⡟⠃⡇⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠉⠉⠛⠒⠒⠒⠢⠤⠤⠭⠭⢝⣯⡓⠒⣾⣿⣄⣉⠉⠋⠻⢷⣠⠔⠚⠉⠀⠀⣿⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⢿⡻⢿⣽⣛⡷⡶⢬⣇⠀⠀⠀⠀⠀⠻⣟⠛⠻⣿⠓⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠓⠤⣀⡙⠳⠶⠛⠀⠀⠀⠀⠀⠀⠹⣧⠀⠈⠳⣄⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠓⠦⢄⡀⠀⠀⠀⠀⠀⠀⠈⠳⡀⠀⠙⣆⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠑⠢⢄⡀⠀⠀⠀⠀⠈⠢⡀⢹⣻⢿⡀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠑⠢⣄⡀⠀⠀⠘⣾⡇⢸⡇⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⣆⠀⠀⠸⡄⢸⡇⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡞⠀⠀⠀⠙⠷⠃⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
      
██████╗ ██╗████████╗ ██████╗██╗  ██╗
██╔══██╗██║╚══██╔══╝██╔════╝██║  ██║
██████╔╝██║   ██║   ██║     ███████║
██╔═══╝ ██║   ██║   ██║     ██╔══██║
██║     ██║   ██║   ╚██████╗██║  ██║
╚═╝     ╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝

██╗   ██╗██╗███████╗██╗ ██████╗ ███╗  ██╗
██║   ██║██║██╔════╝██║██╔═══██╗████╗ ██║
╚██╗ ██╔╝██║███████╗██║██║   ██║██╔██╗██║
 ╚████╔╝ ██║╚════██║██║██║   ██║██║╚████║
  ╚██╔╝  ██║███████║██║╚██████╔╝██║ ╚███║
   ╚═╝   ╚═╝╚══════╝╚═╝ ╚═════╝╚═╝  ╚══╝
World Cup 2026
            """

# Make sure the Unicode logo prints on Windows consoles (cp1252 would crash).
sys.stdout.reconfigure(encoding="utf-8")

for line in LOGO.split("\n"):
    print(line.center(80))

for team in teams:
    valid_teams.add(team["name_en"].lower())

# Offline fallback: if the API gave us no teams, accept the mock-data teams.
if not valid_teams:
    valid_teams = {name.lower() for name in mock_data.MOCK_STATS}

def analyze_match(home, away, match_info):
    facts = db.get_facts(home, away)
    # Stats fall back on mock data, so this still works with no live game.
    home_factors = [category for team, category, text, created in facts if team == home]
    away_factors = [category for team, category, text, created in facts if team == away]

    home_goals = predictScore(mock_data.mockStrength(home), home_factors)
    away_goals = predictScore(mock_data.mockStrength(away), away_factors)

    scoreline = f"{home} {home_goals}-{away_goals} {away}"

    # Human intelligence the official API is missing, remembered per match.
    fact_lines = [f"{team} - {category}: {text}" for team, category, text, created in facts]

    # Background on each team from API-Football (authorized API).
    team_background = f"{get_team_info(home)}; {get_team_info(away)}"

    try:
        interaction = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=(
                f"Match info: {match_info}. "
                f"Team background: {team_background}. "
                f"Our model predicts {scoreline}. "
                f"User-submitted facts the official data is missing: {fact_lines}. "
                "Give the most likely result with a probability for each outcome. "
                "Use the user facts to adjust your analysis. Focus on the current squad, "
                "not storied legacies. Account for home advantage justly. Keep it brief. " \
                "Focus on making it pleasant to look at for a cli interface. No emojis." \
                "Give a short description as to why"
            ),
        )
        report = interaction.text
    except Exception as error:
        report = f"(AI analysis unavailable right now: {error})"

    
    print(f"\nModel prediction: {scoreline}")

    print(report)
    db.save_report(home, away, scoreline, report)

    # Let the user add intel that will be remembered next time.
    note = input("\nAdd match intel? (press Enter to skip): ").strip()
    if note:
        which = input(f"Which team is this about? ({home}/{away}): ").strip().title()
        category = input("Category (Injury/Suspension/Weather/Morale/Manager): ").strip().title()
        db.add_fact(home, away, which, category, note)
        print("Saved - it will be remembered next time you analyze this match.")


## Ask user for team name -> checks if team is playing -> returns Gemini-powered output
while True:

    team = input("What team are you looking for? type quit or exit to leave: ").lower().strip()

    if team == "quit" or team == "exit":
        print("Thank you so much for trying out our app! :)")
        break

    elif team not in valid_teams:
        print(f"{team} is not a World Cup team, check your spelling and try again")
        continue

    print(team)

    today = datetime.now().strftime("%m/%d/%Y")
    todays_game = None

    for game in games:
        home = game.get("home_team_name_en", "").lower()
        away = game.get("away_team_name_en", "").lower()

        if team == home or team == away:
            if game.get("local_date", "").startswith(today):
                todays_game = game
                break

    if todays_game:
        home = todays_game.get("home_team_name_en")
        away = todays_game.get("away_team_name_en")
        home_score = todays_game.get("home_score")
        away_score = todays_game.get("away_score")
        status = todays_game.get("time_elapsed")

        match_stadium = None
        stadium_city = stadium_country = None
        for stadium in stadiums:
            if stadium["id"] == todays_game["stadium_id"]:
                match_stadium = stadium["name_en"]
                stadium_city = stadium["city_en"]
                stadium_country = stadium["country_en"]

        match_info = (f"{home} vs {away} | Score: {home_score}-{away_score} | Status: {status}"
                      f"| Stadium: {match_stadium} | City: {stadium_city} | Country: {stadium_country}")

        analyze_match(home, away, match_info)

    else:
        # No match today -> run a mock match so the demo still works.
        print(f"{team.title()} has no match today - running a demo match instead.")
        opponent = input("Who are they playing? ").strip().title()
        analyze_match(team.title(), opponent, f"{team.title()} vs {opponent} (demo match)")
