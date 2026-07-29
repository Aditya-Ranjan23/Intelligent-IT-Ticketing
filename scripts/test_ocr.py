"""
Test script for Phase 2.5 Task C: Real Image OCR Verification
Reads eval/test_screenshot.png static fixture from disk,
encodes it to base64, and tests app/services/ocr_service.py text extraction.
"""
import base64
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.services.ocr_service import extract_text_from_base64


def audit_ocr():
    img_path = ROOT / "eval" / "test_screenshot.png"
    raw_bytes = img_path.read_bytes()
    b64_str = base64.b64encode(raw_bytes).decode("utf-8")
    print(f"Read test image fixture: {img_path} ({len(raw_bytes)} bytes)")

    expected_text = "ERROR 0x8004 Microsoft Teams crashed unexpectedly"
    extracted_text, has_screenshot = extract_text_from_base64(b64_str)
    
    print("\n" + "="*50)
    print("OCR AUDIT RESULTS:")
    print(f"Has Screenshot Flag: {has_screenshot}")
    print(f"Expected Text: '{expected_text}'")
    print(f"Extracted Text: '{extracted_text}'")
    print("="*50)

    is_match = bool(extracted_text and "ERROR" in extracted_text and "Teams" in extracted_text)
    print(f"Matches Expected Content: {'Yes' if is_match else 'No / Partial'}")
    return is_match, extracted_text


if __name__ == "__main__":
    audit_ocr()
