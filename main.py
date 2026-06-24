import requests
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

## Setting up Gemini API
load_dotenv()

api_key = os.environ["GENAI_KEY"]

client = genai.Client(api_key=api_key)

interaction = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain how AI works in a few words"
)
print(interaction.text)

## Setting up World Cup API

wc_token = os.environ["WC_TOKEN"]
headers = {"Authorization": f"Bearer {wc_token}"}

response = requests.get("https://worldcup26.ir/get/teams", headers=headers)

print(response.json())

## Set up SQL database -- Stores queries from user

## Ask user for team name -> checks if team is playing -> returns Gemini-powered output
