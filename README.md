# Photo Culler v2

An AI photo culler. It scores your photos with the Gemini API, flags bad
duplicates, and moves rejects into a `deleted_photos` folder so nothing is
permanently deleted.

Works on Windows, macOS, and Linux.

## How to read this guide

Two kinds of boxes appear below, so you always know where to type things:

- **TERMINAL** means type it into a terminal window and press Enter.
- **.ENV FILE** means type it inside the `.env` text file. Do NOT type
  these lines into a terminal. They are settings, not commands.

---

## Before you start (one-time checks)

You need three things:

1. **Python 3.10 or newer.** Check by opening a terminal (see below) and
   typing `python --version` (Windows) or `python3 --version`
   (macOS/Linux). If you get an error or a version lower than 3.10,
   install Python from https://www.python.org/downloads/
2. **Git.** Check with `git --version`. If missing, install it from
   https://git-scm.com/downloads
3. **A free Gemini API key** from https://aistudio.google.com/apikey
   (sign in, click "Create API key", copy it somewhere for Step 3).

### How to open a terminal

- **Windows:** press the Start button, type `PowerShell`, press Enter.
- **macOS:** press Cmd + Space, type `Terminal`, press Enter.
- **Linux:** press Ctrl + Alt + T.

---

## Step 1: Download (clone) the project

**TERMINAL**

```
git clone https://github.com/jayanma29-bit/photo_culler_v2.git
cd photo_culler_v2
```

The first line downloads the project into a new folder called
`photo_culler_v2`. The second line moves your terminal into that folder.

**Important:** for every step after this, your terminal must be inside the
`photo_culler_v2` folder. If you close the terminal and open a new one,
move back into the folder with `cd` and the path to where you cloned it,
for example `cd C:\Users\YourName\photo_culler_v2` on Windows or
`cd ~/photo_culler_v2` on macOS/Linux. Running things from any other
folder will break the program's paths.

After cloning, the folder looks like this:

```
photo_culler_v2/
├── .github/
├── src/                 (the program: main.py, judge.py, ...)
├── tests/
├── sample_photos/       (example photos you can try first)
├── test_photos/         (default input folder)
├── .env.example         (template for your settings)
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

These do not come with the download. They get created on your computer
as you follow the steps: `.venv/` (Step 2), `.env` (Step 3), and
`output/` and `results.json` (first run).

---

## Step 2: Create a virtual environment and install packages

A virtual environment is a private box for this project's Python packages,
so they don't mix with anything else on your computer. You create it once.

**TERMINAL (Windows PowerShell)**

```
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If you see a red error saying scripts are disabled, run this one line,
then run the activate line again:

