"""Tests for VPMA VTT/SRT/TXT Parser (Task 35).

Tests that:
1. WebVTT files are parsed with speaker tags, NOTE/STYLE blocks, cue dedup
2. SRT files are parsed with cue numbers and timestamps stripped
3. Plain text files are cleaned up with minimal changes
4. parse_transcript_file dispatches based on file extension
5. Edge cases: empty files, malformed input, unsupported formats
"""

import pytest
from app.services.vtt_parser import (
    parse_srt,
    parse_transcript_file,
    parse_txt,
    parse_vtt,
)

# ============================================================
# WebVTT PARSING
# ============================================================


class TestParseVTT:
    def test_basic_vtt_with_speaker_tags(self):
        """Parse VTT with <v Speaker> tags into 'Speaker: text' format."""
        vtt = """WEBVTT

00:00:01.000 --> 00:00:05.000
<v Alice>Hello everyone, welcome to the meeting.</v>

00:00:05.500 --> 00:00:10.000
<v Bob>Thanks Alice, let's get started.</v>
"""
        result = parse_vtt(vtt)
        assert "Alice: Hello everyone, welcome to the meeting." in result
        assert "Bob: Thanks Alice, let's get started." in result

    def test_vtt_without_speaker_tags(self):
        """Parse VTT without voice tags — plain text preserved."""
        vtt = """WEBVTT

00:00:01.000 --> 00:00:05.000
This is a simple subtitle line.

00:00:05.500 --> 00:00:10.000
And another line of text.
"""
        result = parse_vtt(vtt)
        assert "This is a simple subtitle line." in result
        assert "And another line of text." in result

    def test_vtt_note_blocks_skipped(self):
        """NOTE blocks in VTT are completely skipped."""
        vtt = """WEBVTT

NOTE
This is a comment that should not appear in output.

00:00:01.000 --> 00:00:05.000
<v Alice>Actual dialog here.</v>
"""
        result = parse_vtt(vtt)
        assert "comment" not in result
        assert "Alice: Actual dialog here." in result

    def test_vtt_style_blocks_skipped(self):
        """STYLE blocks in VTT are completely skipped."""
        vtt = """WEBVTT

STYLE
::cue { color: white; }

00:00:01.000 --> 00:00:05.000
<v Alice>Styled dialog.</v>
"""
        result = parse_vtt(vtt)
        assert "color" not in result
        assert "STYLE" not in result
        assert "Alice: Styled dialog." in result

    def test_vtt_duplicate_cue_dedup(self):
        """Duplicate cue text is deduplicated."""
        vtt = """WEBVTT

00:00:01.000 --> 00:00:05.000
<v Alice>Same line repeated.</v>

00:00:05.000 --> 00:00:08.000
<v Alice>Same line repeated.</v>

00:00:08.000 --> 00:00:12.000
<v Alice>A different line.</v>
"""
        result = parse_vtt(vtt)
        assert result.count("Same line repeated.") == 1
        assert "A different line." in result

    def test_vtt_html_tags_stripped(self):
        """HTML tags like <i>, <b> are stripped from cue text."""
        vtt = """WEBVTT

00:00:01.000 --> 00:00:05.000
<v Alice>This is <i>important</i> and <b>bold</b>.</v>
"""
        result = parse_vtt(vtt)
        assert "Alice: This is important and bold." in result
        assert "<i>" not in result
        assert "<b>" not in result

    def test_vtt_voice_tag_without_closing(self):
        """Voice tags without closing </v> are handled."""
        vtt = """WEBVTT

00:00:01.000 --> 00:00:05.000
<v Alice>No closing tag here
"""
        result = parse_vtt(vtt)
        assert "Alice: No closing tag here" in result

    def test_vtt_empty_content(self):
        """Empty VTT produces empty output."""
        result = parse_vtt("WEBVTT\n\n")
        assert result == ""

    def test_vtt_with_cue_identifiers(self):
        """Cue identifiers (numbers before timestamps) are skipped."""
        vtt = """WEBVTT

1
00:00:01.000 --> 00:00:05.000
First subtitle.

2
00:00:05.500 --> 00:00:10.000
Second subtitle.
"""
        result = parse_vtt(vtt)
        assert "First subtitle." in result
        assert "Second subtitle." in result
        # Cue numbers should not appear as text
        lines = result.strip().split("\n")
        assert all(not line.strip().isdigit() for line in lines)

    def test_vtt_metadata_after_header(self):
        """Metadata lines after WEBVTT header are handled."""
        vtt = """WEBVTT - Meeting transcript
Kind: captions
Language: en

00:00:01.000 --> 00:00:05.000
<v Alice>Hello.</v>
"""
        result = parse_vtt(vtt)
        assert "Alice: Hello." in result


# ============================================================
# SRT PARSING
# ============================================================


