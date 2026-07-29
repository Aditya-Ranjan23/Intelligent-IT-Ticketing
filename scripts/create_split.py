"""
Deterministic stratified train/holdout split script for Phase 2.5 verification.
Splits eval/data/tickets-labeled.csv into eval/data/seed.csv (~80%) and eval/data/holdout.csv (~20%).
"""
import csv
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "eval" / "data" / "tickets-labeled.csv"
SEED_CSV = ROOT / "eval" / "data" / "seed.csv"
HOLDOUT_CSV = ROOT / "eval" / "data" / "holdout.csv"


def make_split():
    rows_by_cat = defaultdict(list)
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows_by_cat[row["expected_label"]].append(row["text"])

    random.seed(42)  # Deterministic seed

    seed_rows = []
    holdout_rows = []

    for cat, texts in sorted(rows_by_cat.items()):
        # Shuffle deterministically
        shuffled = list(texts)
        random.shuffle(shuffled)
        
        # Hold out ~20% (at least 2 per category)
        n_holdout = max(2, int(round(len(shuffled) * 0.20)))
        n_seed = len(shuffled) - n_holdout

        for t in shuffled[:n_seed]:
            seed_rows.append({"text": t, "expected_label": cat})
        for t in shuffled[n_seed:]:
            holdout_rows.append({"text": t, "expected_label": cat})

    with SEED_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "expected_label"])
        writer.writeheader()
        writer.writerows(seed_rows)

    with HOLDOUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "expected_label"])
        writer.writeheader()
        writer.writerows(holdout_rows)

    print(f"Created seed.csv ({len(seed_rows)} rows) and holdout.csv ({len(holdout_rows)} rows).")


if __name__ == "__main__":
    make_split()
