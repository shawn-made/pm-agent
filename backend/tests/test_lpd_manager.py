"""Tests for Task 23: LPD Manager Service."""

import pytest
from app.models.schemas import LPD_SECTION_NAMES
from app.services.crud import get_session_summary_count
from app.services.lpd_manager import (
    RECENT_CONTEXT_TOKEN_BUDGET,
    _estimate_tokens,
    _lpd_file_path,
    append_to_section,
    get_context_for_injection,
    get_full_lpd,
    get_section_staleness,
    initialize_lpd,
    log_session_summary,
    render_lpd_markdown,
    update_section,
)

# ============================================================
# initialize_lpd
# ============================================================


class TestInitializeLPD:
    @pytest.mark.asyncio
    async def test_creates_all_seven_sections(self):
        sections = await initialize_lpd("default")
        assert len(sections) == 7
        names = [s.section_name for s in sections]
        assert names == LPD_SECTION_NAMES

    @pytest.mark.asyncio
    async def test_idempotent(self):
        """Calling initialize twice returns existing sections without error."""
        first = await initialize_lpd("default")
        second = await initialize_lpd("default")
        assert len(second) == 7
        assert [s.section_id for s in first] == [s.section_id for s in second]

    @pytest.mark.asyncio
    async def test_creates_markdown_file(self, tmp_path):
        await initialize_lpd("default")
        file_path = _lpd_file_path("default")
        assert file_path.exists()
        content = file_path.read_text()
        assert "# Living Project Document" in content
        assert "## Overview" in content

    @pytest.mark.asyncio
    async def test_sections_have_correct_order(self):
        sections = await initialize_lpd("default")
        orders = [s.section_order for s in sections]
        assert orders == [1, 2, 3, 4, 5, 6, 7]

    @pytest.mark.asyncio
    async def test_sections_start_empty(self):
        sections = await initialize_lpd("default")
        for s in sections:
            assert s.content == ""


# ============================================================
# get_full_lpd
# ============================================================


class TestGetFullLPD:
    @pytest.mark.asyncio
    async def test_empty_when_not_initialized(self):
        result = await get_full_lpd("default")
        assert result == {}

    @pytest.mark.asyncio
    async def test_returns_all_sections(self):
        await initialize_lpd("default")
        result = await get_full_lpd("default")
        assert len(result) == 7
        assert "Overview" in result
        assert "Recent Context" in result

    @pytest.mark.asyncio
    async def test_reflects_updates(self):
        await initialize_lpd("default")
        await update_section("default", "Overview", "Project Alpha is a mobile app")
        result = await get_full_lpd("default")
        assert result["Overview"] == "Project Alpha is a mobile app"


# ============================================================
# render_lpd_markdown
# ============================================================


class TestRenderLPDMarkdown:
    @pytest.mark.asyncio
    async def test_empty_when_not_initialized(self):
        result = await render_lpd_markdown("default")
        assert result == ""

    @pytest.mark.asyncio
    async def test_contains_all_sections(self):
        await initialize_lpd("default")
        md = await render_lpd_markdown("default")
        assert "# Living Project Document" in md
        for name in LPD_SECTION_NAMES:
            assert f"## {name}" in md

    @pytest.mark.asyncio
    async def test_shows_content_when_present(self):
        await initialize_lpd("default")
        await update_section("default", "Risks", "- Supply chain delay risk")
        md = await render_lpd_markdown("default")
        assert "- Supply chain delay risk" in md

    @pytest.mark.asyncio
    async def test_shows_placeholder_for_empty(self):
        await initialize_lpd("default")
        md = await render_lpd_markdown("default")
        assert "_No overview recorded yet._" in md


# ============================================================
# update_section
# ============================================================


