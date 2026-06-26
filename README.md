# Pitch Vision

World Cup 2026 match predictor powered by Gemini AI

## What it does

Pitch Vision predicts World Cup match outcomes by combining a local statistcal model with AI analysis. It calculates a scoreline using team form, goal difference, and situational multipliers (injuries, suspensions, morale, etc.), then sends that context to Google Gemini for a natural-language report with win/draw/loss probabilities. Users can submit match intel during a session and it will influence predictions for that matchup going forward.

## Data sources

- World Cup API -- match schedules, live scores, stadiums
- API-Football -- team background (name, country, founding year)
- Google Gemini 2.5 Flash -- AI-powered match analysis

## Setup

create a .env file with:

GENAI_KEY=your-gemini-api-key
WC_TOKEN=your-worldcup-api-token
FOOTBALL_KEY=your-api-football-key

Then:

pip install -r requirements.txt
python main.py

## How it works

1. Enter a World Cup team name
2. If the team has a match today, it pulls live data; otherwise it runs a demo match
3. The local model predicts a scoreline based on team strength and any intel you've added
4. Gemini receives the prediction, team background, and user-submitted facts, then returns a full analysis
5. You can add match intel (Injury, Suspension, Weather, Morale, Manager) that adjusts future predictions within the session