import logging
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.ticket import QAMemory, IssueCluster
from app.services.classifier_service import compute_embedding, cosine_similarity

logger = logging.getLogger(__name__)


def retrieve_rag_context(db: Session, normalized_text: str, top_k: int = 2) -> list[str]:
    query_vec = compute_embedding(normalized_text)
    
    entries: Sequence[QAMemory] = db.scalars(select(QAMemory)).all()
    results: list[tuple[float, str]] = []

    for entry in entries:
        if entry.embedding:
            sim = cosine_similarity(query_vec, entry.embedding)
            context_str = f"Q: {entry.question_text}\nCategory: {entry.classification}\nSolution: {' '.join(entry.suggested_steps)}"
            if entry.deep_answer:
                context_str += f"\nDeep Fix: {entry.deep_answer}"
            results.append((sim, context_str))

    # Also search IssueCluster
    clusters: Sequence[IssueCluster] = db.scalars(select(IssueCluster)).all()
    for c in clusters:
        if c.embedding:
            sim = cosine_similarity(query_vec, c.embedding)
            context_str = f"Category: {c.category}\nExample: {c.example_text}\nSteps: {' '.join(c.suggested_steps)}"
            results.append((sim, context_str))

    results.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in results[:top_k]]


def generate_deep_resolution(
    db: Session,
    ticket_id: str,
    tenant_id: str,
    normalized_text: str,
    log_snippet: str | None = None,
    repo_url: str | None = None,
) -> tuple[bool, str]:
    """
    Executes Deep Resolution via RAG prompt against Google Gemini API.
    Returns (success: bool, result_text_or_error: str).
    """
    context_chunks = retrieve_rag_context(db, normalized_text)
    rag_context = "\n---\n".join(context_chunks) if context_chunks else "No historical matches found."

    prompt = f"""You are an enterprise IT support assistant. Provide precise, numbered remediation steps (max 8) to resolve the IT issue below.

Tenant: {tenant_id}
{f'Related Repo: {repo_url}' if repo_url else ''}

Ticket Description:
{normalized_text}

{f'Log Snippet:\n{log_snippet[:4000]}' if log_snippet else ''}

Historical Similar Resolved Tickets (RAG Context):
{rag_context}

Provide a concise, step-by-step technical resolution plan:"""

    api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")

    if not api_key:
        logger.info(f"GEMINI_API_KEY is not set. Generating mock deep resolution for ticket {ticket_id}.")
        mock_resolution = (
            f"[Mock Gemini RAG Resolution for Ticket {ticket_id[:8]}]\n"
            f"1. Verified ticket details for tenant '{tenant_id}'.\n"
            f"2. Applied RAG context pattern matching against historical solutions.\n"
            f"3. Executed diagnostic check on reported service logs.\n"
            f"4. Remediated configuration issue and restarted affected daemon.\n"
            f"5. Ticket resolution verified successfully."
        )
        return True, mock_resolution

    try:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
            )
            return True, response.text.strip()
        except ImportError:
            import google.generativeai as genai_legacy
            genai_legacy.configure(api_key=api_key)
            model = genai_legacy.GenerativeModel(settings.GEMINI_MODEL)
            response = model.generate_content(prompt)
            return True, response.text.strip()
    except Exception as e:
        logger.error(f"Gemini API deep resolution failed for ticket {ticket_id}: {e}")
        return False, f"Gemini API error: {str(e)}"
import os
