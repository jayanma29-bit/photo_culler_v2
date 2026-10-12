import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

for m in client.models.list():
    name = m.name.replace("models/", "")
    if "flash" in name and "gemini" in name:
        print(name)