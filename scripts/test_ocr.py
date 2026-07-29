"""
Test script for Phase 2.5 Task C: Real Image OCR Verification
Generates a real PNG image with rendered error text using PIL,
encodes it to base64, and tests app/services/ocr_service.py text extraction.
"""
import base64
import io
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.services.ocr_service import extract_text_from_base64


def audit_ocr():
    # 1. Create a real image with rendered text canvas
    img = Image.new("RGB", (600, 150), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    
    expected_text = "ERROR 0x8004 Microsoft Teams crashed unexpectedly"
    d.text((20, 40), expected_text, fill=(0, 0, 0))

    # 2. Save image bytes to PNG buffer
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    raw_bytes = buf.getvalue()
    b64_str = base64.b64encode(raw_bytes).decode("utf-8")

    # Save PNG to disk for reference
    img_path = ROOT / "eval" / "test_screenshot.png"
    img_path.parent.mkdir(parents=True, exist_ok=True)
    img_path.write_bytes(raw_bytes)
    print(f"Generated real test image: {img_path} ({len(raw_bytes)} bytes)")

    # 3. Pass to OCR service
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
