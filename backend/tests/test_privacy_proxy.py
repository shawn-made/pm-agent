"""Tests for VPMA Privacy Proxy — PII detection (Tasks 3-4) + Anonymize/Reidentify (Task 5)."""

import json

import pytest
from app.services.privacy_proxy import (
    LOW_CONFIDENCE_THRESHOLD,
    anonymize,
    detect_custom_terms,
    detect_ner,
    detect_pii,
    detect_regex,
    reidentify,
)

# ============================================================
# TASK 3: REGEX PII DETECTION
# ============================================================


class TestEmailDetection:
    def test_standard_email(self):
        entities = detect_regex("Contact john.smith@acme.com for details.")
        emails = [e for e in entities if e.entity_type == "EMAIL"]
        assert len(emails) == 1
        assert emails[0].text == "john.smith@acme.com"

    def test_multiple_emails(self):
        text = "Send to alice@example.com and bob@company.org"
        entities = detect_regex(text)
        emails = [e for e in entities if e.entity_type == "EMAIL"]
        assert len(emails) == 2

    def test_email_with_plus(self):
        entities = detect_regex("Email user+tag@domain.com")
        emails = [e for e in entities if e.entity_type == "EMAIL"]
        assert len(emails) == 1
        assert emails[0].text == "user+tag@domain.com"

    def test_no_email(self):
        entities = detect_regex("No email addresses here.")
        emails = [e for e in entities if e.entity_type == "EMAIL"]
        assert len(emails) == 0


class TestPhoneDetection:
    def test_standard_phone(self):
        entities = detect_regex("Call 555-123-4567 for info.")
        phones = [e for e in entities if e.entity_type == "PHONE"]
        assert len(phones) == 1
        assert phones[0].text == "555-123-4567"

    def test_phone_with_dots(self):
        entities = detect_regex("Phone: 555.123.4567")
        phones = [e for e in entities if e.entity_type == "PHONE"]
        assert len(phones) == 1

    def test_phone_with_parens(self):
        entities = detect_regex("Call (555) 123-4567")
        phones = [e for e in entities if e.entity_type == "PHONE"]
        assert len(phones) == 1

    def test_phone_no_separators(self):
        entities = detect_regex("Phone: 5551234567")
        phones = [e for e in entities if e.entity_type == "PHONE"]
        assert len(phones) == 1

    def test_no_phone(self):
        entities = detect_regex("The project has 42 tasks.")
        phones = [e for e in entities if e.entity_type == "PHONE"]
        assert len(phones) == 0


class TestURLDetection:
    def test_https_url(self):
        entities = detect_regex("Visit https://www.example.com/page for details.")
        urls = [e for e in entities if e.entity_type == "URL"]
        assert len(urls) == 1
        assert "example.com" in urls[0].text

    def test_http_url(self):
        entities = detect_regex("See http://internal.acme.com/dashboard")
        urls = [e for e in entities if e.entity_type == "URL"]
        assert len(urls) == 1

    def test_no_url(self):
        entities = detect_regex("No links in this text.")
        urls = [e for e in entities if e.entity_type == "URL"]
        assert len(urls) == 0


class TestCustomTerms:
    def test_single_term(self):
        entities = detect_custom_terms(
            "The Project Falcon timeline is at risk.",
            ["Project Falcon"],
        )
        assert len(entities) == 1
        assert entities[0].text == "Project Falcon"
        assert entities[0].entity_type == "CUSTOM"

    def test_case_insensitive(self):
        entities = detect_custom_terms(
            "We discussed project falcon with the team.",
            ["Project Falcon"],
        )
        assert len(entities) == 1

    def test_multiple_terms(self):
        entities = detect_custom_terms(
            "Meeting with ClientCo about Q4 Roadmap progress.",
            ["ClientCo", "Q4 Roadmap"],
        )
        assert len(entities) == 2

    def test_repeated_term(self):
        entities = detect_custom_terms(
            "ClientCo sent updates. We replied to ClientCo.",
            ["ClientCo"],
        )
        assert len(entities) == 2

    def test_empty_terms_list(self):
        entities = detect_custom_terms("Some text.", [])
        assert len(entities) == 0

    def test_whitespace_terms_ignored(self):
        entities = detect_custom_terms("Some text.", ["", "  "])
        assert len(entities) == 0

    def test_no_match(self):
        entities = detect_custom_terms(
            "Regular meeting notes.", ["Project Falcon"]
        )
        assert len(entities) == 0


class TestRegexConfidence:
    def test_regex_entities_have_full_confidence(self):
        entities = detect_regex("Email: test@example.com, Phone: 555-123-4567")
        for entity in entities:
            assert entity.confidence == 1.0

    def test_custom_terms_have_full_confidence(self):
        entities = detect_custom_terms("Project Falcon", ["Project Falcon"])
        for entity in entities:
            assert entity.confidence == 1.0


