import os
import json
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image, ImageOps

# Optional support for iPhone/Mac HEIC photos. Everything still works without it.
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    HEIC_SUPPORTED = True
except ImportError:
    HEIC_SUPPORTED = False

load_dotenv()

MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

PROMPT = """
You are a strict photo editor culling a batch of photos. Judge this photo on sharpness/focus, exposure, composition, and whether the subject is clear (easily visible, nothing awkwardly cut off).

Respond with ONLY a JSON object with these keys:
    "keep": true or false
    "score": integer 1-10 (10 = excellent)
    "reason": one short sentence explaining your decision

"""

_client = None


def get_client():
    """Create the API client on first use, so --help and cached runs work without a key."""
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise SystemExit(
                "GEMINI_API_KEY is not set. Copy .env.example to .env and put your key in it."
            )
        _client = genai.Client(api_key=api_key)
    return _client


def judge_photo(path, retries=3):
    """Send a photo to Gemini and return {"keep": bool, "score": int, "reason": str}."""
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)
    img = img.convert("RGB")
    img.thumbnail((1024, 1024))

    client = get_client()
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
            keep = data["keep"]
            if isinstance(keep, str):
                keep = keep.strip().lower() == "true"
            return {
                "keep": bool(keep),
                "score": int(data["score"]),
                "reason": str(data["reason"]),
            }
        except Exception as e:
            last_error = e
            text = str(e).lower()
            if "404" in text or "not found" in text:
                raise SystemExit(
                    f"Model '{MODEL}' was not found for your API key. "
                    "Run `python -m src.list_models` to see which models you can use, "
                    "then set GEMINI_MODEL in your .env file."
                )
            if "api key" in text and ("invalid" in text or "not valid" in text):
                raise SystemExit("Your GEMINI_API_KEY was rejected. Check the key in your .env file.")
            time.sleep(2 ** attempt)

    raise last_error