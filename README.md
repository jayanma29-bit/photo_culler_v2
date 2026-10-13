# Photo Culler

![portability](https://github.com/jayanma29-bit/photo_culler_v2/actions/workflows/portability.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%20%7C%203.12%20%7C%203.14-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

Sort a messy folder of photos into the ones worth keeping, the ones that are not, and the extra copies, using AI and image hashing.

## Contents

- [Description](#description)
- [Setup](#setup)
- [Usage](#usage)
- [Understanding the output](#understanding-the-output)
- [Safety and privacy](#safety-and-privacy)
- [Troubleshooting](#troubleshooting)
- [Project files](#project-files)
- [Future updates](#future-updates)
- [Results](#results)
- [License](#license)

## Description

After a shoot, trip or event you often end up with hundreds of photos: some blurry, some badly exposed, and lots of near-identical burst shots. Photo Culler does the first pass of sorting for you.

**How it works**

1. **AI judging.** A Gemini model looks at each photo and rates sharpness/focus, exposure, composition and subject clarity. It returns a keep/reject decision, a 1-10 score and a one-sentence reason.
2. **Duplicate detection.** Among the photos the AI wanted to keep, a local perceptual hash finds near-identical shots. Only the highest-scoring photo in each group is kept.
3. **Sorted copies and a report.** Your photos are copied into `kept`, `low_rated` and `duplicates` folders, and `report.csv` explains every decision.

**Your original photos are never modified.** The tool only reads your input folder and writes copies to a separate output folder.

**Good to know:** judgments are cached in `results.json`, so rerunning on the same photos is free and instant, and an interrupted run continues where it stopped. One bad photo never stops a run; it is printed as an `ERROR` line and skipped.

## Setup

**You need:**

- Python 3.10 or newer ([python.org/downloads](https://www.python.org/downloads/))
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey). Availability, limits and pricing depend on your country and change over time, so check Google's current terms.

**Windows (PowerShell)**

```powershell
git clone https://github.com/jayanma29-bit/photo_culler_v2.git
cd photo_culler_v2
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
```

**macOS / Linux**

```bash
git clone https://github.com/jayanma29-bit/photo_culler_v2.git
cd photo_culler_v2
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env
```

Then:

1. In `.env`, replace `your_key_here` with your API key and save.
2. Check the install: `python -m src.main --help` should print the options list.
3. Keep your venv active. Your prompt should start with `(.venv)` every time you run the tool.

No git? Use **Code > Download ZIP** on the repository page and open a terminal in the unzipped folder. On Windows, if activation says "scripts are disabled", run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and activate again.

## Usage

Run from the project folder. Start with a dry run, which prints every decision and writes nothing:

```
python -m src.main --input "path/to/photos" --dry-run
python -m src.main --input "path/to/photos"
```

| Option | Meaning |
|---|---|
| `--input PATH` | Folder with your photos (default `test_photos`) |
| `--output PATH` | Where sorted copies and the report go (default `output`) |
| `--dry-run` | Print decisions, write no folders or report (new photos still use API calls) |
| `--threshold N` | Duplicate sensitivity: lower is stricter, higher groups more (default 6) |
| `--rejudge` | Ignore saved judgments and ask the AI again |
| `--results PATH` | Judgment cache file (default `results.json`) |

Supported types: `.jpg`, `.jpeg`, `.png`, `.webp`, and iPhone `.heic`. Only the top level of the input folder is scanned. Optionally set `GEMINI_MODEL` in `.env` to use a different model.

## Understanding the output

```
output/
  kept/                 the best photos
  rejected/low_rated/   blurry, dark, badly composed
  rejected/duplicates/  fine, but a better copy is in kept/
  report.csv            filename, status, score, reason, duplicate_of
```

The run ends with a summary line such as `Done. kept=12 low_rated=5 duplicates=3 errors=0 cached=20`. If `errors` is above 0, some photos failed; rerun the same command and only those are retried.

To measure how well the AI agrees with you, run `python -m src.evaluate --template`, fill in the `keep` column of `labels.csv` (1 or 0), then run `python -m src.evaluate`.

## Safety and privacy

- Inputs are only read, never changed. The `kept/` and `rejected/` folders inside the output folder are rebuilt every run, so use a dedicated output folder. The tool refuses to delete folders it did not create.
- Photos are resized to 1024 px and **sent to Google's Gemini API** for judging. Only use photos you are comfortable sharing with a third party.
- Your API key lives only in `.env`, which git ignores. Never paste it in code, chats or screenshots. If it leaks, delete it in Google AI Studio and make a new one.
- `results.json` stores your filenames and the AI's reasons. Do not publish it if your filenames are private.

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` | The venv is not active. Activate it and run `pip install -r requirements.txt`. |
| `GEMINI_API_KEY is not set` or `was rejected` | Check that `.env` exists, contains your key with no extra spaces, and that you run from the project folder. |
| `Model '...' was not found` | Run `python -m src.list_models`, then set `GEMINI_MODEL=<model>` in `.env`. |
| `ERROR` lines with 429 or quota | You hit a rate limit. Wait and rerun; finished photos are cached. |
| `ERROR ... cannot identify image file` | The file is corrupt or not a real image. It is skipped. |
| `Found 0 photos` | Check the path and file types. Subfolders are not scanned. |
| `Refusing to overwrite ...` | Choose a different `--output` folder. |
| `PermissionError` on `report.csv` | Close the file in Excel and rerun. |
| Wrong duplicate grouping | Lower `--threshold` to group less, raise it to group more. |
| `Failed building wheel for pillow-heif` | No HEIC package for your Python yet. Remove that line from `requirements.txt`; everything else still works. |

Still stuck? Open a GitHub issue with your OS, `python --version`, the command you ran, and the last 10 lines of output. Never include your API key.

## Project files

| File | What it does |
|---|---|
| `src/main.py` | The CLI: loops over photos, groups duplicates, sorts copies, writes the report |
| `src/judge.py` | Gemini API call, prompt, retries, friendly API errors |
| `src/evaluate.py` | Compares the AI's decisions to your own labels |
| `src/list_models.py` | Lists the Gemini models your key can use |
| `tests/` | Automated tests (fake judge, no API key needed) |
| `.github/workflows/portability.yml` | CI on Windows, macOS and Linux with Python 3.10, 3.12, 3.14 |
| `requirements.txt` | The 8 direct dependencies |
| `.env.example` | Template for your private `.env` |

Run the tests with `pip install pytest`, then `python -m pytest -q`.

## Future updates

Planned ideas, nothing here is built yet.

**Error codes and handling**
- [ ] Distinct exit codes (bad config, bad folder, some photos failed, quota hit). Today a run with failed photos still exits with code 0.
- [ ] A failed-photos summary at the end of a run, plus an optional `--log` file
- [ ] Smarter retries that skip errors that can never succeed, and a `--check` command that verifies setup before a long run

**User interface**
- [ ] A local web UI: pick a folder, watch progress, see a thumbnail gallery with scores and reasons
- [ ] Manual override (move a photo between kept, low-rated and duplicates) and a side-by-side duplicate viewer
- [ ] A packaged desktop app so no terminal is needed

**Speed and cost**
- [ ] Progress bar, parallel judging, and a cost estimate before any API calls
- [ ] A cache keyed by file contents instead of filename

**Smarter culling**
- [ ] Compare shots in a duplicate group directly, and detect closed eyes
- [ ] Custom criteria such as "I care most about sharp eyes"
- [ ] An offline option using a local vision model

**More formats and packaging**
- [ ] RAW files, recursive subfolder scanning, and an HTML report with thumbnails
- [ ] `pip install photo-culler` and a Docker image

## Results

(Add your measured accuracy, keep recall and keep precision from `python -m src.evaluate`, and how many photos you tested.)

## License

MIT. See `LICENSE`.