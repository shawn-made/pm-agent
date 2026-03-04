"""VPMA Deep Strategy — 4-Pass Multi-Artifact Consistency Analysis Engine.

Flow:
1. Anonymize all artifact content via Privacy Proxy
2. Pass 1: Build dependency graph (LLM)
3. Pass 2: Detect inconsistencies (LLM)
4. Pass 3: Generate proposed updates (LLM)
5. Pass 4: Cross-validate consistency (LLM)
6. Reidentify PII in all outputs
7. Log session to database
"""

import json
import logging
from pathlib import Path

from app.models.schemas import (
    DeepStrategyApplyRequest,
    DeepStrategyApplyResponse,
    DeepStrategyArtifact,
    DeepStrategyResponse,
    DeepStrategySummary,
    DependencyEdge,
    DependencyGraph,
    Inconsistency,
    ProposedUpdate,
    SessionCreate,
    ValidationCheck,
)
from app.prompts.deep_strategy_prompts import (
    PASS1_DEPENDENCY_GRAPH,
    PASS2_INCONSISTENCY_DETECTION,
    PASS3_PROPOSED_UPDATES,
    PASS4_CROSS_VALIDATION,
)
from app.services.artifact_sync import get_custom_terms, get_llm_client
from app.services.crud import create_session
from app.services.privacy_proxy import anonymize, reidentify

logger = logging.getLogger(__name__)

# VPMA artifact types that can be written to directly
MANAGED_ARTIFACT_TYPES = {"raid log", "status report", "meeting notes"}


def _build_artifact_block(artifacts: list[DeepStrategyArtifact]) -> str:
    """Format artifacts as numbered, labeled text blocks for LLM input."""
    blocks = []
    for art in sorted(artifacts, key=lambda a: a.priority):
        blocks.append(
            f"--- Artifact: {art.name} (Priority {art.priority}) ---\n"
            f"{art.content}\n"
            f"--- End: {art.name} ---"
        )
    return "\n\n".join(blocks)


def _strip_code_fences(text: str) -> str:
    """Strip markdown code fences from LLM response."""
    text = text.strip()
    if text.startswith("```"):
        first_newline = text.index("\n") if "\n" in text else len(text)
        text = text[first_newline + 1 :]
    if text.endswith("```"):
        text = text[:-3].rstrip()
    return text


def _extract_json_object(text: str) -> dict | None:
    """Extract and parse a JSON object from text."""
    text = _strip_code_fences(text)
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        return None
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError as e:
        logger.warning("Failed to parse JSON object: %s", e)
        return None


def _extract_json_array(text: str) -> list | None:
    """Extract and parse a JSON array from text."""
    text = _strip_code_fences(text)
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        return None
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError as e:
        logger.warning("Failed to parse JSON array: %s", e)
        return None


def _parse_dependency_graph(llm_response: str) -> DependencyGraph:
    """Parse Pass 1 response into a DependencyGraph."""
    data = _extract_json_object(llm_response)
    if not data:
        logger.warning("No valid JSON in Pass 1 response")
        return DependencyGraph()

    edges = []
    for edge_data in data.get("edges", []):
        try:
            edges.append(DependencyEdge(**edge_data))
        except Exception as e:
            logger.warning("Skipping malformed edge: %s", e)

    return DependencyGraph(
        artifacts=data.get("artifacts", []),
        edges=edges,
        summary=data.get("summary", ""),
    )


def _parse_inconsistencies(llm_response: str) -> list[Inconsistency]:
    """Parse Pass 2 response into Inconsistency objects."""
    data = _extract_json_array(llm_response)
    if data is None:
        logger.warning("No valid JSON array in Pass 2 response")
        return []

    results = []
    for item in data:
        try:
            results.append(Inconsistency(**item))
        except Exception as e:
            logger.warning("Skipping malformed inconsistency: %s", e)
    return results


def _parse_proposed_updates(llm_response: str) -> list[ProposedUpdate]:
    """Parse Pass 3 response into ProposedUpdate objects."""
    data = _extract_json_array(llm_response)
    if data is None:
        logger.warning("No valid JSON array in Pass 3 response")
        return []

    results = []
    for item in data:
        try:
            results.append(ProposedUpdate(**item))
        except Exception as e:
            logger.warning("Skipping malformed proposed update: %s", e)
    return results


def _parse_validation(llm_response: str) -> list[ValidationCheck]:
    """Parse Pass 4 response into ValidationCheck objects."""
    data = _extract_json_array(llm_response)
    if data is None:
        logger.warning("No valid JSON array in Pass 4 response")
        return []

    results = []
    for item in data:
        try:
            results.append(ValidationCheck(**item))
        except Exception as e:
            logger.warning("Skipping malformed validation check: %s", e)
    return results


