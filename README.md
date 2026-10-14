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
3. **Sorted copies and a report.** Your photos are copied into a `kept` folder and a `rejected` folder (which is split into `low_rated` and `duplicates`), and `report.csv` explains every decision.

**Your original photos are never modified.** The tool only reads your input folder and writes copies to a separate output folder.

**Good to know:** judgments are cached in `results.json`, so rerunning on the same photos is free and instant, and an interrupted run continues where it stopped. One bad photo never stops a run; it is printed as an `ERROR` line and skipped.

## Setup

Plan on about 10 minutes. You will install Python, download the project, install its packages, add your API key, and run it. Every step says what you should see and what to do if you don't.

**You need:** a Windows, macOS or Linux computer, an internet connection, and a Google account (for the Gemini API key). API availability, limits and pricing depend on your country and change over time, so check Google's current terms.

**Two kinds of code boxes below.** Some boxes are labeled for one operating system. Type only the box for your system. Never paste a Windows box and a macOS/Linux box together, because the other system's commands will fail.

### Step 0: Open a terminal

A terminal is a window where you type commands. Every command in this guide goes into it: type or paste the command, press Enter, and wait until your prompt comes back before the next one.

- **Windows:** press the Windows key, type `PowerShell`, press Enter.
- **macOS:** press Cmd+Space, type `Terminal`, press Enter.
- **Linux:** press Ctrl+Alt+T.

### Step 1: Check that Python is installed

Windows:

```
python --version
```

macOS / Linux:

```
python3 --version
```

**You should see:** `Python 3.10.x` or higher (3.12 and 3.14 also work).

