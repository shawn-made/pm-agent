"""Tests for Task 21: LPD Data Model & Schema — tables, models, template, constants."""

from pathlib import Path

import pytest
from app.models.schemas import (
    LPD_SECTION_NAMES,
    LPD_SECTIONS,
    LPDSectionCreate,
    LPDSessionSummaryCreate,
)
from app.services.database import get_db

# ============================================================
# LPD_SECTIONS constant
# ============================================================


class TestLPDSectionsConstant:
    def test_has_seven_sections(self):
        assert len(LPD_SECTIONS) == 7

    def test_section_names(self):
        expected = [
            "Overview",
            "Stakeholders",
            "Timeline & Milestones",
            "Risks",
            "Decisions",
            "Open Questions",
            "Recent Context",
        ]
        assert LPD_SECTION_NAMES == expected

    def test_section_orders_sequential(self):
        orders = [s["order"] for s in LPD_SECTIONS]
        assert orders == [1, 2, 3, 4, 5, 6, 7]

    def test_section_names_list_matches(self):
        names_from_constant = [s["name"] for s in LPD_SECTIONS]
        assert names_from_constant == LPD_SECTION_NAMES


# ============================================================
# Database tables
# ============================================================


class TestLPDTables:
    @pytest.mark.asyncio
    async def test_lpd_sections_table_exists(self):
        db = await get_db()
        try:
            cursor = await db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='lpd_sections'"
            )
            row = await cursor.fetchone()
            assert row is not None
        finally:
            await db.close()

    @pytest.mark.asyncio
    async def test_lpd_session_summaries_table_exists(self):
        db = await get_db()
        try:
            cursor = await db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='lpd_session_summaries'"
            )
            row = await cursor.fetchone()
            assert row is not None
        finally:
            await db.close()

    @pytest.mark.asyncio
    async def test_lpd_sections_unique_constraint(self):
        """project_id + section_name must be unique."""
        db = await get_db()
        try:
            await db.execute(
                "INSERT INTO lpd_sections (section_id, project_id, section_name, content, section_order) "
                "VALUES ('s1', 'default', 'Overview', '', 1)"
            )
            await db.commit()
            with pytest.raises(Exception):
                await db.execute(
                    "INSERT INTO lpd_sections (section_id, project_id, section_name, content, section_order) "
                    "VALUES ('s2', 'default', 'Overview', '', 1)"
                )
                await db.commit()
        finally:
            await db.close()

    @pytest.mark.asyncio
    async def test_lpd_sections_columns(self):
        """Verify all expected columns exist."""
        db = await get_db()
        try:
            cursor = await db.execute("PRAGMA table_info(lpd_sections)")
            columns = {row[1] for row in await cursor.fetchall()}
            expected = {
                "section_id",
                "project_id",
                "section_name",
                "content",
                "section_order",
                "updated_at",
                "verified_at",
            }
            assert expected == columns
        finally:
            await db.close()

    @pytest.mark.asyncio
    async def test_lpd_session_summaries_columns(self):
        """Verify all expected columns exist."""
        db = await get_db()
        try:
            cursor = await db.execute("PRAGMA table_info(lpd_session_summaries)")
            columns = {row[1] for row in await cursor.fetchall()}
            expected = {
                "summary_id",
                "project_id",
                "session_id",
                "summary_text",
                "entities_extracted",
                "created_at",
            }
            assert expected == columns
        finally:
            await db.close()


# ============================================================
# Pydantic models
# ============================================================


class TestLPDModels:
    def test_lpd_section_create_defaults(self):
        section = LPDSectionCreate(
            project_id="default",
            section_name="Overview",
            section_order=1,
        )
        assert section.content == ""
        assert section.section_id is None

    def test_lpd_section_create_with_content(self):
        section = LPDSectionCreate(
            project_id="proj-1",
            section_name="Risks",
            content="- Supply chain delay risk",
            section_order=4,
        )
        assert section.content == "- Supply chain delay risk"
        assert section.section_order == 4

    def test_lpd_session_summary_create_defaults(self):
        summary = LPDSessionSummaryCreate(
            project_id="default",
            summary_text="Discussed timeline changes",
        )
        assert summary.entities_extracted == "{}"
        assert summary.session_id is None

    def test_lpd_session_summary_create_with_entities(self):
        summary = LPDSessionSummaryCreate(
            project_id="default",
            session_id="sess-1",
            summary_text="Decided to switch vendors",
            entities_extracted='{"decisions": ["Switch to Vendor B"]}',
        )
        assert summary.session_id == "sess-1"
        assert "decisions" in summary.entities_extracted


# ============================================================
# LPD Template
# ============================================================


class TestLPDTemplate:
    def test_template_file_exists(self):
        template_path = Path(__file__).parent.parent / "app" / "prompts" / "templates" / "lpd.md"
        assert template_path.exists()

    def test_template_has_all_sections(self):
        template_path = Path(__file__).parent.parent / "app" / "prompts" / "templates" / "lpd.md"
        content = template_path.read_text()
        for section_name in LPD_SECTION_NAMES:
            assert f"## {section_name}" in content, f"Missing section: {section_name}"

    def test_template_has_placeholders(self):
        template_path = Path(__file__).parent.parent / "app" / "prompts" / "templates" / "lpd.md"
        content = template_path.read_text()
        assert "{{project_name}}" in content
        assert "{{last_updated}}" in content
