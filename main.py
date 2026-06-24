import requests
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

## Setting up Gemini API
load_dotenv()

api_key = os.environ["GENAI_KEY"]

client = genai.Client(api_key=api_key)


## Setting up World Cup API

wc_token = os.environ["WC_TOKEN"]
headers = {"Authorization": f"Bearer {wc_token}"}

response_games = requests.get("https://worldcup26.ir/get/games", headers=headers)
response_teams = requests.get("https://worldcup26.ir/get/teams", headers=headers)

games = response_games.json()["games"]
teams = response_teams.json()["teams"]

valid_teams = set()

for team in teams:
    valid_teams.add(team["name_en"].lower())

## Ask user for team name -> checks if team is playing -> returns Gemini-powered output
while True:

    team = input("What team are you looking for? type quit or exit to leave: ").lower().strip()

    if team == "quit" or team == "exit":
        print("Thank you so much for trying out our app! :)")
        break

    elif team not in teams:
        print(f"{team} is not a World Cup team, check your spelling and try again")
        continue

    print(team)

    live_game = None


    for game in games:
        home = game.get("home_team_name_en", "").lower()
        away = game.get("away_team_name_en", "").lower()

        if team == home or team == away:
            if game.get("time_elapsed") == "live":
                live_game = game
                break

    if live_game:
        home = live_game.get("home_team_name_en")
        away = live_game.get("away_team_name_en")
        home_score = live_game.get("home_score")
        away_score = live_game.get("away_score")
        time_elapsed = live_game.get("time_elapsed")

        match_info = f"{home} vs {away} | Score: {home_score}-{away_score} | Time: {time_elapsed}"

        interaction = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=(
            f"There is a game currently going on. Here is the match info: {match_info}. "
            "What is the highest probability of the match result? "
            "You are allowed to use external knowledge but focus on the current squad. Don't worry so look so much into storied legacies" \
            "to improve your decision-making. Include a probability score for each result. Keep it brief.")
            )
        print(interaction.text)
        
    else:
        print(f"{team.title()} is not playing right now")






