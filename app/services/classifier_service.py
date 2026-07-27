import re
import logging
from dataclasses import dataclass
from typing import Sequence

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.ticket import IssueCluster, QAMemory

logger = logging.getLogger(__name__)

# Global lazy-loaded embedding model and scikit-learn fallback classifier
_model: SentenceTransformer | None = None
_tfidf_vectorizer: TfidfVectorizer | None = None
_fallback_clf: LogisticRegression | None = None


def get_embedding_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info(f"Loading sentence-transformers model '{settings.EMBEDDING_MODEL_NAME}'...")
        _model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
    return _model


def compute_embedding(text: str) -> list[float]:
    model = get_embedding_model()
    vec = model.encode(text, convert_to_numpy=True)
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()


def normalize_text(raw: str) -> str:
    text = re.sub(r"\s+", " ", raw)
    text = re.sub(r"[^\w\s.,;:!?'\"()-]", " ", text, flags=re.UNICODE)
    return text.strip()[:8000]


def fit_fallback_classifier(samples: list[tuple[str, str, list[str]]]) -> None:
    """
    Fits the scikit-learn TF-IDF + LogisticRegression fallback classifier on seed samples.
    samples: list of (text, category, suggested_steps)
    """
    global _tfidf_vectorizer, _fallback_clf
    if not samples:
        return

    texts = [s[0] for s in samples]
    labels = [s[1] for s in samples]

    _tfidf_vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    X = _tfidf_vectorizer.fit_transform(texts)

    _fallback_clf = LogisticRegression(C=1.0, max_iter=200)
    _fallback_clf.fit(X, labels)
    logger.info(f"Fallback scikit-learn classifier trained on {len(samples)} samples.")


@dataclass
class ClassificationResult:
    classification: str
    confidence: float
    suggested_steps: list[str]
    normalized_text: str
    has_screenshot: bool
    ocr_text: str | None = None


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    a = np.array(vec_a, dtype=np.float32)
    b = np.array(vec_b, dtype=np.float32)
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot / (norm_a * norm_b))


def classify_ticket(
    db: Session,
    text: str = "",
    ocr_text: str | None = None,
    log_snippet: str | None = None,
    has_screenshot: bool = False,
) -> ClassificationResult:
    """
    Hybrid classification:
    1. Sentence-Transformers Vector Similarity Search on issue_clusters / db.
    2. Scikit-learn TF-IDF + LogisticRegression Fallback if vector similarity is below threshold.
    """
    parts = [text, ocr_text or "", log_snippet or ""]
    combined = normalize_text(" \n ".join(p for p in parts if p))

    if not combined:
        return ClassificationResult(
            classification="UNKNOWN_ESCALATION",
            confidence=0.20,
            suggested_steps=[
                "Collect exact error text, timestamp, and device name.",
                "Attach logs or a screenshot of the full error window.",
                "Route to L2 support.",
            ],
            normalized_text="",
            has_screenshot=has_screenshot,
            ocr_text=ocr_text,
        )

    # 1. Primary: Vector embedding computation & cluster search
    query_vec = compute_embedding(combined)

    clusters: Sequence[IssueCluster] = db.scalars(select(IssueCluster)).all()

    best_cluster: IssueCluster | None = None
    best_similarity: float = 0.0

    for cluster in clusters:
        if cluster.embedding:
            sim = cosine_similarity(query_vec, cluster.embedding)
            if sim > best_similarity:
                best_similarity = sim
                best_cluster = cluster

    # If embedding similarity is strong (>= 0.65)
    if best_cluster and best_similarity >= 0.65:
        # Scale confidence nicely up to 0.98
        conf = min(0.98, max(0.68, best_similarity))
        return ClassificationResult(
            classification=best_cluster.category,
            confidence=conf,
            suggested_steps=best_cluster.suggested_steps or [],
            normalized_text=combined,
            has_screenshot=has_screenshot,
            ocr_text=ocr_text,
        )

    # 2. Fallback: Scikit-learn TF-IDF classifier
    if _tfidf_vectorizer and _fallback_clf:
        try:
            X_test = _tfidf_vectorizer.transform([combined])
            probs = _fallback_clf.predict_proba(X_test)[0]
            max_idx = np.argmax(probs)
            pred_label = str(_fallback_clf.classes_[max_idx])
            fallback_conf = float(probs[max_idx])

            if fallback_conf > 0.40 and pred_label != "UNKNOWN_ESCALATION":
                # Find default steps for predicted label
                matched_steps = []
                for c in clusters:
                    if c.category == pred_label:
                        matched_steps = c.suggested_steps
                        break
                return ClassificationResult(
                    classification=pred_label,
                    confidence=min(0.85, max(0.55, fallback_conf * 0.9)),
                    suggested_steps=matched_steps or ["Check system logs and retry action."],
                    normalized_text=combined,
                    has_screenshot=has_screenshot,
                    ocr_text=ocr_text,
                )
        except Exception as e:
            logger.warning(f"Fallback classifier inference failed: {e}")

    # Fallback to UNKNOWN_ESCALATION
    return ClassificationResult(
        classification="UNKNOWN_ESCALATION",
        confidence=0.35,
        suggested_steps=[
            "Collect exact error text, timestamp, and device name.",
            "Attach logs or a screenshot of the full error window.",
            "Route to L2 support if no playbook matched.",
        ],
        normalized_text=combined,
        has_screenshot=has_screenshot,
        ocr_text=ocr_text,
    )
