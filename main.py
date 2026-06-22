import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ["GENAI_KEY"]

client = genai.Client(api_key=api_key)

interaction = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain how AI works in a few words"

)
print(interaction.text)
