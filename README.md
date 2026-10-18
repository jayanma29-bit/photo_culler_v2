# Photo Culler

![portability](https://github.com/jayanma29-bit/photo_culler_v2/actions/workflows/portability.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%20%7C%203.12%20%7C%203.14-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

Sort a messy folder of photos into the ones worth keeping, the ones that are not, and the extra copies, using AI and image hashing.

## What you need

- Windows, macOS or Linux, and an internet connection
- **Python 3.10 or newer.** Check with `python --version` (`python3 --version` on macOS / Linux). Install from [python.org/downloads](https://www.python.org/downloads/) if needed. On Windows, tick **Add python.exe to PATH**.
- **A free Gemini API key** from [aistudio.google.com/apikey](https://aistudio.google.com/apikey) (Google account required). Availability, limits and pricing vary by country, so check Google's current terms.
- **A folder of photos** (`.jpg`, `.jpeg`, `.png`, `.webp`, `.heic`)
- **Git** (optional; there is a ZIP download option)

Setup takes about 10 minutes. Commands go into a terminal: PowerShell on Windows, Terminal on macOS / Linux.

## Contents

- [What you need](#what-you-need)
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
3. **Sorted copies and a report.** Your photos are copied into a `kept` folder and a `rejected` folder (which is split into `low_rated` and `duplicates`), and `report.csv` explains every decision.

**Your original photos are never modified.** The tool only reads your input folder and writes copies to a separate output folder.

**Good to know:** judgments are cached in `results.json`, so rerunning on the same photos is free and instant, and an interrupted run continues where it stopped. One bad photo never stops a run; it is printed as an `ERROR` line and skipped.


### Everyday use (after setup)

Each time you want to sort a new batch of photos:

1. Open a terminal and go to the project folder. **Change the path to yours.**
2. Activate the environment. Your prompt should start with `(.venv)`.
3. Run the program on your photos. **Always include `--input`.** Without it, the program runs on the sample photos again.
4. Open your results folder.

Windows:

```
cd "C:\Users\you\Desktop\photo_culler_v2"
.\.venv\Scripts\Activate.ps1
python -m src.main --input "C:\Users\you\Pictures\Trip" --output "C:\Users\you\Desktop\culled"
```

macOS / Linux:

```
cd ~/Desktop/photo_culler_v2
source .venv/bin/activate
python3 -m src.main --input "/Users/you/Pictures/Trip" --output "/Users/you/Desktop/culled"
```

- Every run rebuilds `kept/` and `rejected/` in the output folder. Copy your results out first, or use a new `--output` folder for each batch.
- Add `--dry-run` to preview decisions without writing any files.
- For a new photos folder, add `--results results_name.json` so old and new verdicts don't mix.


## Setup

Takes about 5 minutes. Open a terminal first: **PowerShell** on Windows, **Terminal** on macOS / Linux.

### 1. Download the project

```
git clone https://github.com/jayanma29-bit/photo_culler_v2.git
cd photo_culler_v2
```

No Git? [Install it](https://git-scm.com/downloads), or on the GitHub page click **Code → Download ZIP**, unzip, and open a terminal inside the unzipped folder.

### 2. Install

**Windows:**
```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**macOS / Linux:**
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Your prompt should now start with `(.venv)`.

### 3. Add your API key

**Windows:**
```
Copy-Item .env.example .env
notepad .env
```

**macOS / Linux:**
```
cp .env.example .env
nano .env
```

Replace `your_key_here` with your key (`GEMINI_API_KEY=AIza...`), then save. No quotes, no spaces around `=`. Never share this file.

The folder should look like this: 

```
photo_culler_v2/
├── .github/
├── src/                 (the program: main.py, judge.py, ...)
├── tests/
├── sample_photos/       (example photos you can try first)
├── .env.example         (template for your settings)
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

### 4. Run it

Try the sample photos first:

```
python -m src.main --input sample_photos
```

(Use `python3` on macOS / Linux.) Then open the `output` folder. You should see `kept/`, `rejected/` and `report.csv`.

**Now your own photos:**

```
python -m src.main --input "C:\Users\you\Pictures\Trip" --output "C:\Users\you\Desktop\culled"
```

On macOS / Linux the paths look like `/Users/you/Pictures/Trip`. Tip: add `--dry-run` to preview decisions without writing any files.


### Everyday use (after setup)

Each time you want to sort a new batch of photos:

1. Open a terminal and go to the project folder. **Change the path to yours.**
2. Activate the environment. Your prompt should start with `(.venv)`.
3. Run the program on your photos. **Always include `--input`.** Without it, the program runs on the sample photos again.
4. Open your results folder.

Windows:

```
cd "C:\Users\you\Desktop\photo_culler_v2"
.\.venv\Scripts\Activate.ps1
python -m src.main --input "C:\Users\you\Pictures\Trip" --output "C:\Users\you\Desktop\culled"
```

macOS / Linux:

```
cd ~/Desktop/photo_culler_v2
source .venv/bin/activate
python3 -m src.main --input "/Users/you/Pictures/Trip" --output "/Users/you/Desktop/culled"
```

- Every run rebuilds `kept/` and `rejected/` in the output folder. Copy your results out first, or use a new `--output` folder for each batch.
- Add `--dry-run` to preview decisions without writing any files.
- For a new photos folder, add `--results results_name.json` so old and new verdicts don't mix.


**Something went wrong?** See [Troubleshooting](#troubleshooting). Still stuck? Open a GitHub issue and I'll get back to you as soon as I can.













## Usage

Run from the project folder with the venv active. Start with a dry run, which prints every decision and writes nothing:

```
python -m src.main --input "path/to/photos" --dry-run
python -m src.main --input "path/to/photos"
```

(Use `python3` instead of `python` on macOS / Linux.)

| Option | Meaning |
|---|---|
| `--input PATH` | Folder with your photos (default `sample_photos`) |
| `--output PATH` | Where sorted copies and the report go (default `output`) |
| `--dry-run` | Print decisions, write no folders or report (new photos still use API calls) |
| `--threshold N` | Duplicate sensitivity: lower is stricter, higher groups more (default 6) |
| `--rejudge` | Ignore saved judgments and ask the AI again |
| `--results PATH` | Judgment cache file (default `results.json`) |

Supported types: `.jpg`, `.jpeg`, `.png`, `.webp`, and iPhone `.heic`. Only the top level of the input folder is scanned.

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
- Your API key lives only in `.env`. Never paste it in code, chats or screenshots. If it leaks, delete it in Google AI Studio and make a new one.
- `.gitignore` keeps private and generated data out of git: `.env`, `results.json`, `labels.csv`, `output/`, `test_photos/` and `source_photos/`. `results.json` and `labels.csv` contain your filenames, so do not publish them if those are private.
- Photos you want to share belong in `sample_photos/`, which is not ignored.

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` | The venv is not active. Activate it and run `pip install -r requirements.txt`. |
| `No module named src` | You are not in the project folder. `cd` into the folder that contains `src/`. |
| `GEMINI_API_KEY is not set` | Create `.env` (Step 4) and run from the project folder. On Windows, check the file is not really named `.env.txt`: run `Get-ChildItem -Force .env*`. |
| `GEMINI_API_KEY was rejected` | Check `.env` for typos, quotes or extra spaces, and that the key is active in Google AI Studio. |
| `Model '...' was not found` | Run `python -m src.list_models`, then set `GEMINI_MODEL=<model>` in `.env`. |
| `Input folder not found` | The `--input` path does not exist. Folders like `test_photos/` are not in the repo; use `sample_photos` or your own path, in quotes if it has spaces. |
| `Found 0 photos` | Check the path and file types. Subfolders are not scanned. |
| `ERROR` lines with 429 or quota | You hit a rate limit. Wait and rerun; finished photos are cached. |
| `ERROR ... cannot identify image file` | The file is corrupt or not a real image. It is skipped. |
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
| `sample_photos/` | Example photos to try the tool right after cloning |
| `tests/` | Automated tests (fake judge, no API key needed) |
| `.github/workflows/portability.yml` | CI on Windows, macOS and Linux with Python 3.10, 3.12, 3.14 |
| `requirements.txt` | The 8 direct dependencies |
| `.env.example` | Template for your private `.env` |
| `.gitignore` | Keeps secrets and private or generated data out of git |
| `LICENSE` | MIT license |

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