def _apply_updates_for_validation(
    artifacts: list[DeepStrategyArtifact],
    updates: list[ProposedUpdate],
) -> str:
    """Create a combined view of artifacts with proposed updates applied.

    Used as input for Pass 4 cross-validation.
    """
    # Build a map of artifact content
    content_map = {art.name: art.content for art in artifacts}

    # Apply updates per artifact
    for update in updates:
        name = update.artifact_name
        if name not in content_map:
            continue

        if update.change_type == "add":
            if update.section:
                content_map[name] += f"\n\n[NEW in {update.section}]\n{update.proposed_text}"
            else:
                content_map[name] += f"\n\n[NEW]\n{update.proposed_text}"
        elif update.change_type == "modify" and update.current_text:
            content_map[name] = content_map[name].replace(
                update.current_text,
                f"[UPDATED] {update.proposed_text}",
                1,
            )
        elif update.change_type == "remove" and update.current_text:
            content_map[name] = content_map[name].replace(
                update.current_text,
                "[REMOVED]",
                1,
            )

    # Rebuild as text blocks
    blocks = []
    for art in sorted(artifacts, key=lambda a: a.priority):
        content = content_map.get(art.name, art.content)
        blocks.append(
            f"--- Artifact: {art.name} (Priority {art.priority}) ---\n"
            f"{content}\n"
            f"--- End: {art.name} ---"
        )
    return "\n\n".join(blocks)


def _compute_summary(
    artifacts: list[DeepStrategyArtifact],
    inconsistencies: list[Inconsistency],
    updates: list[ProposedUpdate],
    validations: list[ValidationCheck],
) -> DeepStrategySummary:
    """Compute summary statistics from the 4-pass results."""
    total_checks = len(validations)
    passed_checks = sum(1 for v in validations if v.passed)
    consistency_score = passed_checks / total_checks if total_checks > 0 else 1.0

    return DeepStrategySummary(
        artifacts_analyzed=len(artifacts),
        inconsistencies_found=len(inconsistencies),
        updates_proposed=len(updates),
        validation_passed=all(v.passed for v in validations) if validations else True,
        consistency_score=round(consistency_score, 2),
    )


async def run_deep_strategy(
    artifacts: list[DeepStrategyArtifact],
    project_id: str = "default",
) -> DeepStrategyResponse:
    """Run the 4-pass Deep Strategy analysis pipeline.

    Args:
        artifacts: List of artifacts to analyze (minimum 2).
        project_id: Project scope for session logging.

    Returns:
        DeepStrategyResponse with all 4 pass results + summary.

    Raises:
        LLMError: If any LLM call fails.
        ValueError: If fewer than 2 artifacts provided.
    """
    if len(artifacts) < 2:
        raise ValueError("Deep Strategy requires at least 2 artifacts")

    client = await get_llm_client()
    custom_terms = await get_custom_terms()

    # Anonymize all artifact content
    anonymized_artifacts = []
    total_pii = 0
    for art in artifacts:
        anon_result = await anonymize(art.content, custom_terms=custom_terms)
        anonymized_artifacts.append(art.model_copy(update={"content": anon_result.anonymized_text}))
        total_pii += len(anon_result.entities)

    artifact_block = _build_artifact_block(anonymized_artifacts)

    # --- Pass 1: Dependency Graph ---
    logger.info("Deep Strategy Pass 1/4: Building dependency graph")
    pass1_prompt = (
        f"## Artifacts (sorted by priority)\n\n{artifact_block}\n\n"
        f"## Priority Order\n"
        + "\n".join(f"{a.priority}. {a.name}" for a in sorted(artifacts, key=lambda a: a.priority))
    )
    pass1_response = await client.call(
        system_prompt=PASS1_DEPENDENCY_GRAPH,
        user_prompt=pass1_prompt,
        max_tokens=4096,
    )
    dependency_graph = _parse_dependency_graph(pass1_response)

    # --- Pass 2: Inconsistency Detection ---
    logger.info("Deep Strategy Pass 2/4: Detecting inconsistencies")
    graph_json = dependency_graph.model_dump_json()
    pass2_prompt = (
        f"## Artifacts\n\n{artifact_block}\n\n"
        f"## Dependency Graph (from Pass 1)\n{graph_json}\n\n"
        f"## Priority Order\n"
        + "\n".join(f"{a.priority}. {a.name}" for a in sorted(artifacts, key=lambda a: a.priority))
    )
    pass2_response = await client.call(
        system_prompt=PASS2_INCONSISTENCY_DETECTION,
        user_prompt=pass2_prompt,
        max_tokens=8192,
    )
    inconsistencies = _parse_inconsistencies(pass2_response)

    # --- Pass 3: Proposed Updates ---
    logger.info("Deep Strategy Pass 3/4: Generating proposed updates")
    inconsistencies_json = json.dumps([inc.model_dump() for inc in inconsistencies])
    pass3_prompt = (
        f"## Artifacts\n\n{artifact_block}\n\n"
        f"## Inconsistencies (from Pass 2)\n{inconsistencies_json}\n\n"
        f"## Priority Order\n"
        + "\n".join(f"{a.priority}. {a.name}" for a in sorted(artifacts, key=lambda a: a.priority))
    )
    pass3_response = await client.call(
        system_prompt=PASS3_PROPOSED_UPDATES,
        user_prompt=pass3_prompt,
        max_tokens=8192,
    )
    proposed_updates = _parse_proposed_updates(pass3_response)

    # --- Pass 4: Cross-Validation ---
    logger.info("Deep Strategy Pass 4/4: Cross-validating consistency")
    updated_artifact_block = _apply_updates_for_validation(anonymized_artifacts, proposed_updates)
    pass4_prompt = f"## Artifacts (with proposed changes applied)\n\n{updated_artifact_block}"
    pass4_response = await client.call(
        system_prompt=PASS4_CROSS_VALIDATION,
        user_prompt=pass4_prompt,
        max_tokens=4096,
    )
    validation_checks = _parse_validation(pass4_response)

    # Reidentify PII in all outputs
    for i, inc in enumerate(inconsistencies):
        inconsistencies[i] = inc.model_copy(
            update={
                "description": await reidentify(inc.description),
                "source_excerpt": await reidentify(inc.source_excerpt),
                "target_excerpt": await reidentify(inc.target_excerpt),
            }
        )
    for i, update in enumerate(proposed_updates):
        proposed_updates[i] = update.model_copy(
            update={
                "current_text": await reidentify(update.current_text),
                "proposed_text": await reidentify(update.proposed_text),
                "rationale": await reidentify(update.rationale),
            }
        )
    for i, check in enumerate(validation_checks):
        validation_checks[i] = check.model_copy(update={"detail": await reidentify(check.detail)})
    dependency_graph = dependency_graph.model_copy(
        update={"summary": await reidentify(dependency_graph.summary)}
    )
    for i, edge in enumerate(dependency_graph.edges):
        dependency_graph.edges[i] = edge.model_copy(
            update={"relationship": await reidentify(edge.relationship)}
        )

    # Compute summary
    summary = _compute_summary(artifacts, inconsistencies, proposed_updates, validation_checks)

    # Log session
    session = await create_session(
        SessionCreate(
            project_id=project_id,
            tab_used="deep_strategy",
            user_input=f"Deep Strategy: {len(artifacts)} artifacts analyzed",
            agent_output=f"Found {len(inconsistencies)} inconsistencies, proposed {len(proposed_updates)} updates",
            tokens_used=sum(
                client.estimate_tokens(r)
                for r in [pass1_response, pass2_response, pass3_response, pass4_response]
            ),
            llm_model=getattr(client, "model", None),
        )
    )

    return DeepStrategyResponse(
        session_id=session.session_id,
        dependency_graph=dependency_graph,
        inconsistencies=inconsistencies,
        proposed_updates=proposed_updates,
        validation_checks=validation_checks,
        summary=summary,
        pii_detected=total_pii,
    )


