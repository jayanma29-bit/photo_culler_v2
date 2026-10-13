# Photo Culler

![portability](https://github.com/jayanma29-bit/photo_culler_v2/actions/workflows/portability.yml/badge.svg)

Sorts a folder of photos into **kept**, **rejected/low_rated** and **rejected/duplicates**. A Gemini model judges sharpness, exposure, composition and subject clarity. A local perceptual-hash check then finds near-identical shots (like bursts) and keeps only the best one. **Your original photos are never moved, changed or deleted**: the tool only writes copies.

Tested automatically on Windows, macOS and Linux with Python 3.10 and 3.12.

## What you need

- Python 3.10 or newer (https://www.python.org/downloads/)
- A Gemini API key from https://aistudio.google.com/apikey (availability and free-tier rules depend on your country, so check Google's terms)

## Setup: Windows (PowerShell)

```powershell
git clone https://github.com/jayanma29-bit/photo_culler_v2.git
cd photo_culler_v2
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
```

- If activation says "scripts are disabled", run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and activate again.
- In Command Prompt (cmd), activate with `.venv\Scripts\activate.bat` instead.

## Setup: macOS and Linux

```bash
git clone https://github.com/jayanma29-bit/photo_culler_v2.git
cd photo_culler_v2
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env
```

On Debian or Ubuntu, if `python3 -m venv` fails, run `sudo apt install python3-venv` first.

In `.env`, replace `your_key_here` with your API key and save. Never share or commit this file.

## Usage

```
python -m src.main --input "path/to/your/photos"
```

Results appear in `output/`:

```
output/
  kept/                 the best photos
  rejected/low_rated/   judged blurry, dark, badly composed, etc.
  rejected/duplicates/  fine photos, but a better copy is in kept/
  report.csv            every photo with status, score and reason
```

| Option | Meaning |
|---|---|
| `--input PATH` | Folder with your photos (default `test_photos`) |
| `--output PATH` | Where sorted copies are written (default `output`) |
| `--dry-run` | Print decisions without writing sorted folders or the report |
| `--threshold N` | Duplicate sensitivity. Lower = stricter (default 6) |
| `--rejudge` | Ignore saved results and ask the AI again |
| `--results PATH` | Cache file for AI judgments (default `results.json`) |

Supported types: `.jpg`, `.jpeg`, `.png`, `.webp`, and `.heic`/`.heif` (iPhone/Mac photos, when `pillow-heif` installs). Only the top level of the input folder is scanned.

Judgments are cached by filename, so reruns are instant and free. If you scan two different folders that contain files with the same name, give each its own `--results` file.

## Privacy and cost

Each photo is shrunk and **uploaded to Google's Gemini API** for judging. Only use photos you are comfortable sending to a third party. API usage is subject to your key's limits and pricing. Failed calls are retried automatically.

## Troubleshooting

| Message | Fix |
|---|---|
| `GEMINI_API_KEY is not set` | Create `.env` from `.env.example` and add your key. Run from the project folder. |
| `Model '...' was not found` | Run `python -m src.list_models`, then set `GEMINI_MODEL=<a listed model>` in `.env`. |
| `Your GEMINI_API_KEY was rejected` | Check for a typo, quotes, or spaces in `.env`. |
| `Found 0 photos` | Check the folder path and file types. Subfolders are not scanned. |

## Measuring accuracy

Create a label sheet with `python -m src.evaluate --template`, fill the `keep` column yourself (1 = keep, 0 = reject), then run `python -m src.evaluate` for accuracy, keep recall and keep precision, plus every photo where the AI and you disagree.

## Results

(Fill in after running the evaluation: your accuracy and recall, what failed, and how you fixed it.)

## How it works

1. Each photo is corrected for rotation, shrunk to at most 1024 px, and sent to Gemini, which returns a keep/reject decision, a 1-10 score and a reason.
2. Photos judged "keep" are fingerprinted locally with a perceptual hash. Near-identical photos are grouped, and only the highest-scoring one in each group is kept.
3. Copies are sorted into folders and a CSV report is written.

## Limitations

- Each photo is judged on its own; the AI never compares two shots directly.
- Duplicate sensitivity is a tunable guess, so adjust `--threshold` for your photos.
- RAW files are not supported.