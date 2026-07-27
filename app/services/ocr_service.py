import base64
import io
import logging
from PIL import Image

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

logger = logging.getLogger(__name__)


def extract_text_from_base64(image_base64: str | None) -> tuple[str | None, bool]:
    """
    Decodes base64 screenshot image bytes and uses Tesseract OCR to extract text.
    Returns (extracted_text, has_screenshot).
    """
    if not image_base64 or len(image_base64.strip()) < 20:
        return None, False

    try:
        # Strip header if present (e.g. data:image/png;base64,...)
        raw_b64 = image_base64.split(",")[-1].strip()
        img_bytes = base64.b64decode(raw_b64)
        img = Image.open(io.BytesIO(img_bytes))

        if not PYTESSERACT_AVAILABLE:
            logger.warning("pytesseract package not installed.")
            return "[Screenshot decoded — pytesseract package unavailable for OCR.]", True

        try:
            text = pytesseract.image_to_string(img).strip()
            if text:
                return text, True
            return "[Screenshot processed — no readable text extracted via OCR.]", True
        except Exception as ocr_err:
            logger.warning(f"Tesseract OCR execution failed: {ocr_err}")
            return f"[Screenshot attached — OCR execution fallback: {ocr_err}]", True

    except Exception as err:
        logger.error(f"Failed to decode base64 image: {err}")
        return None, False
