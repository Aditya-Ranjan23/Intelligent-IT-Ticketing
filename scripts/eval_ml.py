"""Offline classifier eval against eval/data/tickets-labeled.csv"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ml.pipeline import run_ml_pipeline

CSV = ROOT / "eval" / "data" / "tickets-labeled.csv"


def main() -> None:
    rows: list[tuple[str, str]] = []
    with CSV.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append((row["text"], row["expected_label"]))

    top1 = 0
    mismatches: list[str] = []
    for text, expected in rows:
        got = run_ml_pipeline(text=text).classification
        if got == expected:
            top1 += 1
        else:
            mismatches.append(f"expected {expected} got {got} | {text[:60]}")

    acc = top1 / len(rows) if rows else 0.0
    print(f"Offline eval: {top1}/{len(rows)} top-1 = {acc * 100:.1f}%")
    if mismatches:
        print("Mismatches:")
        for m in mismatches:
            print(" -", m)
    if acc < 0.8:
        print("Accuracy below 80% on this slice.", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
