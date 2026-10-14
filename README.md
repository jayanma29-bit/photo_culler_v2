# Photo Culler

![portability](https://github.com/jayanma29-bit/photo_culler_v2/actions/workflows/portability.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%20%7C%203.12%20%7C%203.14-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

Sort a messy folder of photos into the ones worth keeping, the ones that are not, and the extra copies, using AI and image hashing.

## What you need

Have these ready before you start. Total time: about 10 minutes.

| You need | Details |
|---|---|
| A computer | Windows, macOS or Linux |
| An internet connection | The AI judging runs through Google's Gemini API |
| Python 3.10 or newer | Step 1 checks this and tells you how to install it if it is missing |
| A Google account | Used in Step 5 to get a free Gemini API key |
| Photos to sort | Keep them together in one folder. Supported: `.jpg`, `.jpeg`, `.png`, `.webp`, `.heic` |
| Git (optional) | Step 2 also shows a way to download the project without it |

API availability, limits and pricing depend on your country and change over time, so check Google's current terms.

**You will write down four things as you go.** Keep a notes file open and fill these in:

```
Project folder path : ______________________  (Step 2)
Photos folder path  : ______________________  (Step 3)
Results folder path : ______________________  (Step 3)
Gemini API key      : ______________________  (Step 5, keep it private)
```

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

## Setup

Do the steps in order. Steps 0 to 5 are a one-time setup. After that you only repeat Step 8.

### How to read this guide

- **Type only the box for your system.** Boxes are labeled Windows or macOS / Linux. Never paste both together, because the other system's commands will fail.
- **Type one command at a time.** Press Enter and wait for your prompt to come back before the next one.
- **Placeholders must be replaced.** Anything like `YourName`, `PHOTOS_PATH` or `path\to\...` is an example. Replace it with your real value.
- **After each command** you will see **You should see** (what a working result looks like) and **If not** (what to do).

### Finding a folder's path

You will copy folder paths in Steps 2, 3 and 8. A path is a folder's full address, for example `C:\Users\YourName\Desktop\MyPhotos`.

- **Windows:** in File Explorer, right-click the folder and choose **Copy as path**. On Windows 11, if you do not see it, hold Shift while you right-click. Windows adds the quotation marks for you.
- **macOS:** in Finder, right-click the folder, hold the Option key, and choose **Copy "FolderName" as Pathname**. Add the quotation marks yourself when you use it.
- **Linux:** in a terminal, `cd` into the folder and type `pwd`. Copy what it prints.

**Shortcut on Windows and macOS:** type `cd ` (with a space after it), drag the folder from your file window into the terminal, and press Enter.

### Step 0: Open a terminal

A terminal is a window where you type commands.

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

**If not** (the command is not found, or the version is below 3.10): install the newest Python from [python.org/downloads](https://www.python.org/downloads/). On Windows, tick **Add python.exe to PATH** on the first installer screen. Close the terminal, open a new one, and check again. On Windows, if `python` still is not found but `py --version` works, type `py -m venv .venv` in Step 4 instead of `python -m venv .venv`.

### Step 2: Download the project

**2a. Choose where the project will live, and go there.**

> **You must change the path in this step.** The commands below use your Desktop as an example. The terminal has to be inside the folder where you want the project to live, so replace the path with your own if you want it somewhere else.

To use your Desktop:

Windows:

```
cd $HOME\Desktop
```

macOS / Linux:

```
cd ~/Desktop
```

To use a different folder, replace the path with yours. Keep the quotation marks, which are needed if the path has spaces.

Windows:

```
cd "C:\Users\YourName\Documents"
```

macOS:

```
cd "/Users/yourname/Documents"
```

Linux:

```
cd "/home/yourname/Documents"
```

**You should see:** no message, and your prompt now ends with the name of that folder.

**If not:** on Windows, `Cannot find path ... Desktop` usually means your Desktop is inside OneDrive. Use `cd "$HOME\OneDrive\Desktop"` or pick another folder, such as Documents.

**2b. Download the project.**

**Option A, with git:**

```
git clone https://github.com/jayanma29-bit/photo_culler_v2.git
cd photo_culler_v2
```

You should see `Cloning into 'photo_culler_v2'...`. The second line (`cd photo_culler_v2`) is not a path you change. It always moves into the folder that was just downloaded. If you get `git is not recognized`, install git from [git-scm.com](https://git-scm.com/downloads) or use Option B.

**Option B, without git:** on the GitHub repository page click the green **Code** button, then **Download ZIP**. Unzip it (on Windows: right-click, **Extract All**). The folder is named `photo_culler_v2-main`.
- **Windows:** open that folder in File Explorer, click the address bar at the top, type `powershell`, and press Enter. A terminal opens inside the folder.
- **macOS / Linux:** in the terminal run `cd ~/Downloads/photo_culler_v2-main`. **Change this path** if you unzipped it somewhere else.

**2c. Check you are in the right folder.** Run this:

Windows:

```
Get-ChildItem
```

macOS / Linux:

```
ls
```

You should see `src`, `tests`, `sample_photos`, `requirements.txt` and `README.md`. If you don't, you are in the wrong folder; use `cd` to move into the project folder.

Here is what the project folder looks like right after downloading:

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

Files that start with a dot (`.github`, `.env.example`, `.gitignore`) are often hidden in file browsers. On macOS press Cmd+Shift+. to show them. That is normal.

**2d. Write down your project folder path.** Run this and copy what it prints into your notes:

Windows:

```
Get-Location
```

macOS / Linux:

```
pwd
```

> **Important:** from here on, every command must be run from inside this project folder. The program finds its files relative to it.

### Step 3: Set up your folders (photos in, results out)

The program needs two folders: one to read photos from (input) and one to write results to (output). Set them up now, before installing anything else. You will tell the program about them when you run it (Step 8).

**3a. Choose your photos folder (input).** Pick one:

- **To try it first:** use `sample_photos`, which is already in the project. There is nothing to set up. Go to 3b.
- **To sort your own photos:**
  1. Create a new empty folder, for example `MyPhotos` on your Desktop (right-click, **New**, **Folder**).
  2. Copy your photos into it. Put them directly in this folder, because subfolders are not scanned.
  3. For your first run, use a small batch of 20 to 50 photos so it finishes quickly.
  4. Copy the folder's path (see "Finding a folder's path" above) into your notes as your **Photos folder path**.

**3b. Choose your results folder (output).** Pick one:

- **Default (easiest):** do nothing. Results go into a folder called `output` inside the project, and the program creates it on the first run. Write `output` in your notes.
- **Your own location:**
  1. Create a new empty folder for the results, for example `culled` on your Desktop.
  2. Use a folder just for this tool, and not the same folder as your photos. The `kept` and `rejected` folders inside it are rebuilt on every run.
  3. Copy its path into your notes as your **Results folder path**.

**3c. Your notes should now look like this** (examples):

```
Project folder path : C:\Users\YourName\Desktop\photo_culler_v2
Photos folder path  : C:\Users\YourName\Desktop\MyPhotos     (or: sample_photos)
Results folder path : C:\Users\YourName\Desktop\culled       (or: output)
```

**How to change them later:** you do not edit any code or settings file. You type a different path in the run command (Step 8) and nothing else.

### Step 4: Create a virtual environment and install packages

A virtual environment is a private box for this project's packages, so they don't mix with other Python programs on your computer. Make sure your terminal is still inside the project folder (Step 2d).

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

### Step 5: Get an API key and create your `.env` file

The AI judging needs your own Gemini API key. It goes in a file named `.env`, which is **not** in the repository on purpose, so you create it yourself. This is a settings file: its lines are typed inside the file, never into the terminal.

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

### Step 6: Check that it works

```
python -m src.main --help
```

**You should see:** a usage message listing the options (`--input`, `--output`, `--dry-run` and so on).

**If not:** `ModuleNotFoundError` means the environment is not active (go back to Step 4). `No module named src` means you are in the wrong folder (go back to Step 2).

### Step 7: Run it on the sample photos

First a dry run. It writes no files but does call the AI, so it needs your key and internet:

```
python -m src.main --input sample_photos --dry-run
```

**You should see:** `Found N photos in sample_photos`, then one line per photo showing whether it is kept, low-rated or a duplicate, with a score and a reason. Each photo takes a few seconds. It ends with a `Done.` summary line. If you see `GEMINI_API_KEY is not set`, go back to Step 5.

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

Your project folder now looks like this:

```
photo_culler_v2/
├── .github/
├── .venv/               (you created it in Step 4)
├── output/              (made by the program: kept/, rejected/, report.csv)
├── sample_photos/
├── src/
├── tests/
├── .env                 (you created it in Step 5: holds your API key)
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
└── results.json         (made by the program: remembers its judgments)
```

### Step 8: Use your own photos and your own folders

This is where you use the paths from your notes (Step 3). You give them to the program with two options:

- `--input` is the folder with your photos.
- `--output` is the folder where the results go.

Both are optional. If you leave one out, the default is used: `sample_photos` for input and `output` for output.

**The pattern:**

```
python -m src.main --input "PHOTOS_PATH" --output "RESULTS_PATH"
```

Replace `PHOTOS_PATH` and `RESULTS_PATH` with the paths from your notes. Keep the quotation marks. If you used **Copy as path** on Windows, the quotes came with the path, so replace `"PHOTOS_PATH"` including its quotes. Do not end a Windows path with a backslash.

**Do a dry run first, then the real run.** A dry run prints every decision and writes nothing.

Windows:

```
python -m src.main --input "C:\Users\YourName\Desktop\MyPhotos" --output "C:\Users\YourName\Desktop\culled" --dry-run
python -m src.main --input "C:\Users\YourName\Desktop\MyPhotos" --output "C:\Users\YourName\Desktop\culled"
```

macOS:

```
python3 -m src.main --input "/Users/yourname/Desktop/MyPhotos" --output "/Users/yourname/Desktop/culled" --dry-run
python3 -m src.main --input "/Users/yourname/Desktop/MyPhotos" --output "/Users/yourname/Desktop/culled"
```

Linux:

```
python3 -m src.main --input "/home/yourname/Desktop/MyPhotos" --output "/home/yourname/Desktop/culled" --dry-run
python3 -m src.main --input "/home/yourname/Desktop/MyPhotos" --output "/home/yourname/Desktop/culled"
```

**Changing only one folder.** Leave the other option out.

- Only your own photos, results in the default `output`: `python -m src.main --input "PHOTOS_PATH"`
- Only a different results folder, with the default `sample_photos`: `python -m src.main --output "RESULTS_PATH"`

**Changing folders any time.** Run the command again with a different path. Nothing else changes. Two tips:

- Judgments are remembered in `results.json` by filename, and cameras often reuse names like `IMG_0001.jpg`. When you switch to a different photos folder, give it its own memory file so the two sets don't get mixed up. For example, add `--results results_trip.json` to the command.
- Press the Up arrow key in the terminal to bring back your last command instead of typing the paths again.

Supported files are `.jpg`, `.jpeg`, `.png`, `.webp` and `.heic`, and only the top level of the photos folder is scanned.

To see the results, open your results folder: the `output` folder in the project (use the command in Step 7), or the folder you gave to `--output`.

### Coming back later

Steps 1 to 5 are a one-time setup. Each time you open a new terminal, only do this. **Change the paths** to your own project folder and your own photos and results folders from your notes.

Windows:

```
cd "C:\Users\YourName\Desktop\photo_culler_v2"
.\.venv\Scripts\Activate.ps1
python -m src.main --input "C:\Users\YourName\Desktop\MyPhotos" --output "C:\Users\YourName\Desktop\culled"
```

macOS / Linux:

```
cd "/path/to/photo_culler_v2"
source .venv/bin/activate
python3 -m src.main --input "/path/to/photos" --output "/path/to/results"
```

### Files you create yourself

| File or folder | Created by | Needed to run? |
|---|---|---|
| `.venv/` | You, in Step 4 | Yes |
| `.env` | You, in Step 5 | Yes (holds your API key) |
| A photo folder | You, in Step 3 (or use `sample_photos/`) | Yes |
| A results folder | You, in Step 3, or `output/` made by the tool | No |
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
| `GEMINI_API_KEY is not set` | Create `.env` (Step 5) and run from the project folder. On Windows, check the file is not really named `.env.txt`: run `Get-ChildItem -Force .env*`. |
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