async def apply_deep_strategy_updates(
    request: DeepStrategyApplyRequest,
) -> DeepStrategyApplyResponse:
    """Apply selected Deep Strategy updates to VPMA artifacts.

    For VPMA-managed artifacts (RAID Log, Status Report, Meeting Notes),
    writes directly to the artifact file. For other artifacts, returns
    the content for copy-to-clipboard.
    """
    from app.services.artifact_manager import get_or_create_artifact, read_artifact_content

    applied = []
    copied_to_clipboard = []

    for update in request.updates:
        artifact_type_lower = update.artifact_name.lower()

        # Check if this is a VPMA-managed artifact type
        if artifact_type_lower in MANAGED_ARTIFACT_TYPES:
            try:
                artifact = await get_or_create_artifact(
                    project_id=request.project_id,
                    artifact_type=update.artifact_name,
                )
                content = await read_artifact_content(artifact.file_path)

                if update.change_type == "add":
                    # Append to section or end of file
                    if update.section and f"## {update.section}" in content:
                        # Insert after section heading
                        section_pos = content.index(f"## {update.section}")
                        next_section = content.find("\n## ", section_pos + 1)
                        if next_section == -1:
                            insert_pos = len(content)
                        else:
                            insert_pos = next_section
                        content = (
                            content[:insert_pos].rstrip()
                            + "\n"
                            + update.proposed_text
                            + "\n\n"
                            + content[insert_pos:]
                        )
                    else:
                        content += "\n" + update.proposed_text + "\n"
                elif update.change_type == "modify" and update.current_text:
                    content = content.replace(update.current_text, update.proposed_text, 1)
                elif update.change_type == "remove" and update.current_text:
                    content = content.replace(update.current_text, "", 1)

                # Write back
                artifact_path = Path(artifact.file_path)
                artifact_path.write_text(content)

                applied.append(
                    {
                        "artifact_name": update.artifact_name,
                        "section": update.section,
                        "status": "applied",
                    }
                )
            except Exception as e:
                logger.error("Failed to apply update to %s: %s", update.artifact_name, e)
                applied.append(
                    {
                        "artifact_name": update.artifact_name,
                        "section": update.section,
                        "status": f"error: {str(e)}",
                    }
                )
        else:
            # Not a VPMA-managed artifact — add to clipboard list
            copied_to_clipboard.append(update.artifact_name)

    return DeepStrategyApplyResponse(
        applied=applied,
        copied_to_clipboard=list(set(copied_to_clipboard)),
    )