# ============================================================
# TASK 4: SPACY NER DETECTION
# ============================================================


class TestNERDetection:
    def test_person_detection(self):
        entities = detect_ner("John Smith presented the quarterly results.")
        persons = [e for e in entities if e.entity_type == "PERSON"]
        assert len(persons) >= 1
        assert any("John" in e.text for e in persons)

    def test_org_detection(self):
        entities = detect_ner("Microsoft announced new features today.")
        orgs = [e for e in entities if e.entity_type == "ORG"]
        assert len(orgs) >= 1
        assert any("Microsoft" in e.text for e in orgs)

    def test_gpe_detection(self):
        entities = detect_ner("The team in New York will lead the effort.")
        gpes = [e for e in entities if e.entity_type == "GPE"]
        assert len(gpes) >= 1
        assert any("New York" in e.text for e in gpes)

    def test_ner_source_is_ner(self):
        entities = detect_ner("Sarah Johnson joined Google last month.")
        for entity in entities:
            assert entity.source == "ner"

    def test_ner_has_offsets(self):
        text = "Sarah Johnson joined Google last month."
        entities = detect_ner(text)
        for entity in entities:
            assert entity.start >= 0
            assert entity.end > entity.start
            assert text[entity.start : entity.end] == entity.text

    def test_no_entities_in_plain_text(self):
        entities = detect_ner("The quick brown fox jumps over the lazy dog.")
        # May find some entities, but none of our target types
        relevant = [e for e in entities if e.entity_type in {"PERSON", "ORG", "GPE", "PRODUCT"}]
        assert len(relevant) == 0


class TestNERConfidence:
    def test_multi_word_person_high_confidence(self):
        entities = detect_ner("John Smith presented the results.")
        persons = [e for e in entities if e.entity_type == "PERSON"]
        if persons:
            # Multi-word name should have high confidence
            assert persons[0].confidence >= LOW_CONFIDENCE_THRESHOLD

    def test_confidence_is_between_0_and_1(self):
        entities = detect_ner(
            "Sarah Johnson from Microsoft in New York discussed the roadmap."
        )
        for entity in entities:
            assert 0.0 <= entity.confidence <= 1.0


# ============================================================
# COMBINED PIPELINE (detect_pii)
# ============================================================


class TestCombinedDetection:
    def test_mixed_pii_types(self):
        """Realistic meeting notes with multiple PII types."""
        text = (
            "Meeting with John Smith (john.smith@acme.com, 555-123-4567) "
            "from ACME Corp. Discussed Project Falcon timeline. "
            "See https://internal.acme.com/status for details."
        )
        result = detect_pii(text, custom_terms=["Project Falcon"])

        entity_types = {e.entity_type for e in result.entities}
        assert "EMAIL" in entity_types
        assert "PHONE" in entity_types
        assert "URL" in entity_types
        assert "CUSTOM" in entity_types

    def test_deduplication_prefers_longer(self):
        """When regex and NER detect overlapping spans, keep the longer one."""
        text = "Contact john.smith@acme.com for details."
        result = detect_pii(text)

        # Email should appear only once (not both as EMAIL and possibly as some NER entity)
        email_entities = [e for e in result.entities if "john.smith@acme.com" in e.text]
        assert len(email_entities) == 1

    def test_overall_confidence_calculated(self):
        text = "John Smith from Microsoft discussed the plan."
        result = detect_pii(text)
        assert 0.0 <= result.overall_confidence <= 1.0

    def test_no_pii_returns_empty(self):
        result = detect_pii("The quick brown fox jumps over the lazy dog.")
        # May have some entities, but confidence should still be valid
        assert result.overall_confidence >= 0.0

    def test_custom_terms_only(self):
        """Detection works when only custom terms match."""
        result = detect_pii(
            "Working on Project Falcon this week.",
            custom_terms=["Project Falcon"],
            use_ner=False,
        )
        assert len(result.entities) >= 1
        assert result.entities[0].entity_type == "CUSTOM"

    def test_ner_disabled(self):
        """Pipeline works with NER disabled (regex + custom only)."""
        text = "Email sarah@example.com about Project Falcon."
        result = detect_pii(text, custom_terms=["Project Falcon"], use_ner=False)
        sources = {e.source for e in result.entities}
        assert "ner" not in sources
        assert "regex" in sources or "custom" in sources

    def test_realistic_meeting_notes(self):
        """Full realistic scenario from PRD."""
        text = """
        Weekly standup notes - Feb 12, 2026

        Attendees: Sarah Johnson, Mike Chen, Lisa Park

        Updates:
        - Sarah: Completed the ClientCo integration API. Sent specs to
          engineering@clientco.com. Call Mike at 415-555-0123 for review.
        - Mike: Risk identified - vendor delay from PartnerOrg may push
          timeline by 2 weeks. See https://jira.internal.com/PROJ-456
        - Lisa: Budget review with CFO scheduled for Friday in Chicago.

        Action items captured in Project Falcon tracker.
        """
        result = detect_pii(
            text,
            custom_terms=["Project Falcon", "ClientCo", "PartnerOrg"],
        )

        # Should detect multiple entity types
        entity_types = {e.entity_type for e in result.entities}

        # Regex should catch email, phone, URL
        assert "EMAIL" in entity_types
        assert "PHONE" in entity_types
        assert "URL" in entity_types

        # Custom terms should catch at least some
        custom_found = [e for e in result.entities if e.source == "custom"]
        assert len(custom_found) >= 1

        # NER should catch person names
        ner_found = [e for e in result.entities if e.source == "ner"]
        assert len(ner_found) >= 1

        # Total should be a reasonable number
        assert len(result.entities) >= 6


