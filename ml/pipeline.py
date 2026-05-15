from dataclasses import dataclass

from ml.classifier import classify_ticket
from ml.preprocess import build_feature_text


@dataclass
class MlResult:
    classification: str
    confidence: float
    suggested_steps: list[str]
    normalized_text: str
    has_screenshot: bool
    ocr_hint: str | None = None


def run_ml_pipeline(
    text: str = "",
    image_base64: str | None = None,
    log_snippet: str | None = None,
) -> MlResult:
    combined, has_screenshot, ocr_hint = build_feature_text(
        text=text,
        image_base64=image_base64,
        log_snippet=log_snippet,
    )
    result = classify_ticket(combined)
    return MlResult(
        classification=result.classification,
        confidence=result.confidence,
        suggested_steps=result.suggested_steps,
        normalized_text=combined,
        has_screenshot=has_screenshot,
        ocr_hint=ocr_hint,
    )
