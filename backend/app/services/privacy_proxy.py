"""VPMA Privacy Proxy — PII detection, anonymization, and re-identification.

Three detection layers:
1. Regex patterns (email, phone, URL) — deterministic, fast
2. spaCy NER (PERSON, ORG, GPE, PRODUCT) — ML-based, context-aware
3. Custom sensitive terms (user-defined from Settings)

Flow: detect_pii(text) → anonymize(text) → LLM call → reidentify(response)
"""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

import spacy

from app.services.database import VPMA_DIR

# Load spaCy model once at module level
_nlp: Optional[spacy.language.Language] = None

# Entity types we extract from spaCy NER
SPACY_ENTITY_LABELS = {"PERSON", "ORG", "GPE", "PRODUCT"}

# Entities below this confidence are filtered out (not anonymized)
MIN_CONFIDENCE_THRESHOLD = 0.75

# Minimum entity text length — skip very short detections (e.g., "I.")
MIN_ENTITY_LENGTH = 2

# Words that spaCy en_core_web_sm commonly misclassifies as named entities
# in conversational text (transcripts, meeting notes).  Case-insensitive.
NER_STOPLIST = frozenset(
    {
        # Interjections / conversational words misclassified as PERSON
        "hey",
        "hi",
        "hmm",
        "hm",
        "oh",
        "yeah",
        "yep",
        "nope",
        "jeez",
        "ok",
        "okay",
        "sure",
        "thanks",
        "bye",
        "hello",
        "wow",
        "oops",
        "ugh",
        "um",
        "uh",
        "ah",
        "standup",
        # Common words misclassified as ORG
        "sms",
        "ui",
        "ux",
        "api",
        "qa",
        "hr",
        "it",
        "ai",
        "ml",
        "pm",
        "am",
        "eta",
        "eod",
        "eow",
        "asap",
        "tbd",
        "tba",
        "congratulations",
        "congrats",
        # Common words misclassified as GPE
        "colleague",
        "remote",
        "hybrid",
        "onsite",
        # Common words misclassified as PRODUCT
        "reschedule",
        "discovery",
        "standup",
        "retro",
        "sprint",
    }
)

# Token format: <TYPE_N> e.g., <PERSON_1>, <EMAIL_2>
TOKEN_PATTERN = re.compile(r"<(PERSON|ORG|GPE|PRODUCT|EMAIL|PHONE|URL|CUSTOM)_(\d+)>")

# LLMs sometimes strip angle brackets, producing bare tokens like ORG_88.
# This pattern catches those so reidentify() can still replace them.
BARE_TOKEN_PATTERN = re.compile(
    r"(?<![<\w])(PERSON|ORG|GPE|PRODUCT|EMAIL|PHONE|URL|CUSTOM)_(\d+)(?![>\w])"
)

# Audit log location — co-located with the rest of the project data
AUDIT_LOG_PATH = VPMA_DIR / "privacy" / "audit_log.jsonl"


def _get_nlp() -> spacy.language.Language:
    """Lazy-load spaCy model (avoids slow import at startup if unused)."""
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp


# ============================================================
# DATA STRUCTURES
# ============================================================


@dataclass
class DetectedEntity:
    """A single PII entity found in text."""

    text: str  # The original text span ("John Smith")
    entity_type: str  # "PERSON", "ORG", "EMAIL", "PHONE", "URL", "GPE", "PRODUCT", "CUSTOM"
    source: str  # "regex", "ner", "custom"
    start: int  # Character offset in original text
    end: int  # Character offset end
    confidence: float = 1.0  # 0.0-1.0, regex/custom = 1.0, NER varies


@dataclass
class DetectionResult:
    """Result of running all detection layers on a text."""

    entities: list[DetectedEntity] = field(default_factory=list)
    overall_confidence: float = 1.0


@dataclass
class AnonymizeResult:
    """Result of anonymizing text."""

    anonymized_text: str
    entities: list[DetectedEntity] = field(default_factory=list)
    token_map: dict[str, str] = field(default_factory=dict)  # token → original
    overall_confidence: float = 1.0


# ============================================================
# LAYER 1: REGEX DETECTION (Task 3)
# ============================================================

