import os
import json
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image, ImageOps

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")


PROMPT = """
You are a strict photo editor culling a batch of photos. Judge this photo on sharpness/focus, exposure, composition, and whether the subject is clear (easily visible, nothing awkwardly cut off).

Respond with ONLY a JSON object with these keys:
    "keep": true or false
    "score": integer 1-10 (10 = excellent)
    "reason": one short sentence explaining your decision

"""


def judge_photo(path, retries=3):
    """Send a photo to Gemini and return a dict with keys: keep, score, reason, ie {"keep": bool, "score": int, "reason": str}"""

    img = Image.open(path)
    img = ImageOps.exif_transpose(img)
    img = img.convert("RGB")
    img.thumbnail((1024, 1024))

    last_error = None

    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=[img, PROMPT],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                ),
            )
            data = json.loads(response.text)
            return {
                "keep": data["keep"],
                "score": data["score"],
                "reason": data["reason"],
            }
        except Exception as e:
            last_error = e
            time.sleep(2 ** attempt)

    raise last_error