class TestParseSRT:
    def test_basic_srt(self):
        """Parse standard SRT format."""
        srt = """1
00:00:01,000 --> 00:00:05,000
Hello from the first subtitle.

2
00:00:05,500 --> 00:00:10,000
And here is the second one.

3
00:00:10,500 --> 00:00:15,000
Final subtitle.
"""
        result = parse_srt(srt)
        assert "Hello from the first subtitle." in result
        assert "And here is the second one." in result
        assert "Final subtitle." in result

    def test_srt_cue_numbers_stripped(self):
        """Cue numbers are not in output."""
        srt = """1
00:00:01,000 --> 00:00:05,000
Text here.
"""
        result = parse_srt(srt)
        lines = result.strip().split("\n")
        assert len(lines) == 1
        assert lines[0] == "Text here."

    def test_srt_timestamps_stripped(self):
        """Timestamps are not in output."""
        srt = """1
00:00:01,000 --> 00:00:05,000
Some text.
"""
        result = parse_srt(srt)
        assert "-->" not in result

    def test_srt_html_tags_stripped(self):
        """HTML formatting tags in SRT are stripped."""
        srt = """1
00:00:01,000 --> 00:00:05,000
This is <i>italic</i> text.
"""
        result = parse_srt(srt)
        assert "This is italic text." in result
        assert "<i>" not in result

    def test_srt_duplicate_lines_deduped(self):
        """Duplicate subtitle lines are deduplicated."""
        srt = """1
00:00:01,000 --> 00:00:03,000
Repeated line.

2
00:00:03,000 --> 00:00:05,000
Repeated line.

3
00:00:05,000 --> 00:00:07,000
Unique line.
"""
        result = parse_srt(srt)
        assert result.count("Repeated line.") == 1
        assert "Unique line." in result

    def test_srt_empty(self):
        """Empty SRT produces empty output."""
        result = parse_srt("")
        assert result == ""


# ============================================================
# PLAIN TEXT PARSING
# ============================================================


class TestParseTXT:
    def test_basic_text(self):
        """Plain text is passed through with minimal cleanup."""
        text = "  Line one.  \n  Line two.  \n  Line three.  "
        result = parse_txt(text)
        assert "Line one." in result
        assert "Line two." in result
        assert "Line three." in result

    def test_blank_line_normalization(self):
        """Multiple blank lines are collapsed to single blank lines."""
        text = "First paragraph.\n\n\n\nSecond paragraph."
        result = parse_txt(text)
        lines = result.split("\n")
        # Should have at most one blank line between paragraphs
        consecutive_blanks = 0
        for line in lines:
            if not line:
                consecutive_blanks += 1
            else:
                consecutive_blanks = 0
            assert consecutive_blanks <= 1

    def test_trailing_blank_lines_removed(self):
        """Trailing blank lines are removed."""
        text = "Some text.\n\n\n"
        result = parse_txt(text)
        assert not result.endswith("\n")

    def test_empty_text(self):
        """Empty text produces empty output."""
        result = parse_txt("")
        assert result == ""


# ============================================================
# parse_transcript_file (FILE DISPATCH)
# ============================================================


class TestParseTranscriptFile:
    def test_vtt_extension(self, tmp_path):
        """Dispatches .vtt files to VTT parser."""
        vtt_file = tmp_path / "meeting.vtt"
        vtt_file.write_text("WEBVTT\n\n00:00:01.000 --> 00:00:05.000\n<v Alice>Hello.</v>\n")
        result = parse_transcript_file(vtt_file)
        assert "Alice: Hello." in result

    def test_srt_extension(self, tmp_path):
        """Dispatches .srt files to SRT parser."""
        srt_file = tmp_path / "meeting.srt"
        srt_file.write_text("1\n00:00:01,000 --> 00:00:05,000\nHello.\n")
        result = parse_transcript_file(srt_file)
        assert "Hello." in result

    def test_txt_extension(self, tmp_path):
        """Dispatches .txt files to TXT parser."""
        txt_file = tmp_path / "notes.txt"
        txt_file.write_text("Meeting notes here.\n")
        result = parse_transcript_file(txt_file)
        assert "Meeting notes here." in result

    def test_unsupported_extension(self, tmp_path):
        """Raises ValueError for unsupported file types."""
        pdf_file = tmp_path / "meeting.pdf"
        pdf_file.write_text("fake pdf")
        with pytest.raises(ValueError, match="Unsupported transcript format"):
            parse_transcript_file(pdf_file)

    def test_file_not_found(self):
        """Raises FileNotFoundError for missing files."""
        with pytest.raises(FileNotFoundError):
            parse_transcript_file("/nonexistent/file.vtt")

    def test_case_insensitive_extension(self, tmp_path):
        """File extension matching is case-insensitive."""
        vtt_file = tmp_path / "meeting.VTT"
        vtt_file.write_text("WEBVTT\n\n00:00:01.000 --> 00:00:05.000\nHello.\n")
        result = parse_transcript_file(vtt_file)
        assert "Hello." in result