**If not** (the command is not found, or the version is below 3.10): install the newest Python from [python.org/downloads](https://www.python.org/downloads/). On Windows, tick **Add python.exe to PATH** on the first installer screen. Close the terminal, open a new one, and check again. On Windows, if `python` still is not found but `py --version` works, type `py -m venv .venv` in Step 3 instead of `python -m venv .venv`.

### Step 2: Download the project

First choose where it will live. This puts it on your Desktop.

Windows:

```
cd $HOME\Desktop
```

macOS / Linux:

```
cd ~/Desktop
```

**Option A, with git:**

```
git clone https://github.com/jayanma29-bit/photo_culler_v2.git
cd photo_culler_v2
```

You should see `Cloning into 'photo_culler_v2'...`. If you get `git is not recognized`, install git from [git-scm.com](https://git-scm.com/downloads) or use Option B.

**Option B, without git:** on the GitHub repository page click the green **Code** button, then **Download ZIP**. Unzip it (on Windows: right-click, **Extract All**). The folder is named `photo_culler_v2-main`.
- **Windows:** open that folder in File Explorer, click the address bar at the top, type `powershell`, and press Enter. A terminal opens inside the folder.
- **macOS / Linux:** in the terminal run `cd ~/Downloads/photo_culler_v2-main`.

**Check you are in the right folder.** Run this:

Windows:

```
Get-ChildItem
```

macOS / Linux:

```
ls
```

You should see `src`, `tests`, `sample_photos`, `requirements.txt` and `README.md`. If you don't, you are in the wrong folder; use `cd` to move into the project folder.

> **Important:** from here on, every command must be run from inside this project folder. The program finds its files relative to it.

### Step 3: Create a virtual environment and install packages

A virtual environment is a private box for this project's packages, so they don't mix with other Python programs on your computer.

**Windows (PowerShell):**

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

**You should see:** after the second command, `(.venv)` appears at the start of your prompt. The install then prints many `Collecting...` lines, takes about a minute, and ends with `Successfully installed ...`. A notice saying a new version of pip is available is harmless.

**If not:**
- **"running scripts is disabled" (Windows):** run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, answer `Y` if asked, then run the activate line again.
- **No `(.venv)` at the start of your prompt:** the environment is not active. Run the activate line again, and do not continue until you see it.
- **`venv` fails on Debian or Ubuntu:** run `sudo apt install python3-venv`, then try again.
- **`Failed building wheel for pillow-heif`:** open `requirements.txt`, delete the `pillow-heif` line, save, and run `pip install -r requirements.txt` again. Everything works except `.heic` photos.

### Step 4: Get an API key and create your `.env` file

The AI judging needs your own Gemini API key. It goes in a file named `.env`, which is **not** in the repository on purpose, so you create it yourself. This file is a settings file: its lines are typed inside the file, never into the terminal.

**Get a key:** go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey), sign in, click **Create API key**, and copy it. It usually starts with `AIza`. Treat it like a password: never post it or commit it.

**Create `.env` from the template** (the project includes a template called `.env.example`):

Windows:

```
Copy-Item .env.example .env
notepad .env
```

macOS / Linux:

```
cp .env.example .env
nano .env
```

An editor opens showing `GEMINI_API_KEY=your_key_here`. Delete `your_key_here` and paste your key in its place, so the line reads like `GEMINI_API_KEY=AIza...`. No quotes and no spaces around `=`. Leave the lines that start with `#` alone.

**Save:** in Notepad press Ctrl+S and close it. In nano press Ctrl+O, Enter, then Ctrl+X.

**Check the file exists** (it starts with a dot, so file browsers often hide it, which is normal):

Windows:

```
Get-ChildItem -Force .env*
```

macOS / Linux:

```
ls -a .env*
```

**You should see:** `.env` and `.env.example`. On Windows, if you see `.env.txt` instead, fix the name with `Rename-Item .env.txt .env`.

**Changing the AI model (optional).** You do not need to do this to get started. If you ever want a different Gemini model:

1. Run `python -m src.list_models` to see the models your key can use.
2. Open `.env` again (the same `notepad .env` or `nano .env` command as above).
3. Add or edit a line so it reads `GEMINI_MODEL=model-name-here`, using the exact name from step 1. No quotes and no spaces around `=`.
4. Save the file and run the program again. You do not edit any code.

Photos judged earlier are remembered in `results.json`, so they keep their old verdicts. Add `--rejudge` to the run command to ask the new model about every photo again.

### Step 5: Check that it works

```
python -m src.main --help
```

**You should see:** a usage message listing the options (`--input`, `--output`, `--dry-run` and so on).

**If not:** `ModuleNotFoundError` means the environment is not active (go back to Step 3). `No module named src` means you are in the wrong folder (go back to Step 2).

### Step 6: Run it on the sample photos

First a dry run. It writes no files but does call the AI, so it needs your key and internet:

```
python -m src.main --input sample_photos --dry-run
```

**You should see:** `Found N photos in sample_photos`, then one line per photo showing whether it is kept, low-rated or a duplicate, with a score and a reason. Each photo takes a few seconds. It ends with a `Done.` summary line. If you see `GEMINI_API_KEY is not set`, go back to Step 4.

Now the real run, which writes the sorted copies:

```
python -m src.main --input sample_photos
```

Open the results folder.

Windows:

```
explorer output
```

macOS:

```
open output
```

Linux:

```
xdg-open output
```

**You should see:** the folders `kept` and `rejected` and a file `report.csv`. Your original photos were not changed.

### Step 7: Use your own photos

Put the photos you want sorted in one folder, then point `--input` at it. Keep the quotes if the path has spaces.

**How to get the exact path of a folder:**

- **Windows:** right-click the folder and choose **Copy as path**.
- **macOS:** right-click the folder in Finder, hold the Option key, and choose **Copy ... as Pathname**.
- **Linux:** in a terminal, `cd` into the folder and type `pwd`.

Windows example:

```
python -m src.main --input "C:\Users\you\Pictures\Trip" --dry-run
python -m src.main --input "C:\Users\you\Pictures\Trip"
```

macOS / Linux example:

```
python3 -m src.main --input "/Users/you/Pictures/Trip" --dry-run
python3 -m src.main --input "/Users/you/Pictures/Trip"
```

Supported files are `.jpg`, `.jpeg`, `.png`, `.webp` and `.heic`, and only the top level of that folder is scanned.

By default results go to the `output` folder inside the project. To send them somewhere else, add `--output` with a path, for example `--output "C:\Users\you\Desktop\culled"`. Use a dedicated folder for this, because the `kept` and `rejected` folders inside it are rebuilt on every run.

### Coming back later

Steps 1 to 4 are a one-time setup. Each time you open a new terminal, only do this:

Windows:

```
cd path\to\photo_culler_v2
.\.venv\Scripts\Activate.ps1
python -m src.main --input "path\to\photos"
```

macOS / Linux:

```
cd path/to/photo_culler_v2
source .venv/bin/activate
python3 -m src.main --input "path/to/photos"
```

### Files you create yourself

| File or folder | Created by | Needed to run? |
|---|---|---|
| `.venv/` | You, in Step 3 | Yes |
| `.env` | You, in Step 4 | Yes (holds your API key) |
| A photo folder | You (or use `sample_photos/`) | Yes |
| `results.json` | The tool (judgment cache) | No |
| `output/` | The tool (sorted copies and `report.csv`) | No |
| `labels.csv` | `python -m src.evaluate --template` | Only for accuracy testing |

The last three are private or generated data, so git ignores them. They will not be in a fresh clone, and that is normal.

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