class TestUpdateSection:
    @pytest.mark.asyncio
    async def test_update_existing_section(self):
        await initialize_lpd("default")
        result = await update_section("default", "Overview", "New overview content")
        assert result is True
        lpd = await get_full_lpd("default")
        assert lpd["Overview"] == "New overview content"

    @pytest.mark.asyncio
    async def test_invalid_section_name_returns_false(self):
        await initialize_lpd("default")
        result = await update_section("default", "Nonexistent Section", "content")
        assert result is False

    @pytest.mark.asyncio
    async def test_update_syncs_markdown(self, tmp_path):
        await initialize_lpd("default")
        await update_section("default", "Decisions", "D1: Use SQLite for metadata")
        file_path = _lpd_file_path("default")
        content = file_path.read_text()
        assert "D1: Use SQLite for metadata" in content

    @pytest.mark.asyncio
    async def test_update_nonexistent_project_returns_false(self):
        result = await update_section("nonexistent", "Overview", "content")
        assert result is False


# ============================================================
# append_to_section
# ============================================================


class TestAppendToSection:
    @pytest.mark.asyncio
    async def test_append_to_empty_section(self):
        await initialize_lpd("default")
        result = await append_to_section("default", "Risks", "- New risk identified")
        assert result is True
        lpd = await get_full_lpd("default")
        assert lpd["Risks"] == "- New risk identified"

    @pytest.mark.asyncio
    async def test_append_to_existing_content(self):
        await initialize_lpd("default")
        await update_section("default", "Risks", "- Risk A")
        await append_to_section("default", "Risks", "- Risk B")
        lpd = await get_full_lpd("default")
        assert "- Risk A" in lpd["Risks"]
        assert "- Risk B" in lpd["Risks"]

    @pytest.mark.asyncio
    async def test_invalid_section_returns_false(self):
        await initialize_lpd("default")
        result = await append_to_section("default", "Bogus", "text")
        assert result is False

    @pytest.mark.asyncio
    async def test_nonexistent_project_returns_false(self):
        result = await append_to_section("nonexistent", "Overview", "text")
        assert result is False


# ============================================================
# log_session_summary
# ============================================================


class TestLogSessionSummary:
    @pytest.mark.asyncio
    async def test_creates_summary_record(self):
        await initialize_lpd("default")
        await log_session_summary("default", None, "Discussed project timeline")
        count = await get_session_summary_count("default")
        assert count == 1

    @pytest.mark.asyncio
    async def test_rebuilds_recent_context(self):
        await initialize_lpd("default")
        await log_session_summary("default", None, "Kicked off Phase 1A implementation")
        lpd = await get_full_lpd("default")
        assert "Kicked off Phase 1A implementation" in lpd["Recent Context"]

    @pytest.mark.asyncio
    async def test_multiple_summaries_accumulate(self):
        await initialize_lpd("default")
        await log_session_summary("default", None, "First session: setup")
        await log_session_summary("default", None, "Second session: implementation")
        lpd = await get_full_lpd("default")
        assert "First session: setup" in lpd["Recent Context"]
        assert "Second session: implementation" in lpd["Recent Context"]

    @pytest.mark.asyncio
    async def test_recent_context_pruning(self):
        """Recent Context should stay within token budget."""
        await initialize_lpd("default")
        # Add many long summaries to exceed the budget
        long_text = "x" * 200
        for i in range(50):
            await log_session_summary("default", None, f"Session {i}: {long_text}")

        lpd = await get_full_lpd("default")
        recent = lpd["Recent Context"]
        assert _estimate_tokens(recent) <= RECENT_CONTEXT_TOKEN_BUDGET + 100  # small buffer


# ============================================================
# get_context_for_injection
# ============================================================


