import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise SystemExit("GEMINI_API_KEY is not set. Copy .env.example to .env and put your key in it.")

client = genai.Client(api_key=api_key)
print("Models your key can use (put one in GEMINI_MODEL in your .env file):")
for m in client.models.list():
    name = m.name.replace("models/", "")
    if "gemini" in name:
        print(" ", name)