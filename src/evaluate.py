import csv
import json
import sys
from pathlib import Path

RESULTS_FILE = Path("results.json")
LABELS_FILE = Path("labels.csv")


def make_template(force):
    """Write labels.csv with one blank row per judged photo."""
    if LABELS_FILE.exists() and not force:
        print(f"{LABELS_FILE} already exists, so I did not overwrite it.")
        print("Use --template --force to replace it (this erases your labels).")
        return
    results = json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
    with open(LABELS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "keep"])
        for name in sorted(results):
            writer.writerow([name, ""])
    print(f"Wrote {LABELS_FILE} with {len(results)} rows.")
    print("Fill the keep column: 1 = you would keep it, 0 = you would reject it.")


def pct(num, den):
    return f"{100 * num / den:.1f}%" if den else "n/a"


def evaluate():
    if not RESULTS_FILE.exists():
        print("results.json not found. Run: python -m src.main")
        return
    if not LABELS_FILE.exists():
        print("labels.csv not found. Run: python -m src.evaluate --template")
        return

    results = json.loads(RESULTS_FILE.read_text(encoding="utf-8"))

    truth = {}
    with open(LABELS_FILE, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            value = row["keep"].strip().lower()
            if value in ("1", "yes", "y", "true"):
                truth[row["filename"]] = True
            elif value in ("0", "no", "n", "false"):
                truth[row["filename"]] = False  # blank rows are skipped

    tp = fp = fn = tn = 0
    skipped = 0
    disagreements = []
    for name, true_keep in truth.items():
        if name not in results:
            skipped += 1  # labeled but never judged
            continue
        pred = results[name]
        if pred["keep"] and true_keep:
            tp += 1
        elif pred["keep"] and not true_keep:
            fp += 1
            disagreements.append((name, "AI kept, you would reject", pred))
        elif not pred["keep"] and true_keep:
            fn += 1
            disagreements.append((name, "AI rejected, you would keep", pred))
        else:
            tn += 1

    total = tp + fp + fn + tn
    if total == 0:
        print("No photos have both a label and an AI result yet.")
        return

    print(f"Evaluated {total} labeled photos" + (f" ({skipped} labeled but not judged)" if skipped else ""))
    print()
    print("                    You: keep   You: reject")
    print(f"AI kept             {tp:>9}   {fp:>11}")
    print(f"AI rejected         {fn:>9}   {tn:>11}")
    print()
    print(f"Accuracy:           {pct(tp + tn, total)}")
    print(f"Keep recall:        {pct(tp, tp + fn)}   of photos you would keep, how many the AI kept")
    print(f"Keep precision:     {pct(tp, tp + fp)}   of photos the AI kept, how many you would keep")
    print(f"Reject recall:      {pct(tn, tn + fp)}   of photos you would reject, how many the AI caught")
    print(f"Reject precision:   {pct(tn, tn + fn)}   of photos the AI rejected, how many you would reject")

    if disagreements:
        print("\nDisagreements:")
        for name, kind, pred in disagreements:
            print(f"  {name}: {kind} ({pred['score']}/10) {pred['reason']}")


if __name__ == "__main__":
    if "--template" in sys.argv:
        make_template(force="--force" in sys.argv)
    else:
        evaluate()