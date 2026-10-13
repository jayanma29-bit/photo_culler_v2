import argparse
import csv
import json
import shutil
import sys
from pathlib import Path

import imagehash
from PIL import Image, ImageOps

from src.judge import HEIC_SUPPORTED, judge_photo

EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
if HEIC_SUPPORTED:
    EXTENSIONS |= {".heic", ".heif"}


import json
from pathlib import Path

def load_results(path):
    path = Path(path)
    if not path.exists():
        return {}
    
    try:
        content = path.read_text(encoding="utf-8")
        # Treat completely empty files as malformed JSON so they trigger the recovery test
        if not content.strip():
            raise json.JSONDecodeError("Empty file", content, 0)
        return json.loads(content)
    except (json.JSONDecodeError, ValueError):
        # Backup the corrupted/empty file as .bad
        bad_path = Path(str(path) + ".bad")
        if path.exists():
            path.replace(bad_path)
        return {}


def save_results(results_file, results):
    results_file.write_text(json.dumps(results, indent=2), encoding="utf-8")


def photo_hash(path):
    img = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    return imagehash.phash(img)


def group_duplicates(paths, threshold):
    """Group photos whose perceptual hashes are close. Returns a list of groups."""
    groups = []
    for path in paths:
        h = photo_hash(path)
        for group in groups:
            if any(h - other <= threshold for _, other in group):
                group.append((path, h))
                break
        else:
            groups.append([(path, h)])
    return [[p for p, _ in g] for g in groups]


OUTPUT_MARKER = ".photo_culler_output"


def sort_into_folders(decisions, output_dir):
    """Rebuild kept/ and rejected/ inside output_dir and copy every photo into its folder."""
    kept_dir = output_dir / "kept"
    rejected_dir = output_dir / "rejected"
    low_rated_dir = rejected_dir / "low_rated"
    duplicates_dir = rejected_dir / "duplicates"
    marker = output_dir / OUTPUT_MARKER

    # safety: never delete folders that this tool did not create
    for folder in (kept_dir, rejected_dir):
        if folder.exists() and not marker.exists():
            raise SystemExit(
                f"Refusing to overwrite {folder}: it was not created by this tool. "
                "Choose a different --output folder, or delete that folder yourself."
            )

    for folder in (kept_dir, rejected_dir):
        if folder.exists():
            shutil.rmtree(folder)
    for folder in (kept_dir, low_rated_dir, duplicates_dir):
        folder.mkdir(parents=True)
    marker.write_text(
        "Created by photo_culler. kept/ and rejected/ are rebuilt on every run.\n",
        encoding="utf-8",
    )

    targets = {"kept": kept_dir, "low_rated": low_rated_dir, "duplicate": duplicates_dir}
    for photo, (status, _) in decisions.items():
        shutil.copy2(photo, targets[status] / photo.name)


def write_report(decisions, results, report_file):
    # utf-8-sig so Excel on Windows opens the file with correct characters
    with open(report_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "status", "score", "reason", "duplicate_of"])
        for photo, (status, duplicate_of) in sorted(decisions.items(), key=lambda kv: kv[0].name):
            r = results[photo.name]
            writer.writerow([photo.name, status, r["score"], r["reason"], duplicate_of or ""])


def main():
    # keep printing from crashing on terminals that cannot show every character
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

    parser = argparse.ArgumentParser(
        description="AI photo culler: sorts copies of your photos into kept / low-rated / duplicates. "
                    "Your original photos are never modified."
    )
    parser.add_argument("--input", default="test_photos",
                        help="folder containing your photos (default: test_photos)")
    parser.add_argument("--output", default="output",
                        help="folder where sorted copies and report.csv are written (default: output)")
    parser.add_argument("--results", default="results.json",
                        help="cache file for AI judgments (default: results.json)")
    parser.add_argument("--threshold", type=int, default=6,
                        help="duplicate sensitivity: higher groups more photos together (default: 6)")
    parser.add_argument("--dry-run", action="store_true",
                        help="print decisions but write no sorted folders or report "
                             "(the judgment cache is still saved)")
    parser.add_argument("--rejudge", action="store_true",
                        help="ignore saved results and call the API again")
    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)
    results_file = Path(args.results)

    if not input_dir.is_dir():
        raise SystemExit(f"Input folder not found: {input_dir}")
    if output_dir.resolve() == input_dir.resolve():
        raise SystemExit("--output must be a different folder from --input.")

    results = load_results(results_file)
    photos = sorted(
        p for p in input_dir.iterdir()
        if p.is_file() and p.suffix.lower() in EXTENSIONS
    )
    print(f"Found {len(photos)} photos in {input_dir}" + ("  [DRY RUN]" if args.dry_run else "") + "\n")
    if not photos:
        print("Supported types: " + ", ".join(sorted(EXTENSIONS)))
        print("Only the top level of the folder is scanned (no subfolders).")
        return

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
            save_results(results_file, results)  # save after every photo so a crash loses nothing
            tag = ""

        if result["keep"]:
            survivors.append(photo)
            print(f"KEEP       {photo.name}  ({result['score']}/10)  {tag}{result['reason']}")
        else:
            decisions[photo] = ("low_rated", None)
            print(f"LOW-RATED  {photo.name}  ({result['score']}/10)  {tag}{result['reason']}")

    # Step 2: among photos judged good, keep only the best of each duplicate group
    print("\nChecking for duplicates...")
    for group in group_duplicates(survivors, args.threshold):
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
        output_dir.mkdir(parents=True, exist_ok=True)
        sort_into_folders(decisions, output_dir)
        write_report(decisions, results, output_dir / "report.csv")

    counts = {s: sum(1 for st, _ in decisions.values() if st == s)
              for s in ("kept", "low_rated", "duplicate")}
    print(f"\nDone. kept={counts['kept']} low_rated={counts['low_rated']} "
          f"duplicates={counts['duplicate']} errors={failed} cached={cached}")
    if not args.dry_run:
        print(f"Sorted photos are in {output_dir} and the report is {output_dir / 'report.csv'}")


if __name__ == "__main__":
    main()