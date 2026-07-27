"""
Database seeding script for v0.2.0:
Populates IssueCluster and QAMemory tables with embeddings computed from eval/data/tickets-labeled.csv,
and trains the scikit-learn fallback classifier.
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.database import SessionLocal, init_db
from app.models.ticket import IssueCluster, QAMemory
from app.services.classifier_service import compute_embedding, fit_fallback_classifier

CSV_PATH = ROOT / "eval" / "data" / "tickets-labeled.csv"

PLAYBOOK_STEPS = {
    "NET_VPN_DISCONNECT": [
        "Restart the VPN client and reconnect to the preferred corporate gateway.",
        "Clear saved VPN profile and re-import the enterprise profile from IT portal.",
        "Switch from Wi-Fi to wired network if wireless signal is drop-prone.",
    ],
    "MAIL_OUTLOOK_SYNC": [
        "Run Outlook in Safe Mode (outlook.exe /safe), then restart normally.",
        "Repair Office installation via Control Panel / Apps & Features.",
        "Verify Exchange account credentials and MFA authentication prompts.",
    ],
    "ACC_PASSWORD_RESET": [
        "Use corporate self-service password portal; ensure CAPS LOCK is off.",
        "If AD lockout occurs, wait 15 minutes or contact helpdesk for unlock.",
        "Re-enroll MFA security tokens if prompt displays security defaults error.",
    ],
    "HW_PRINT_SPOOLER": [
        "Clear local print queue (%systemroot%\\System32\\spool\\PRINTERS) and restart Print Spooler service.",
        "Reinstall network printer driver from corporate portal.",
        "Verify printer IP address and spooler port settings.",
    ],
    "APP_TEAMS_CRASH": [
        "Fully quit Teams (system tray), clear cache %appdata%\\Microsoft\\Teams, and relaunch.",
        "Update Microsoft Teams and Windows to latest build.",
        "Use Teams Web Client as temporary workaround while repairing desktop app.",
    ],
    "UNKNOWN_ESCALATION": [
        "Collect exact error text, timestamp, and device name.",
        "Attach logs or a screenshot of the full error window.",
        "Route to L2 support if issue blocks work.",
    ],
}


def seed():
    print("Initializing database schema...")
    init_db()

    db = SessionLocal()
    try:
        print(f"Reading seed dataset from {CSV_PATH}...")
        rows: list[tuple[str, str]] = []
        with CSV_PATH.open(encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append((row["text"], row["expected_label"]))

        print(f"Found {len(rows)} labeled seed tickets. Clearing existing cluster records...")
        db.query(IssueCluster).delete()
        db.query(QAMemory).delete()
        db.commit()

        seed_samples = []

        print("Computing embeddings and populating IssueCluster table...")
        for text, category in rows:
            steps = PLAYBOOK_STEPS.get(category, PLAYBOOK_STEPS["UNKNOWN_ESCALATION"])
            emb = compute_embedding(text)

            cluster = IssueCluster(
                category=category,
                example_text=text,
                embedding=emb,
                suggested_steps=steps,
            )
            db.add(cluster)
            seed_samples.append((text, category, steps))

        db.commit()
        print(f"Successfully seeded {len(rows)} IssueCluster entries into PostgreSQL/SQLite.")

        print("Training scikit-learn fallback classifier...")
        fit_fallback_classifier(seed_samples)
        print("Scikit-learn fallback classifier ready.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
