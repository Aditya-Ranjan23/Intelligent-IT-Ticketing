import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ml.memory.qa_store import upsert_answer
from ml.playbooks import PLAYBOOK

SEEDS = [
    ("vpn keeps disconnecting anyconnect", "NET_VPN_DISCONNECT"),
    ("outlook mailbox not syncing exchange", "MAIL_OUTLOOK_SYNC"),
    ("forgot password cannot sign in locked account", "ACC_PASSWORD_RESET"),
    ("printer spooler stuck print queue", "HW_PRINT_SPOOLER"),
    ("microsoft teams crashes on startup", "APP_TEAMS_CRASH"),
]


def main() -> None:
    for question, class_id in SEEDS:
        pb = next(p for p in PLAYBOOK if p.id == class_id)
        upsert_answer(
            question_text=question,
            classification=pb.id,
            suggested_steps=list(pb.suggested_steps),
        )
    print(f"Seeded {len(SEEDS)} playbook entries into Q&A memory.")


if __name__ == "__main__":
    main()
