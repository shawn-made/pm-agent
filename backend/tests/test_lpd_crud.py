"""Tests for Task 22: LPD CRUD Operations."""

import pytest
from app.models.schemas import (
    LPDSectionCreate,
    LPDSessionSummaryCreate,
)
from app.services.crud import (
    create_lpd_section,
    create_lpd_session_summary,
    get_lpd_section,
    get_lpd_sections,
    get_recent_session_summaries,
    get_session_summary_count,
    lpd_exists,
    update_lpd_section_content,
    verify_lpd_section,
)

# ============================================================
# LPD SECTIONS CRUD
# ============================================================


class TestCreateLPDSection:
    @pytest.mark.asyncio
    async def test_create_section(self):
        section = await create_lpd_section(
            LPDSectionCreate(
                project_id="default",
                section_name="Overview",
                content="Project Alpha overview",
                section_order=1,
            )
        )
        assert section.section_name == "Overview"
        assert section.content == "Project Alpha overview"
        assert section.section_order == 1
        assert section.project_id == "default"
        assert section.section_id is not None
        assert section.verified_at is None

    @pytest.mark.asyncio
    async def test_create_section_empty_content(self):
        section = await create_lpd_section(
            LPDSectionCreate(
                project_id="default",
                section_name="Risks",
                section_order=4,
            )
        )
        assert section.content == ""

    @pytest.mark.asyncio
    async def test_create_duplicate_section_fails(self):
        await create_lpd_section(
            LPDSectionCreate(
                project_id="default",
                section_name="Overview",
                section_order=1,
            )
        )
        with pytest.raises(Exception):
            await create_lpd_section(
                LPDSectionCreate(
                    project_id="default",
                    section_name="Overview",
                    section_order=1,
                )
            )

    @pytest.mark.asyncio
    async def test_same_section_name_different_projects(self):
        """Same section name allowed in different projects."""
        from app.models.schemas import ProjectCreate
        from app.services.crud import create_project

        await create_project(ProjectCreate(project_id="proj-2", project_name="Project 2"))
        s1 = await create_lpd_section(
            LPDSectionCreate(project_id="default", section_name="Overview", section_order=1)
        )
        s2 = await create_lpd_section(
            LPDSectionCreate(project_id="proj-2", section_name="Overview", section_order=1)
        )
        assert s1.project_id == "default"
        assert s2.project_id == "proj-2"


class TestGetLPDSections:
    @pytest.mark.asyncio
    async def test_get_sections_empty(self):
        sections = await get_lpd_sections("default")
        assert sections == []

    @pytest.mark.asyncio
    async def test_get_sections_ordered(self):
        """Sections returned in section_order, not insertion order."""
        await create_lpd_section(
            LPDSectionCreate(project_id="default", section_name="Risks", section_order=4)
        )
        await create_lpd_section(
            LPDSectionCreate(project_id="default", section_name="Overview", section_order=1)
        )
        await create_lpd_section(
            LPDSectionCreate(project_id="default", section_name="Stakeholders", section_order=2)
        )
        sections = await get_lpd_sections("default")
        assert len(sections) == 3
        assert sections[0].section_name == "Overview"
        assert sections[1].section_name == "Stakeholders"
        assert sections[2].section_name == "Risks"


class TestGetLPDSection:
    @pytest.mark.asyncio
    async def test_get_existing_section(self):
        await create_lpd_section(
            LPDSectionCreate(
                project_id="default",
                section_name="Decisions",
                content="D1: Use SQLite",
                section_order=5,
            )
        )
        section = await get_lpd_section("default", "Decisions")
        assert section is not None
        assert section.content == "D1: Use SQLite"

    @pytest.mark.asyncio
    async def test_get_nonexistent_section(self):
        section = await get_lpd_section("default", "Nonexistent")
        assert section is None


