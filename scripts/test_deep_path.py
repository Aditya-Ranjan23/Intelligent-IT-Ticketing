"""
Test script for Phase 2.5 Task B: Deep Resolution Path Audit
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv()

from app.core.database import SessionLocal, init_db
from app.services.llm_service import generate_deep_resolution

def audit_deep_path():
    key = os.environ.get("GEMINI_API_KEY")
    is_set = bool(key and len(key.strip()) > 5)
    print(f"GEMINI_API_KEY set: {is_set}")

    init_db()
    db = SessionLocal()
    try:
        ticket_id = "test-audit-ticket-12345"
        success, text = generate_deep_resolution(
            db=db,
            ticket_id=ticket_id,
            tenant_id="audit-tenant",
            normalized_text="The SAP ERP system throws memory access violation error code 0x99231.",
            log_snippet="ERROR 2026-07-29 09:45:00 - Memory access violation in SAP module fin_trans.dll",
        )
        print(f"Deep Resolution Execution Success: {success}")
        print("Captured Deep Resolution Text:\n" + "-"*40)
        print(text)
        print("-" * 40)
        print(f"Mode Exercised: {'Live API' if is_set else 'Mock Fallback'}")
        return is_set, success, text
    finally:
        db.close()

if __name__ == "__main__":
    audit_deep_path()