REGEX_PATTERNS = {
    "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "PHONE": re.compile(r"(?<!\w)(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    "URL": re.compile(r"https?://[^\s<>\"')\]]+"),
}


def detect_regex(text: str) -> list[DetectedEntity]:
    """Detect PII using regex patterns (emails, phones, URLs)."""
    entities = []
    for entity_type, pattern in REGEX_PATTERNS.items():
        for match in pattern.finditer(text):
            entities.append(
                DetectedEntity(
                    text=match.group(),
                    entity_type=entity_type,
                    source="regex",
                    start=match.start(),
                    end=match.end(),
                    confidence=1.0,
                )
            )
    return entities


def detect_custom_terms(text: str, custom_terms: list[str]) -> list[DetectedEntity]:
    """Detect user-defined sensitive terms (case-insensitive)."""
    entities = []
    text_lower = text.lower()
    for term in custom_terms:
        if not term.strip():
            continue
        term_lower = term.strip().lower()
        start = 0
        while True:
            idx = text_lower.find(term_lower, start)
            if idx == -1:
                break
            # Use the original-case text from the input
            original_text = text[idx : idx + len(term.strip())]
            entities.append(
                DetectedEntity(
                    text=original_text,
                    entity_type="CUSTOM",
                    source="custom",
                    start=idx,
                    end=idx + len(term.strip()),
                    confidence=1.0,
                )
            )
            start = idx + 1
    return entities


# ============================================================
# LAYER 2: SPACY NER DETECTION (Task 4)
# ============================================================


def detect_ner(text: str) -> list[DetectedEntity]:
    """Detect PII using spaCy Named Entity Recognition.

    Applies three filters to reduce false positives:
    1. Minimum entity length (skip very short spans like "I.")
    2. Stoplist of common words that en_core_web_sm misclassifies
    3. Confidence threshold — skip low-confidence detections
    """
    nlp = _get_nlp()
    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        if ent.label_ not in SPACY_ENTITY_LABELS:
            continue

        stripped = ent.text.strip()

        # Filter: minimum length
        if len(stripped) < MIN_ENTITY_LENGTH:
            continue

        # Filter: stoplist (case-insensitive)
        if stripped.lower() in NER_STOPLIST:
            continue

        confidence = _estimate_ner_confidence(ent)

        # Filter: confidence threshold
        if confidence < MIN_CONFIDENCE_THRESHOLD:
            continue

        entities.append(
            DetectedEntity(
                text=ent.text,
                entity_type=ent.label_,
                source="ner",
                start=ent.start_char,
                end=ent.end_char,
                confidence=confidence,
            )
        )
    return entities


def _estimate_ner_confidence(ent: spacy.tokens.Span) -> float:
    """Estimate confidence for a spaCy entity.

    spaCy's en_core_web_sm doesn't provide per-entity confidence scores.
    We use heuristics:
    - Multi-word entities (e.g. "John Smith") → higher confidence
    - Single common words (e.g. "Apple") → lower confidence
    - Entities with capitalization patterns → higher confidence
    """
    text = ent.text.strip()

    # Multi-word entities are typically more reliable
    word_count = len(text.split())
    if word_count >= 2:
        return 0.90

    # Single word: check if it's a common word that might be misclassified
    # (e.g., "Apple" as ORG vs. fruit)
    if text[0].isupper() and len(text) > 1:
        return 0.80

    # Single lowercase or very short — low confidence
    return 0.60


# ============================================================
# COMBINED DETECTION PIPELINE
# ============================================================


def detect_pii(
    text: str,
    custom_terms: Optional[list[str]] = None,
    use_ner: bool = True,
) -> DetectionResult:
    """Run all detection layers and merge results.

    Args:
        text: Input text to scan for PII.
        custom_terms: User-defined sensitive terms from Settings.
        use_ner: Whether to run spaCy NER (can be disabled for speed).

    Returns:
        DetectionResult with deduplicated entities and overall confidence.
    """
    if custom_terms is None:
        custom_terms = []

    all_entities: list[DetectedEntity] = []

    # Layer 1: Regex (always runs)
    all_entities.extend(detect_regex(text))

    # Layer 2: Custom terms (if any defined)
    if custom_terms:
        all_entities.extend(detect_custom_terms(text, custom_terms))

    # Layer 3: spaCy NER
    if use_ner:
        all_entities.extend(detect_ner(text))

    # Deduplicate overlapping entities (prefer longer matches, higher confidence)
    merged = _deduplicate_entities(all_entities)

    # Calculate overall confidence
    overall_confidence = _calculate_overall_confidence(merged)

    return DetectionResult(entities=merged, overall_confidence=overall_confidence)


def _deduplicate_entities(entities: list[DetectedEntity]) -> list[DetectedEntity]:
    """Remove overlapping detections, keeping the best match.

    When two entities overlap:
    - Prefer longer spans (more specific)
    - If same length, prefer higher confidence
    - If same length and confidence, prefer regex/custom over NER (deterministic)

    Also boosts confidence when multiple methods agree on the same span.
    """
    if not entities:
        return []

    # Sort by start position, then by length descending
    sorted_entities = sorted(entities, key=lambda e: (e.start, -(e.end - e.start)))

    # Group overlapping entities
    groups: list[list[DetectedEntity]] = []
    current_group: list[DetectedEntity] = [sorted_entities[0]]

    for entity in sorted_entities[1:]:
        # Check if this entity overlaps with any in the current group
        if entity.start < current_group[-1].end:
            current_group.append(entity)
        else:
            groups.append(current_group)
            current_group = [entity]
    groups.append(current_group)

    # From each group, pick the best entity
    result = []
    for group in groups:
        if len(group) == 1:
            result.append(group[0])
            continue

        # Multiple detections for same/overlapping span — boost confidence
        # and pick the longest/best one
        sources = {e.source for e in group}
        best = max(
            group,
            key=lambda e: (
                e.end - e.start,  # longer is better
                e.confidence,  # higher confidence
                e.source != "ner",  # prefer deterministic
            ),
        )

        # Boost confidence if detected by multiple methods
        if len(sources) > 1:
            best.confidence = min(best.confidence + 0.15, 1.0)

        result.append(best)

    return result


def _calculate_overall_confidence(entities: list[DetectedEntity]) -> float:
    """Calculate overall confidence score for a detection run.

    Based on PRD: confidence = multi_method_count / total_count
    High: All entities detected by multiple methods
    Low: Ambiguous entities (NER flagged common words)
    """
    if not entities:
        return 1.0  # No PII found = fully confident in that assessment

    # Average confidence across all entities
    avg_confidence = sum(e.confidence for e in entities) / len(entities)
    return round(avg_confidence, 2)


# ============================================================
# ANONYMIZE & REIDENTIFY (Task 5)
# ============================================================


async def anonymize(
    text: str,
    custom_terms: Optional[list[str]] = None,
    use_ner: bool = True,
) -> AnonymizeResult:
    """Anonymize PII in text by replacing with tokens (<PERSON_1>, etc.).

    Flow:
    1. Detect PII using all layers (regex + NER + custom terms)
    2. For each entity, look up existing vault token or create a new one
    3. Replace entities in text (right-to-left to preserve offsets)
    4. Write to privacy audit log

    Args:
        text: Input text to anonymize.
        custom_terms: User-defined sensitive terms.
        use_ner: Whether to run spaCy NER.

    Returns:
        AnonymizeResult with anonymized text, entities, token map, and confidence.
    """
    from app.services.crud import (
        get_all_pii_mappings,
        lookup_pii_by_original,
        store_pii_mapping,
    )

    # Step 1: Detect PII
    result = detect_pii(text, custom_terms=custom_terms, use_ner=use_ner)

    if not result.entities:
        return AnonymizeResult(
            anonymized_text=text,
            overall_confidence=result.overall_confidence,
        )

    # Step 2: Determine next token numbers from existing vault
    all_mappings = await get_all_pii_mappings()
    type_counters: dict[str, int] = {}
    for mapping in all_mappings:
        match = TOKEN_PATTERN.match(mapping.token)
        if match:
            etype = match.group(1)
            num = int(match.group(2))
            type_counters[etype] = max(type_counters.get(etype, 0), num)

    # Step 3: Assign tokens (reuse token for same text value)
    text_to_token: dict[str, str] = {}
    token_map: dict[str, str] = {}

    for entity in result.entities:
        if entity.text in text_to_token:
            continue  # Already assigned a token for this exact text

        existing = await lookup_pii_by_original(entity.text)
        if existing:
            text_to_token[entity.text] = existing.token
            token_map[existing.token] = entity.text
        else:
            etype = entity.entity_type
            next_num = type_counters.get(etype, 0) + 1
            type_counters[etype] = next_num
            token = f"<{etype}_{next_num}>"
            text_to_token[entity.text] = token
            token_map[token] = entity.text
            await store_pii_mapping(token, entity.text, entity.entity_type)

    # Step 4: Replace in text (right-to-left to preserve character offsets)
    anonymized = text
    for entity in sorted(result.entities, key=lambda e: e.start, reverse=True):
        token = text_to_token[entity.text]
        anonymized = anonymized[: entity.start] + token + anonymized[entity.end :]

    # Step 5: Audit log
    _write_audit_log(
        "anonymize",
        {
            "entity_count": len(result.entities),
            "unique_entities": len(text_to_token),
            "entity_types": sorted(set(e.entity_type for e in result.entities)),
            "confidence": result.overall_confidence,
        },
    )

    return AnonymizeResult(
        anonymized_text=anonymized,
        entities=result.entities,
        token_map=token_map,
        overall_confidence=result.overall_confidence,
    )


async def reidentify(text: str) -> str:
    """Replace anonymization tokens with original values from the PII vault.

    Finds all <TYPE_N> tokens in text and replaces them with the original
    values stored in the vault. Tokens with no vault match are replaced with
    a human-readable fallback (e.g., "a team member") instead of leaking
    the raw token to the user.

    Args:
        text: Anonymized text containing tokens like <PERSON_1>.

    Returns:
        Text with tokens replaced by original values.
    """
    from app.services.crud import get_pii_mapping

    # Find all unique tokens in text (bracketed and bare forms)
    token_strings = set()
    for match in TOKEN_PATTERN.finditer(text):
        token_strings.add(match.group(0))

    bare_tokens: dict[str, str] = {}  # bare form → bracketed form
    for match in BARE_TOKEN_PATTERN.finditer(text):
        bare = match.group(0)
        bracketed = f"<{bare}>"
        # Only treat as bare token if the bracketed form isn't already in text
        if bracketed not in text:
            bare_tokens[bare] = bracketed

    if not token_strings and not bare_tokens:
        return text

    # Load mappings from vault for bracketed tokens
    mappings: dict[str, str] = {}
    unmatched: list[str] = []
    for token in token_strings:
        mapping = await get_pii_mapping(token)
        if mapping:
            mappings[token] = mapping.original_value
        else:
            unmatched.append(token)

    # Load mappings for bare tokens (look up the bracketed form in vault)
    bare_mappings: dict[str, str] = {}
    for bare, bracketed in bare_tokens.items():
        mapping = await get_pii_mapping(bracketed)
        if mapping:
            bare_mappings[bare] = mapping.original_value
        else:
            unmatched.append(bare)

    # Replace bracketed tokens with originals; use fallback for unmatched
    def replace_token(match: re.Match) -> str:
        token = match.group(0)
        if token in mappings:
            return mappings[token]
        entity_type = match.group(1)
        return _UNMATCHED_TOKEN_FALLBACKS.get(entity_type, "[redacted]")

    result = TOKEN_PATTERN.sub(replace_token, text)

    # Replace bare tokens with originals; use fallback for unmatched
    def replace_bare_token(match: re.Match) -> str:
        bare = match.group(0)
        if bare in bare_mappings:
            return bare_mappings[bare]
        entity_type = match.group(1)
        return _UNMATCHED_TOKEN_FALLBACKS.get(entity_type, "[redacted]")

    result = BARE_TOKEN_PATTERN.sub(replace_bare_token, result)

    _write_audit_log(
        "reidentify",
        {
            "token_count": len(token_strings) + len(bare_tokens),
            "reidentified_count": len(mappings) + len(bare_mappings),
            "unmatched_count": len(unmatched),
        },
    )

    return result


# Fallback labels when a PII token has no vault match (e.g. LLM fabricated
# a token number that was never created during anonymization).
_UNMATCHED_TOKEN_FALLBACKS = {
    "PERSON": "[a team member]",
    "ORG": "[an organization]",
    "GPE": "[a location]",
    "PRODUCT": "[a product]",
    "EMAIL": "[an email]",
    "PHONE": "[a phone number]",
    "URL": "[a URL]",
    "CUSTOM": "[redacted]",
}


def _write_audit_log(action: str, details: dict) -> None:
    """Append an entry to the privacy audit log (JSONL format).

    Log file: ~/VPMA/privacy/audit_log.jsonl
    """
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        **details,
    }

    with open(AUDIT_LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")
