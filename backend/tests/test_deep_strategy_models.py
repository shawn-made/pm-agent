"""Tests for Phase 2B Pydantic models — Deep Strategy, Risk Prediction, Reconciliation."""

import pytest
from app.models.schemas import (
    CrossSectionImpact,
    DeepStrategyApplyRequest,
    DeepStrategyApplyResponse,
    DeepStrategyArtifact,
    DeepStrategyRequest,
    DeepStrategyResponse,
    DeepStrategySummary,
    DependencyEdge,
    DependencyGraph,
    Inconsistency,
    PredictedRisk,
    ProposedUpdate,
    ReconciliationResponse,
    RiskPredictionResponse,
    ValidationCheck,
)
from pydantic import ValidationError


class TestDeepStrategyArtifact:
    def test_valid_artifact(self):
        a = DeepStrategyArtifact(name="Project Charter", content="# Charter\nScope...", priority=1)
        assert a.name == "Project Charter"
        assert a.priority == 1

    def test_missing_required_field(self):
        with pytest.raises(ValidationError):
            DeepStrategyArtifact(name="Charter", priority=1)  # missing content


class TestDependencyGraph:
    def test_empty_graph(self):
        g = DependencyGraph(artifacts=[], edges=[], summary="No artifacts")
        assert len(g.artifacts) == 0
        assert len(g.edges) == 0

    def test_graph_with_edges(self):
        edge = DependencyEdge(
            source="Charter", target="Schedule", relationship="scope influences timeline"
        )
        g = DependencyGraph(
            artifacts=["Charter", "Schedule"], edges=[edge], summary="Charter drives Schedule"
        )
        assert len(g.edges) == 1
        assert g.edges[0].source == "Charter"


class TestInconsistency:
    def test_valid_inconsistency(self):
        inc = Inconsistency(
            id="INC-1",
            source_artifact="Charter",
            target_artifact="Schedule",
            description="Charter has 6 deliverables but Schedule only has 5",
            severity="high",
            source_excerpt="6 deliverables",
            target_excerpt="5 deliverables",
        )
        assert inc.severity == "high"
        assert inc.id == "INC-1"

    def test_missing_id(self):
        with pytest.raises(ValidationError):
            Inconsistency(
                source_artifact="A",
                target_artifact="B",
                description="mismatch",
                severity="low",
            )


class TestProposedUpdate:
    def test_valid_update(self):
        u = ProposedUpdate(
            inconsistency_id="INC-1",
            artifact_name="Schedule",
            section="Deliverables",
            current_text="5 deliverables listed",
            proposed_text="6 deliverables listed including API Layer",
            change_type="modify",
            rationale="Align with Charter scope",
        )
        assert u.change_type == "modify"
        assert u.artifact_name == "Schedule"


class TestValidationCheck:
    def test_passed_check(self):
        v = ValidationCheck(
            artifact_name="Schedule",
            check_description="Deliverable count matches Charter",
            passed=True,
        )
        assert v.passed is True
        assert v.detail == ""

    def test_failed_check(self):
        v = ValidationCheck(
            artifact_name="RAID Log",
            check_description="All timeline risks accounted for",
            passed=False,
            detail="Missing risk for Phase 2 delay",
        )
        assert v.passed is False
        assert "Missing risk" in v.detail


class TestDeepStrategySummary:
    def test_defaults(self):
        s = DeepStrategySummary()
        assert s.artifacts_analyzed == 0
        assert s.validation_passed is False
        assert s.consistency_score == 0.0

    def test_populated(self):
        s = DeepStrategySummary(
            artifacts_analyzed=4,
            inconsistencies_found=3,
            updates_proposed=5,
            validation_passed=True,
            consistency_score=1.0,
        )
        assert s.artifacts_analyzed == 4
        assert s.consistency_score == 1.0


class TestDeepStrategyRequestResponse:
    def test_request_minimum(self):
        req = DeepStrategyRequest(
            artifacts=[
                DeepStrategyArtifact(name="A", content="text a", priority=1),
                DeepStrategyArtifact(name="B", content="text b", priority=2),
            ]
        )
        assert len(req.artifacts) == 2
        assert req.project_id == "default"

    def test_response_serialization(self):
        resp = DeepStrategyResponse(
            session_id="test-123",
            dependency_graph=DependencyGraph(artifacts=["A"], edges=[], summary=""),
            inconsistencies=[],
            proposed_updates=[],
            validation_checks=[],
            summary=DeepStrategySummary(artifacts_analyzed=1),
            pii_detected=0,
        )
        data = resp.model_dump()
        assert data["session_id"] == "test-123"
        assert data["summary"]["artifacts_analyzed"] == 1


class TestDeepStrategyApply:
    def test_apply_request(self):
        req = DeepStrategyApplyRequest(
            updates=[
                ProposedUpdate(
                    inconsistency_id="INC-1",
                    artifact_name="Schedule",
                    proposed_text="Updated text",
                    change_type="modify",
                )
            ]
        )
        assert len(req.updates) == 1

    def test_apply_response(self):
        resp = DeepStrategyApplyResponse(
            applied=[{"artifact_name": "Schedule", "section": "Deliverables", "status": "applied"}],
            copied_to_clipboard=["External Doc"],
        )
        assert len(resp.applied) == 1
        assert resp.copied_to_clipboard == ["External Doc"]


class TestPredictedRisk:
    def test_valid_risk(self):
        r = PredictedRisk(
            description="Timeline risk: Phase 2 milestone has no RAID entry",
            severity="medium",
            evidence="Timeline & Milestones section shows June 30 deadline",
            confidence=0.85,
            suggested_raid_entry="R_NEW: Phase 2 delay risk — milestone June 30 with no buffer",
            category="timeline",
        )
        assert r.severity == "medium"
        assert r.confidence == 0.85

    def test_risk_prediction_response(self):
        resp = RiskPredictionResponse(
            predictions=[],
            project_health="needs_attention",
            pii_detected=2,
            session_id="risk-123",
        )
        assert resp.session_id == "risk-123"
        assert resp.project_health == "needs_attention"


class TestCrossSectionImpact:
    def test_valid_impact(self):
        impact = CrossSectionImpact(
            source_section="Decisions",
            target_section="Open Questions",
            impact_type="resolves",
            description="Decision to use PostgreSQL resolves the open question about DB choice",
            source_excerpt="Decided: PostgreSQL for all services",
            target_excerpt="Which database should we use?",
            suggested_action="Mark this Open Question as resolved",
        )
        assert impact.impact_type == "resolves"

    def test_reconciliation_response(self):
        resp = ReconciliationResponse(
            impacts=[],
            sections_analyzed=7,
            pii_detected=0,
            session_id="recon-123",
        )
        assert resp.sections_analyzed == 7