class TestGetContextForInjection:
    @pytest.mark.asyncio
    async def test_empty_when_no_lpd(self):
        result = await get_context_for_injection("default")
        assert result == ""

    @pytest.mark.asyncio
    async def test_empty_when_all_sections_empty(self):
        await initialize_lpd("default")
        result = await get_context_for_injection("default")
        assert result == ""

    @pytest.mark.asyncio
    async def test_includes_overview(self):
        await initialize_lpd("default")
        await update_section("default", "Overview", "Project Alpha builds a mobile app")
        result = await get_context_for_injection("default")
        assert "## Project Context" in result
        assert "### Overview" in result
        assert "Project Alpha builds a mobile app" in result

    @pytest.mark.asyncio
    async def test_includes_multiple_sections(self):
        await initialize_lpd("default")
        await update_section("default", "Overview", "Project Alpha")
        await update_section("default", "Risks", "- Timeline risk")
        await update_section("default", "Decisions", "D1: Use SQLite")
        result = await get_context_for_injection("default")
        assert "### Overview" in result
        assert "### Risks" in result
        assert "### Decisions" in result

    @pytest.mark.asyncio
    async def test_respects_token_budget(self):
        await initialize_lpd("default")
        # Fill sections with large content
        big_text = "Important detail. " * 500  # ~3500 chars = ~875 tokens
        await update_section("default", "Overview", big_text)
        await update_section("default", "Risks", big_text)
        await update_section("default", "Decisions", big_text)

        result = await get_context_for_injection("default", max_tokens=500)
        # Should include some content but be truncated
        assert "## Project Context" in result
        assert _estimate_tokens(result) <= 600  # some buffer for headers

    @pytest.mark.asyncio
    async def test_skips_empty_sections(self):
        await initialize_lpd("default")
        await update_section("default", "Overview", "Project info")
        # Leave other sections empty
        result = await get_context_for_injection("default")
        assert "### Stakeholders" not in result
        assert "### Timeline & Milestones" not in result


# ============================================================
# get_section_staleness
# ============================================================


class TestGetSectionStaleness:
    @pytest.mark.asyncio
    async def test_empty_when_no_lpd(self):
        result = await get_section_staleness("default")
        assert result == []

    @pytest.mark.asyncio
    async def test_returns_all_sections(self):
        await initialize_lpd("default")
        result = await get_section_staleness("default")
        assert len(result) == 7
        names = [r["section_name"] for r in result]
        assert names == LPD_SECTION_NAMES

    @pytest.mark.asyncio
    async def test_tracks_days_since_update(self):
        await initialize_lpd("default")
        result = await get_section_staleness("default")
        # Just created, should be 0 days
        for r in result:
            assert r["days_since_update"] == 0

    @pytest.mark.asyncio
    async def test_has_content_flag(self):
        await initialize_lpd("default")
        await update_section("default", "Overview", "Some content")
        result = await get_section_staleness("default")
        overview = next(r for r in result if r["section_name"] == "Overview")
        risks = next(r for r in result if r["section_name"] == "Risks")
        assert overview["has_content"] is True
        assert risks["has_content"] is False


# ============================================================
# Markdown sync
# ============================================================


class TestMarkdownSync:
    @pytest.mark.asyncio
    async def test_file_updated_on_section_update(self, tmp_path):
        await initialize_lpd("default")
        file_path = _lpd_file_path("default")

        initial_content = file_path.read_text()
        assert "_No overview recorded yet._" in initial_content

        await update_section("default", "Overview", "Updated overview")
        updated_content = file_path.read_text()
        assert "Updated overview" in updated_content
        assert "_No overview recorded yet._" not in updated_content

    @pytest.mark.asyncio
    async def test_file_updated_on_append(self, tmp_path):
        await initialize_lpd("default")
        await append_to_section("default", "Risks", "- Critical risk")
        file_path = _lpd_file_path("default")
        content = file_path.read_text()
        assert "- Critical risk" in content

    @pytest.mark.asyncio
    async def test_file_updated_after_session_summary(self, tmp_path):
        """Markdown file should reflect Recent Context after log_session_summary."""
        await initialize_lpd("default")
        await log_session_summary("default", None, "Reviewed sprint backlog and prioritized items")
        file_path = _lpd_file_path("default")
        content = file_path.read_text()
        assert "Reviewed sprint backlog and prioritized items" in content


# ============================================================
# Helper functions
# ============================================================


class TestHelpers:
    def test_estimate_tokens(self):
        assert _estimate_tokens("") == 0
        assert _estimate_tokens("hello world") == 2  # 11 chars / 4 = 2
        assert _estimate_tokens("a" * 100) == 25  # 100 / 4

    def test_lpd_file_path(self):
        path = _lpd_file_path("default")
        assert path.name == "default_lpd.md"

    def test_lpd_file_path_sanitizes(self):
        path = _lpd_file_path("my project!")
        assert "!" not in path.name
        assert path.name == "my_project__lpd.md"