```
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**TERMINAL (macOS / Linux)**

```
python3 -m venv .venv
source .venv/bin/activate
```

**What you should see:** your prompt now starts with `(.venv)`. That means
the environment is active. Now install the packages (same terminal, all
operating systems):

**TERMINAL**

```
pip install -r requirements.txt
```

Wait for it to finish. You will see a lot of text scrolling by. That is
normal.

---

## Step 3: Add your API key and settings

All of your settings live in one text file called `.env`. You make it by
copying the template.

### 3a. Create your `.env` file

**TERMINAL (Windows)**

```
copy .env.example .env
```

**TERMINAL (macOS / Linux)**

```
cp .env.example .env
```

### 3b. Open `.env` and edit it

Files that start with a dot are hidden on macOS and Linux, so open it from
the terminal:

**TERMINAL (Windows)**

```
notepad .env
```

**TERMINAL (macOS)**

```
open -e .env
```

**TERMINAL (Linux)**

```
nano .env
```
(In nano: edit, then press Ctrl + O, Enter to save, Ctrl + X to exit.)

You can also open the project folder in VS Code and click the `.env` file.

### 3c. Fill in the file

The file should contain these four lines. Replace only what is after the
`=` sign. Do not add spaces around the `=`, and do not add quotes.

**.ENV FILE** (type this inside the file, NOT in the terminal)

```
GEMINI_API_KEY=paste_your_key_here
GEMINI_MODEL=gemini-3.8-flash
INPUT_DIR=test_photos
OUTPUT_DIR=output
```

Save the file when you are done. Never share your `.env` file or post your
key anywhere. It is already excluded from Git.

What each line does:

| Setting | What it means |
|---|---|
| `GEMINI_API_KEY` | Your own key from Google AI Studio. |
| `GEMINI_MODEL` | Which Gemini model scores your photos. |
| `INPUT_DIR` | The folder your photos are read from. |
| `OUTPUT_DIR` | The folder results are written to. |

### Changing the model

Open `.env` (Step 3b), change the `GEMINI_MODEL` line to another model ID
from Google AI Studio, save, and run the program again. You do not edit
any code. The ID must be typed exactly, or you will get a "model not
found" error.

### Choosing where your photos come from (input)

`INPUT_DIR` in your `.env` file is the folder the program reads photos
from. It stays set until you change it.

**Option A: use the default.** Leave the line as `INPUT_DIR=test_photos`.
Then put your photos inside the `test_photos` folder in the project.
Nothing else to do.

**Option B: use a folder somewhere else on your computer.** Replace the
value in the `.env` file with the full path of that folder:

**.ENV FILE** (pick the line for your system, NOT in the terminal)

```
INPUT_DIR=C:\Users\YourName\Pictures\Trip
```
```
INPUT_DIR=/Users/yourname/Pictures/Trip
```
```
INPUT_DIR=/home/yourname/Pictures/Trip
```

The first is a Windows example, the second macOS, the third Linux. Use
only one `INPUT_DIR` line in your file, with your real folder.

**How to get a folder's full path:**

- **Windows:** open the folder in File Explorer, click the address bar at
  the top, and copy the text. If you right-click the folder and choose
  "Copy as path" instead, delete the quotation marks at the start and end
  after pasting.
- **macOS:** right-click the folder in Finder, hold the Option key, and
  click "Copy ... as Pathname".
- **Linux:** in a terminal, `cd` into the folder and type `pwd`. Copy what
  it prints.

Your original photos are never changed or deleted.

### Choosing where results go (output)

`OUTPUT_DIR` in your `.env` file is where results are written.

**Option A: use the default.** Leave it as `OUTPUT_DIR=output`. The
program creates a folder called `output` inside the project the first time
you run it. It does not exist before then, so don't worry if you can't
find it yet.

To open it after the first run:

**TERMINAL (Windows)**

```
explorer output
```

**TERMINAL (macOS)**

```
open output
```

**TERMINAL (Linux)**

```
xdg-open output
```

**Option B: send results somewhere easier to find**, like your Desktop.
Replace the value in the `.env` file with a full path (get it the same way
as for the input folder):

**.ENV FILE** (pick one, NOT in the terminal)

```
OUTPUT_DIR=C:\Users\YourName\Desktop\culled
```
```
OUTPUT_DIR=/Users/yourname/Desktop/culled
```
```
OUTPUT_DIR=/home/yourname/Desktop/culled
```

If the folder does not exist, the program creates it.

---

## Step 4: Run it

Make sure your terminal is inside the `photo_culler_v2` folder and your
prompt starts with `(.venv)`.

**TERMINAL (Windows)**

```
python -m src.main
```

**TERMINAL (macOS / Linux)**

```
python3 -m src.main
```

When it finishes, open your output folder (Step 3, "Choosing where
results go") to see the results. Low-rated photos and bad duplicates are
moved into `deleted_photos`, so you can review them before deleting
anything yourself.

---

## Coming back later

Each time you open a new terminal to run the program again:

1. `cd` into the `photo_culler_v2` folder.
2. Activate the environment again (Step 2: the `Activate.ps1` line on
   Windows, the `source` line on macOS/Linux).
3. Run Step 4.

You do not need to repeat the clone, the install, or the `.env` setup.