class TestEdgeCases:
    def test_empty_text(self):
        result = detect_pii("")
        assert len(result.entities) == 0
        assert result.overall_confidence == 1.0

    def test_none_custom_terms(self):
        """None custom_terms should not crash."""
        result = detect_pii("Hello world.", custom_terms=None)
        assert result is not None

    def test_entity_offsets_are_correct(self):
        """Verify that start/end offsets point to correct text."""
        text = "Email alice@example.com today."
        result = detect_pii(text, use_ner=False)
        for entity in result.entities:
            assert text[entity.start : entity.end] == entity.text


# ============================================================
# TASK 5: ANONYMIZE & REIDENTIFY
# ============================================================


class TestAnonymize:
    @pytest.mark.asyncio
    async def test_basic_anonymize_email(self):
        """Email addresses are replaced with <EMAIL_N> tokens."""
        result = await anonymize(
            "Contact alice@example.com for details.",
            use_ner=False,
        )
        assert "alice@example.com" not in result.anonymized_text
        assert "<EMAIL_1>" in result.anonymized_text
        assert result.token_map["<EMAIL_1>"] == "alice@example.com"

    @pytest.mark.asyncio
    async def test_anonymize_multiple_types(self):
        """Multiple PII types are anonymized with separate token counters."""
        result = await anonymize(
            "Email alice@example.com or call 555-123-4567.",
            use_ner=False,
        )
        assert "alice@example.com" not in result.anonymized_text
        assert "555-123-4567" not in result.anonymized_text
        assert "<EMAIL_1>" in result.anonymized_text
        assert "<PHONE_1>" in result.anonymized_text

    @pytest.mark.asyncio
    async def test_anonymize_custom_terms(self):
        """Custom terms are replaced with <CUSTOM_N> tokens."""
        result = await anonymize(
            "Working on Project Falcon this week.",
            custom_terms=["Project Falcon"],
            use_ner=False,
        )
        assert "Project Falcon" not in result.anonymized_text
        assert "<CUSTOM_1>" in result.anonymized_text

    @pytest.mark.asyncio
    async def test_anonymize_same_value_reuses_token(self):
        """Same PII value at different positions gets the same token."""
        result = await anonymize(
            "Email alice@example.com now. Also try alice@example.com later.",
            use_ner=False,
        )
        assert result.anonymized_text.count("<EMAIL_1>") == 2
        assert "alice@example.com" not in result.anonymized_text

    @pytest.mark.asyncio
    async def test_anonymize_no_pii(self):
        """Text with no PII returns unchanged."""
        result = await anonymize(
            "The project is on track.",
            use_ner=False,
        )
        assert result.anonymized_text == "The project is on track."
        assert len(result.entities) == 0
        assert len(result.token_map) == 0

    @pytest.mark.asyncio
    async def test_anonymize_returns_entities(self):
        """Anonymize result includes detected entities."""
        result = await anonymize(
            "Contact bob@test.com today.",
            use_ner=False,
        )
        assert len(result.entities) >= 1
        assert any(e.entity_type == "EMAIL" for e in result.entities)

    @pytest.mark.asyncio
    async def test_anonymize_returns_confidence(self):
        """Anonymize result includes confidence score."""
        result = await anonymize(
            "Contact bob@test.com today.",
            use_ner=False,
        )
        assert 0.0 <= result.overall_confidence <= 1.0

    @pytest.mark.asyncio
    async def test_anonymize_vault_persistence(self):
        """Second anonymize call reuses tokens from vault."""
        # First call creates the mapping
        result1 = await anonymize(
            "Email alice@example.com",
            use_ner=False,
        )
        token1 = result1.token_map

        # Second call should reuse the same token
        result2 = await anonymize(
            "Another message to alice@example.com",
            use_ner=False,
        )
        # Same original value gets the same token
        for token, original in result2.token_map.items():
            if original == "alice@example.com":
                assert token in token1


