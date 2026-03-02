"""VPMA Content Quality Gate — semantic dedup and contradiction detection for LPD updates.

Compares proposed LPD updates against existing section content using a single
batched LLM call. Classifies each update as new/duplicate/update/contradiction
to prevent blind auto-apply.

Used by: artifact_sync.py (log_session mode)
Designed to be reusable by: intake.py, return path, manual edits (future)
"""

import json
import logging

from app.models.schemas import LPDUpdate, LPDUpdateClassification
from app.prompts.lpd_prompts import CONTENT_GATE_SYSTEM_PROMPT
from app.services.llm_client import LLMClient, LLMError
from app.services.lpd_manager import get_full_lpd, lpd_exists
from app.services.privacy_proxy import anonymize, reidentify

logger = logging.getLogger(__name__)

VALID_CLASSIFICATIONS = {"new", "duplicate", "update", "contradiction"}
AUTO_APPLY_CLASSIFICATIONS = {"new", "update"}


def _parse_classification_response(
    llm_response: str,
    count: int,
) -> list[dict]:
    """Parse the LLM classification response into a list of classification dicts.

    Args:
        llm_response: Raw LLM output (expected JSON array).
        count: Expected number of classifications.

    Returns:
        List of dicts with 'index', 'classification', 'reason' keys.
        Falls back to all-new on parse failure.
    """
    text = llm_response.strip()

    # Strip markdown code fences if present
    if text.startswith("```"):
        first_newline = text.index("\n")
        text = text[first_newline + 1 :]
    if text.endswith("```"):
        text = text[:-3].rstrip()

    # Find the JSON array
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        logger.warning("No JSON array found in content gate response")
        return [
            {"index": i, "classification": "new", "reason": "Gate parse failure"}
            for i in range(count)
        ]

    json_str = text[start : end + 1]

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.warning("Failed to parse content gate JSON: %s", e)
        return [
            {"index": i, "classification": "new", "reason": "Gate parse failure"}
            for i in range(count)
        ]

    # Validate and normalize
    results = []
    seen_indices: set[int] = set()
    for item in data:
        idx = item.get("index", -1)
        classification = item.get("classification", "new").lower().strip()
        reason = item.get("reason", "")

        if classification not in VALID_CLASSIFICATIONS:
            classification = "new"

        if idx not in seen_indices and 0 <= idx < count:
            seen_indices.add(idx)
            results.append({"index": idx, "classification": classification, "reason": reason})

    # Fill in any missing indices as "new"
    for i in range(count):
        if i not in seen_indices:
            results.append({"index": i, "classification": "new", "reason": "Not classified by LLM"})

    results.sort(key=lambda x: x["index"])
    return results


async def classify_lpd_updates(
    project_id: str,
    lpd_updates: list[LPDUpdate],
    client: LLMClient,
    custom_terms: list[str] | None = None,
) -> tuple[list[LPDUpdate], bool]:
    """Classify each proposed LPD update against existing section content.

    Uses a single batched LLM call for cost efficiency.

    Args:
        project_id: Target project.
        lpd_updates: Proposed updates from log_session parsing.
        client: LLM client to use for comparison.
        custom_terms: Custom sensitive terms for privacy proxy.

    Returns:
        Tuple of (classified_updates, gate_active).
        classified_updates: Same list but with classification field populated.
        gate_active: True if classification was performed, False if fallback.
    """
    if not lpd_updates:
        return lpd_updates, True

    # If no LPD exists, everything is "new"
    if not await lpd_exists(project_id):
        return [
            update.model_copy(
                update={
                    "classification": LPDUpdateClassification(
                        classification="new", reason="No existing project hub"
                    )
                }
            )
            for update in lpd_updates
        ], True

    # Fetch current LPD content
    existing_lpd = await get_full_lpd(project_id)

    # Build comparison payload
    comparisons = []
    for i, update in enumerate(lpd_updates):
        existing_content = existing_lpd.get(update.section, "")
        comparisons.append(
            {
                "index": i,
                "section": update.section,
                "existing_content": existing_content,
                "proposed_content": update.content,
            }
        )

    # Anonymize the comparison payload before LLM call
    comparison_text = json.dumps(comparisons)
    anon_result = await anonymize(comparison_text, custom_terms=custom_terms or [])

    # Single batched LLM call
    try:
        llm_response = await client.call(
            system_prompt=CONTENT_GATE_SYSTEM_PROMPT,
            user_prompt=anon_result.anonymized_text,
            max_tokens=2048,
        )

        # Reidentify PII in the response (reasons may contain entity references)
        llm_response = await reidentify(llm_response)

        # Parse classifications
        classifications = _parse_classification_response(llm_response, len(lpd_updates))

    except LLMError:
        logger.warning("Content gate LLM call failed — falling back to auto-apply all")
        return [
            update.model_copy(
                update={
                    "classification": LPDUpdateClassification(
                        classification="new", reason="Content gate unavailable"
                    )
                }
            )
            for update in lpd_updates
        ], False
    except Exception:
        logger.warning(
            "Unexpected error in content gate — falling back to auto-apply all",
            exc_info=True,
        )
        return [
            update.model_copy(
                update={
                    "classification": LPDUpdateClassification(
                        classification="new", reason="Content gate error"
                    )
                }
            )
            for update in lpd_updates
        ], False

    # Attach classifications to updates
    classified_updates = []
    for i, update in enumerate(lpd_updates):
        cls_data = classifications[i]
        classified_updates.append(
            update.model_copy(
                update={
                    "classification": LPDUpdateClassification(
                        classification=cls_data["classification"],
                        reason=cls_data["reason"],
                    )
                }
            )
        )

    return classified_updates, True
