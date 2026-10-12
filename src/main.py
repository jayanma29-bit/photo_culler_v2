import argparse
import csv
import json
import shutil
from pathlib import Path

import imagehash
from PIL import Image, ImageOps

from src.judge import judge_photo

INPUT_DIR = Path("test_photos")
OUTPUT_DIR = Path("output")
KEPT_DIR = OUTPUT_DIR / "kept"
LOW_RATED_DIR = OUTPUT_DIR / "rejected" / "low_rated"
DUPLICATES_DIR = OUTPUT_DIR / "rejected" / "duplicates"
REPORT_FILE = OUTPUT_DIR / "report.csv"
RESULTS_FILE = Path("results.json")
EXTENSIONS = {".jpg", ".jpeg", ".png"}
DUPLICATE_THRESHOLD = 6  # max hash distance to call two photos duplicates (0 = identical)


def load_results():
    if RESULTS_FILE.exists():
        return json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
    return {}


def save_results(results):
    RESULTS_FILE.write_text(json.dumps(results, indent=2), encoding="utf-8")


def photo_hash(path):
    img = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    return imagehash.phash(img)


def group_duplicates(paths):
    """Group photos whose perceptual hashes are close. Returns a list of groups."""
    groups = []
    for path in paths:
        h = photo_hash(path)
        for group in groups:
            if any(h - other <= DUPLICATE_THRESHOLD for _, other in group):
                group.append((path, h))
                break
        else:
            groups.append([(path, h)])
    return [[p for p, _ in g] for g in groups]


def sort_into_folders(decisions):
    """Rebuild output/ from scratch and copy every photo into its folder."""
    for folder in (KEPT_DIR, OUTPUT_DIR / "rejected"):
        if folder.exists():
            shutil.rmtree(folder)  # safe: output/ only ever holds copies
    for folder in (KEPT_DIR, LOW_RATED_DIR, DUPLICATES_DIR):
        folder.mkdir(parents=True)

    targets = {"kept": KEPT_DIR, "low_rated": LOW_RATED_DIR, "duplicate": DUPLICATES_DIR}
    for photo, (status, _) in decisions.items():
        shutil.copy2(photo, targets[status] / photo.name)


def write_report(decisions, results):
    with open(REPORT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "status", "score", "reason", "duplicate_of"])
        for photo, (status, duplicate_of) in sorted(decisions.items(), key=lambda kv: kv[0].name):
            r = results[photo.name]
            writer.writerow([photo.name, status, r["score"], r["reason"], duplicate_of or ""])


def main():
    parser = argparse.ArgumentParser(description="AI photo culler")
    parser.add_argument("--dry-run", action="store_true",
                        help="judge and report on screen, but write no folders or files")
    parser.add_argument("--rejudge", action="store_true",
                        help="ignore saved results and call the API again")
    args = parser.parse_args()

    results = load_results()
    photos = sorted(
        p for p in INPUT_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in EXTENSIONS
    )
    print(f"Found {len(photos)} photos" + ("  [DRY RUN]" if args.dry_run else "") + "\n")

    # decisions maps each photo path to (status, duplicate_of)
    decisions = {}

    # Step 1: judge every photo (cached results are reused)
    survivors = []
    failed = cached = 0
    for photo in photos:
        if photo.name in results and not args.rejudge:
            result = results[photo.name]
            cached += 1
            tag = "(cached) "
        else:
            try:
                result = judge_photo(photo)
            except Exception as e:
                print(f"ERROR      {photo.name}: {e}")
                failed += 1
                continue
            results[photo.name] = result
            save_results(results)  # save after every photo so a crash loses nothing
            tag = ""

        if result["keep"]:
            survivors.append(photo)
            print(f"KEEP       {photo.name}  ({result['score']}/10)  {tag}{result['reason']}")
        else:
            decisions[photo] = ("low_rated", None)
            print(f"LOW-RATED  {photo.name}  ({result['score']}/10)  {tag}{result['reason']}")

    # Step 2: among photos judged good, keep only the best of each duplicate group
    print("\nChecking for duplicates...")
    for group in group_duplicates(survivors):
        best = max(group, key=lambda p: (results[p.name]["score"], p.stat().st_size))
        decisions[best] = ("kept", None)
        if len(group) > 1:
            print(f"DUP GROUP  keeping {best.name} ({results[best.name]['score']}/10)")
        for photo in group:
            if photo != best:
                decisions[photo] = ("duplicate", best.name)
                print(f"DUPLICATE  {photo.name}  ({results[photo.name]['score']}/10)  worse copy of {best.name}")

    # Step 3: write the sorted folders and the report
    if not args.dry_run:
        sort_into_folders(decisions)
        write_report(decisions, results)

    counts = {s: sum(1 for st, _ in decisions.values() if st == s)
              for s in ("kept", "low_rated", "duplicate")}
    print(f"\nDone. kept={counts['kept']} low_rated={counts['low_rated']} "
          f"duplicates={counts['duplicate']} errors={failed} cached={cached}")
    if not args.dry_run:
        print(f"Sorted photos are in {OUTPUT_DIR}\\ and the report is {REPORT_FILE}")


if __name__ == "__main__":
    main()