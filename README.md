# Photo Culler

![portability](https://github.com/jayanma29-bit/photo_culler_v2/actions/workflows/portability.yml/badge.svg)

A command-line tool that sorts a folder of photos into **kept**, **rejected/low_rated** and **rejected/duplicates**.

1. A Gemini AI model judges each photo on sharpness/focus, exposure, composition and subject clarity, and returns a keep/reject decision, a 1-10 score and a one-sentence reason.
2. A local perceptual-hash check then finds near-identical shots (like burst photos) among the keepers and keeps only the highest-scoring one from each group.
3. Copies of your photos are sorted into folders, and a `report.csv` explains every decision.

**The tool never modifies your input folder.** It only writes copies into a separate output folder.

## Requirements

- Python 3.10 or newer ([python.org/downloads](https://www.python.org/downloads/))
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey). Availability, free-tier limits and pricing depend on your country and change over time, so check Google's current terms.

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

- No git? On the repository page click **Code > Download ZIP**, unzip it, and open PowerShell in that folder.
- If `python` is not found, try `py` instead.
- If activation says "scripts are disabled", run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and activate again.
- In Command Prompt, activate with `.venv\Scripts\activate.bat`.

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

- No git? Use **Code > Download ZIP** instead of `git clone`.
- On Debian or Ubuntu, if `python3 -m venv` fails, run `sudo apt install python3-venv` first.

In `.env`, replace `your_key_here` with your API key and save. Your venv must be active (you will see `(.venv)` in your prompt) every time you run the tool.

## Usage

```
python -m src.main --input "path/to/your/photos"
```

Sorted copies and a report appear in `output/`:

```
output/
  kept/                 the best photos
  rejected/low_rated/   judged blurry, dark, badly composed, etc.
  rejected/duplicates/  fine photos, but a better copy is in kept/
  report.csv            every photo with status, score, reason, and which photo it duplicates
```

Try it safely first with `--dry-run`, which prints every decision and writes no folders or report.

| Option | Meaning |
|---|---|
| `--input PATH` | Folder with your photos (default `test_photos`) |
| `--output PATH` | Folder for sorted copies and the report (default `output`) |
| `--dry-run` | Print decisions without writing sorted folders or the report (judgments are still cached) |
| `--threshold N` | Duplicate sensitivity: lower is stricter, higher groups more photos together (default 6) |
| `--rejudge` | Ignore saved judgments and ask the AI again (use after changing the prompt or model) |
| `--results PATH` | Cache file for AI judgments (default `results.json`) |

Supported types: `.jpg`, `.jpeg`, `.png`, `.webp`, and `.heic`/`.heif` (iPhone and Mac photos) when `pillow-heif` is installed. Only the top level of the input folder is scanned, not subfolders. RAW files are not supported.

## Safety

- **Your photos are never moved, edited or deleted.** The input folder is only read.
- **The output folder is rebuilt every run.** The `kept/` and `rejected/` folders inside it are deleted and recreated, so use a dedicated output folder. The tool refuses to touch `kept/` or `rejected/` folders it did not create.
- **Your API key is a secret.** Keep it only in `.env`, which is excluded from git. Never paste it into chats, code or screenshots. If it leaks, delete it in Google AI Studio and create a new one.
- **Photos leave your computer.** Each photo is shrunk to at most 1024 px and uploaded to Google's Gemini API for judging. Only use photos you are comfortable sending to a third party, and review Google's current terms for how API data may be used.
- **Cost and limits.** Each photo not already in the cache is one API call, subject to your key's rate limits and pricing. Judgments are cached, so reruns are free and instant.

## How decisions are made

- The AI is asked to act as a strict photo editor. A photo with `keep: true` goes on to duplicate checking, and `keep: false` goes to `low_rated`.
- Near-duplicates are found with a perceptual hash. Two photos within `--threshold` of each other (default 6 out of 64 bits) are grouped. In each group the highest AI score wins, with ties broken by larger file size.
- Photos whose AI call fails after retries are listed as `ERROR` and left out of `output/`. Successful photos are cached, so rerunning retries only the failed ones. Rate-limit errors are retried with longer waits.

## Measuring accuracy

1. Run the tool on a set of photos, then create a label sheet: `python -m src.evaluate --template`
2. Open `labels.csv` and fill the `keep` column yourself (`1` = you would keep it, `0` = you would reject it). Judge the photos, not the AI's answers.
3. Run `python -m src.evaluate` for accuracy, keep recall, keep precision, and a list of every photo where you and the AI disagree.

The evaluation reads the default `results.json`, and it measures the AI's keep/reject judgment, not duplicate grouping.

## Troubleshooting

| Message | Fix |
|---|---|
| `GEMINI_API_KEY is not set` | Create `.env` from `.env.example`, add your key, and run from the project folder. |
| `Model '...' was not found` | Run `python -m src.list_models`, then set `GEMINI_MODEL=<a listed model>` in `.env`. |
| `Your GEMINI_API_KEY was rejected` | Check `.env` for typos, quotes or extra spaces. |
| Many `ERROR` lines mentioning 429 or quota | You hit a rate or daily limit. Wait and rerun; finished photos are cached. |
| `Found 0 photos` | Check the folder path and file types. Subfolders are not scanned. |
| `Refusing to overwrite ... not created by this tool` | Pick a different `--output` folder. |
| `results.json was empty or corrupted` | The cache was set aside as `results.json.bad` and a fresh one started. Nothing to do. |

## Project structure

```
src/main.py          command-line tool: judging, duplicate grouping, sorting, report
src/judge.py         Gemini API call, prompt, retries
src/evaluate.py      precision/recall against your own labels
src/list_models.py   lists the models your API key can use
tests/               automated tests (no API key needed)
.github/workflows/   checks that it installs and starts on Windows, macOS and Linux
```

## Development

```
pip install pytest
python -m pytest -q
```

The tests use a fake judge, so they need no API key. Continuous integration checks installation, startup and these tests on Windows, macOS and Linux. The AI judging itself needs a real key and is not run there.

## Limitations

- Each photo is judged on its own. The AI never compares two shots directly.
- Duplicate grouping is greedy: a long sequence of slowly changing shots can chain into one group. Lower `--threshold` if different shots get grouped.
- The cache is keyed by filename. If you scan two folders with identical filenames, give each its own `--results` file.
- Model names change over time. If the default model stops working, set `GEMINI_MODEL` in `.env`.

## Results

(Add your measured accuracy, keep recall and keep precision from `python -m src.evaluate`, what failed, and how you fixed it.)

## License

MIT. See `LICENSE`.