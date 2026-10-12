import os
import subprocess
from dotenv import load_dotenv

load_dotenv()
key = os.environ["GEMINI_API_KEY"]

# --cached searches exactly what is staged for the commit
result = subprocess.run(
    ["git", "grep", "--cached", "-l", "-F", key],
    capture_output=True, text=True,
)

print("key length:", len(key))
print("files containing the key:", result.stdout.split() or "none")