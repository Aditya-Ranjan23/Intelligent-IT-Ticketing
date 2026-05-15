from dataclasses import dataclass

from ml.playbooks import PLAYBOOK, UNKNOWN_ESCALATION, UNKNOWN_STEPS, PlaybookEntry
from ml.preprocess import noise_penalty


@dataclass(frozen=True)
class ClassificationResult:
    classification: str
    confidence: float
    suggested_steps: list[str]


def classify_ticket(normalized_text: str) -> ClassificationResult:
    hay = normalized_text.lower()
    best: tuple[PlaybookEntry, int] | None = None

    for entry in PLAYBOOK:
        score = sum(1 for kw in entry.keywords if kw in hay)
        if best is None or score > best[1]:
            best = (entry, score)

    noise_adj = noise_penalty(hay)

    if best and best[1] > 0:
        entry, score = best
        confidence = min(
            0.97,
            max(0.55, entry.base_confidence - noise_adj + score * 0.02),
        )
        return ClassificationResult(
            classification=entry.id,
            confidence=confidence,
            suggested_steps=list(entry.suggested_steps),
        )

    return ClassificationResult(
        classification=UNKNOWN_ESCALATION,
        confidence=max(0.2, 0.45 - noise_adj),
        suggested_steps=list(UNKNOWN_STEPS),
    )
