import requests
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

## Setting up Gemini API
load_dotenv()

api_key = os.environ["GENAI_KEY"]

client = genai.Client(api_key=api_key)

'''
interaction = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain how AI works in a few words"
)
'''
#print(interaction.text)

## Setting up World Cup API

wc_token = os.environ["WC_TOKEN"]
headers = {"Authorization": f"Bearer {wc_token}"}

response = requests.get("https://worldcup26.ir/get/games", headers=headers)

games = response.json()["games"]

## Ask user for team name -> checks if team is playing -> returns Gemini-powered output

team = input("What team are you looking for? ").lower().strip()

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
      "What is the highest probability of the match result?")
)

else:
  print(f"{team.title()} is not playing right now")

