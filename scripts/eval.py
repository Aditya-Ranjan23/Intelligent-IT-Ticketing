"""
Held-out evaluation script for v0.2.0 Python classifier pipeline against eval/data/holdout.csv.
Evaluates model on unseen ticket samples to avoid data leakage artifacts.
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.database import SessionLocal
from app.services.classifier_service import classify_ticket
from scripts.seed_db import seed

HOLDOUT_CSV_PATH = ROOT / "eval" / "data" / "holdout.csv"


def evaluate():
    print("Seeding database vector store exclusively from eval/data/seed.csv...")
    seed()

    db = SessionLocal()
    try:
        rows: list[tuple[str, str]] = []
        with HOLDOUT_CSV_PATH.open(encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append((row["text"], row["expected_label"]))

        top1 = 0
        mismatches: list[str] = []
        category_counts: dict[str, dict[str, int]] = {}

        print(f"\nRunning evaluation on {len(rows)} HELD-OUT ticket samples...")
        for text, expected in rows:
            res = classify_ticket(db=db, text=text)
            got = res.classification

            if expected not in category_counts:
                category_counts[expected] = {"correct": 0, "total": 0}
            category_counts[expected]["total"] += 1

            if got == expected:
                top1 += 1
                category_counts[expected]["correct"] += 1
            else:
                mismatches.append(f"Expected: {expected:<20} | Got: {got:<20} | Conf: {res.confidence:.2f} | Text: {text[:60]}")

        acc = (top1 / len(rows)) * 100.0 if rows else 0.0

        print("\n" + "=" * 60)
        print(f"HELD-OUT EVALUATION RESULT (v0.2.0 Python Classifier):")
        print(f"Top-1 Accuracy on Holdout Set: {top1}/{len(rows)} ({acc:.1f}%)")
        print("=" * 60)

        print("\nPer-Category Breakdown on Holdout Set:")
        for cat, stats in sorted(category_counts.items()):
            cat_acc = (stats["correct"] / stats["total"]) * 100.0 if stats["total"] else 0.0
            print(f"  - {cat:<22}: {stats['correct']}/{stats['total']} ({cat_acc:.1f}%)")

        if mismatches:
            print("\nMismatches:")
            for m in mismatches:
                print("  -", m)

        return acc, top1, len(rows), category_counts, mismatches

    finally:
        db.close()


if __name__ == "__main__":
    evaluate()