class TestReidentify:
    @pytest.mark.asyncio
    async def test_basic_reidentify(self):
        """Tokens are replaced back with original values."""
        # First anonymize to populate vault
        anon_result = await anonymize(
            "Contact alice@example.com for details.",
            use_ner=False,
        )

        # Then reidentify
        restored = await reidentify(anon_result.anonymized_text)
        assert "alice@example.com" in restored
        assert "<EMAIL_1>" not in restored

    @pytest.mark.asyncio
    async def test_reidentify_no_tokens(self):
        """Text with no tokens returns unchanged."""
        result = await reidentify("No tokens here.")
        assert result == "No tokens here."

    @pytest.mark.asyncio
    async def test_reidentify_unknown_token(self):
        """Unknown tokens are left in place."""
        result = await reidentify("Hello <PERSON_999>!")
        assert "<PERSON_999>" in result

    @pytest.mark.asyncio
    async def test_reidentify_multiple_tokens(self):
        """Multiple different tokens are all resolved."""
        anon_result = await anonymize(
            "Email alice@example.com or call 555-123-4567.",
            use_ner=False,
        )
        restored = await reidentify(anon_result.anonymized_text)
        assert "alice@example.com" in restored
        assert "555-123-4567" in restored


class TestRoundTrip:
    @pytest.mark.asyncio
    async def test_round_trip_simple(self):
        """anonymize → reidentify recovers original text."""
        original = "Email alice@example.com or call 555-123-4567."
        anon_result = await anonymize(original, use_ner=False)
        restored = await reidentify(anon_result.anonymized_text)
        assert restored == original

    @pytest.mark.asyncio
    async def test_round_trip_custom_terms(self):
        """Round trip works with custom terms."""
        original = "Working on Project Falcon this week."
        anon_result = await anonymize(
            original,
            custom_terms=["Project Falcon"],
            use_ner=False,
        )
        assert "Project Falcon" not in anon_result.anonymized_text
        restored = await reidentify(anon_result.anonymized_text)
        assert restored == original

    @pytest.mark.asyncio
    async def test_round_trip_with_ner(self):
        """Round trip works with NER-detected entities."""
        original = "John Smith presented the quarterly results."
        anon_result = await anonymize(original, use_ner=True)

        if anon_result.entities:
            # If NER found entities, round trip should restore them
            restored = await reidentify(anon_result.anonymized_text)
            assert "John Smith" in restored or len(anon_result.entities) == 0

    @pytest.mark.asyncio
    async def test_round_trip_realistic(self):
        """Full realistic meeting notes round trip."""
        original = (
            "Email alice@example.com or call 555-123-4567. "
            "Visit https://internal.acme.com/status for details. "
            "Project Falcon is on track."
        )
        anon_result = await anonymize(
            original,
            custom_terms=["Project Falcon"],
            use_ner=False,
        )

        # Verify anonymization
        assert "alice@example.com" not in anon_result.anonymized_text
        assert "555-123-4567" not in anon_result.anonymized_text
        assert "Project Falcon" not in anon_result.anonymized_text

        # Verify round trip
        restored = await reidentify(anon_result.anonymized_text)
        assert restored == original


class TestAuditLog:
    @pytest.mark.asyncio
    async def test_anonymize_writes_audit_log(self, tmp_path, monkeypatch):
        """Anonymize writes an entry to the audit log."""
        log_path = tmp_path / "privacy" / "audit_log.jsonl"
        monkeypatch.setattr(
            "app.services.privacy_proxy.AUDIT_LOG_PATH", log_path
        )

        await anonymize(
            "Contact alice@example.com",
            use_ner=False,
        )

        assert log_path.exists()
        lines = log_path.read_text().strip().split("\n")
        entry = json.loads(lines[-1])
        assert entry["action"] == "anonymize"
        assert entry["entity_count"] >= 1
        assert "timestamp" in entry

    @pytest.mark.asyncio
    async def test_reidentify_writes_audit_log(self, tmp_path, monkeypatch):
        """Reidentify writes an entry to the audit log."""
        log_path = tmp_path / "privacy" / "audit_log.jsonl"
        monkeypatch.setattr(
            "app.services.privacy_proxy.AUDIT_LOG_PATH", log_path
        )

        # First anonymize to populate vault
        anon_result = await anonymize(
            "Contact alice@example.com",
            use_ner=False,
        )

        # Then reidentify
        await reidentify(anon_result.anonymized_text)

        lines = log_path.read_text().strip().split("\n")
        # Last entry should be from reidentify
        entry = json.loads(lines[-1])
        assert entry["action"] == "reidentify"
        assert entry["token_count"] >= 1