class TestUpdateLPDSectionContent:
    @pytest.mark.asyncio
    async def test_update_content(self):
        await create_lpd_section(
            LPDSectionCreate(
                project_id="default",
                section_name="Overview",
                content="Initial overview",
                section_order=1,
            )
        )
        updated = await update_lpd_section_content(
            "default", "Overview", "Updated overview with more detail"
        )
        assert updated is not None
        assert updated.content == "Updated overview with more detail"

    @pytest.mark.asyncio
    async def test_update_nonexistent_returns_none(self):
        result = await update_lpd_section_content("default", "Nonexistent", "content")
        assert result is None

    @pytest.mark.asyncio
    async def test_update_changes_timestamp(self):
        original = await create_lpd_section(
            LPDSectionCreate(
                project_id="default",
                section_name="Overview",
                content="v1",
                section_order=1,
            )
        )
        updated = await update_lpd_section_content("default", "Overview", "v2")
        assert updated.updated_at >= original.updated_at


class TestVerifyLPDSection:
    @pytest.mark.asyncio
    async def test_verify_sets_timestamp(self):
        await create_lpd_section(
            LPDSectionCreate(
                project_id="default",
                section_name="Risks",
                section_order=4,
            )
        )
        verified = await verify_lpd_section("default", "Risks")
        assert verified is not None
        assert verified.verified_at is not None

    @pytest.mark.asyncio
    async def test_verify_nonexistent_returns_none(self):
        result = await verify_lpd_section("default", "Nonexistent")
        assert result is None


class TestLPDExists:
    @pytest.mark.asyncio
    async def test_no_sections_returns_false(self):
        assert await lpd_exists("default") is False

    @pytest.mark.asyncio
    async def test_with_sections_returns_true(self):
        await create_lpd_section(
            LPDSectionCreate(
                project_id="default",
                section_name="Overview",
                section_order=1,
            )
        )
        assert await lpd_exists("default") is True


# ============================================================
# LPD SESSION SUMMARIES CRUD
# ============================================================


class TestCreateSessionSummary:
    @pytest.mark.asyncio
    async def test_create_summary(self):
        summary = await create_lpd_session_summary(
            LPDSessionSummaryCreate(
                project_id="default",
                summary_text="Discussed vendor selection and timeline risks",
                entities_extracted='{"decisions": ["Choose Vendor B"]}',
            )
        )
        assert summary.summary_text == "Discussed vendor selection and timeline risks"
        assert summary.project_id == "default"
        assert summary.summary_id is not None
        assert "decisions" in summary.entities_extracted

    @pytest.mark.asyncio
    async def test_create_summary_minimal(self):
        summary = await create_lpd_session_summary(
            LPDSessionSummaryCreate(
                project_id="default",
                summary_text="Quick status check",
            )
        )
        assert summary.entities_extracted == "{}"
        assert summary.session_id is None


class TestGetRecentSessionSummaries:
    @pytest.mark.asyncio
    async def test_empty_project(self):
        summaries = await get_recent_session_summaries("default")
        assert summaries == []

    @pytest.mark.asyncio
    async def test_returns_newest_first(self):
        await create_lpd_session_summary(
            LPDSessionSummaryCreate(project_id="default", summary_text="First session")
        )
        await create_lpd_session_summary(
            LPDSessionSummaryCreate(project_id="default", summary_text="Second session")
        )
        summaries = await get_recent_session_summaries("default")
        assert len(summaries) == 2
        assert summaries[0].summary_text == "Second session"
        assert summaries[1].summary_text == "First session"

    @pytest.mark.asyncio
    async def test_limit_parameter(self):
        for i in range(5):
            await create_lpd_session_summary(
                LPDSessionSummaryCreate(project_id="default", summary_text=f"Session {i}")
            )
        summaries = await get_recent_session_summaries("default", limit=3)
        assert len(summaries) == 3


class TestGetSessionSummaryCount:
    @pytest.mark.asyncio
    async def test_empty_returns_zero(self):
        count = await get_session_summary_count("default")
        assert count == 0

    @pytest.mark.asyncio
    async def test_counts_correctly(self):
        for i in range(4):
            await create_lpd_session_summary(
                LPDSessionSummaryCreate(project_id="default", summary_text=f"Session {i}")
            )
        count = await get_session_summary_count("default")
        assert count == 4
