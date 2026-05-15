import hashlib
import re


def normalize_ticket_text(raw: str) -> str:
    text = re.sub(r"\s+", " ", raw)
    text = re.sub(r"[^\w\s.,;:!?'\"()-]", " ", text, flags=re.UNICODE)
    return text.strip()[:8000]


def screenshot_ocr_hint(image_base64: str | None) -> str | None:
    if not image_base64:
        return None
    return (
        "[Screenshot attached — OCR pending; using subject/body cues only for this demo.]"
    )


def build_feature_text(
    text: str = "",
    image_base64: str | None = None,
    log_snippet: str | None = None,
) -> tuple[str, bool, str | None]:
    has_screenshot = bool(image_base64 and len(image_base64) > 40)
    ocr_hint = screenshot_ocr_hint(image_base64)
    parts = [text, log_snippet or "", ocr_hint or ""]
    combined = normalize_ticket_text(" \n ".join(p for p in parts if p))
    return combined, has_screenshot, ocr_hint


def noise_penalty(text: str) -> float:
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    return (digest[0] % 7) / 100.0
