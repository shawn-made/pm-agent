"""VPMA VTT/SRT/TXT Parser — pure-function transcript file parser.

Parses transcript files into clean speaker-tagged plain text suitable
for the artifact sync pipeline.

Supported formats:
- WebVTT (.vtt): Handles <v> speaker tags, NOTE/STYLE blocks, cue dedup
- SubRip (.srt): Standard numbered subtitle format
- Plain text (.txt): Passthrough with minimal cleanup

Design decision D44: Parser is a separate pure-function module from the
watcher service for testability and reuse.
"""

import re
from pathlib import Path

# WebVTT voice tag pattern: <v Speaker Name>text</v> or <v Speaker Name>text
_VTT_VOICE_TAG = re.compile(r"<v\s+([^>]+)>(.*?)(?:</v>)?$")

# HTML-style tags to strip from cue text
_HTML_TAGS = re.compile(r"<[^>]+>")

# WebVTT timestamp line: 00:00:00.000 --> 00:00:05.000
_VTT_TIMESTAMP = re.compile(r"\d{2}:\d2,?\d*\s*-->\s*\d")
_VTT_TIMESTAMP_FULL = re.compile(
    r"(\d{1,2}:)?\d{2}:\d{2}[.,]\d{1,3}\s*-->\s*(\d{1,2}:)?\d{2}:\d{2}[.,]\d{1,3}"
)

# SRT timestamp line: 00:00:00,000 --> 00:00:05,000
_SRT_TIMESTAMP = _VTT_TIMESTAMP_FULL  # Same pattern covers both

# SRT cue number (just digits on a line by themselves)
_SRT_CUE_NUMBER = re.compile(r"^\d+\s*$")


def parse_vtt(text: str) -> str:
    """Parse WebVTT content into clean speaker-tagged text.

    Handles:
    - WEBVTT header and metadata lines
    - NOTE and STYLE blocks (skipped)
    - <v Speaker>text</v> voice tags → "Speaker: text"
    - Overlapping/duplicate cue text dedup
    - HTML tag stripping
    - Timestamp lines (stripped)

    Args:
        text: Raw WebVTT file content.

    Returns:
        Clean plain text with speaker attribution where available.
    """
    lines = text.split("\n")
    output_lines: list[str] = []
    seen_text: set[str] = set()
    in_note_block = False
    in_style_block = False
    skip_header = True

    for line in lines:
        stripped = line.strip()

        # Skip WEBVTT header line
        if skip_header:
            if stripped.startswith("WEBVTT"):
                continue
            # Skip blank lines and metadata after header
            if not stripped:
                continue
            skip_header = False

        # NOTE blocks: skip until blank line
        if stripped.startswith("NOTE"):
            in_note_block = True
            continue
        if in_note_block:
            if not stripped:
                in_note_block = False
            continue

        # STYLE blocks: skip until blank line
        if stripped.startswith("STYLE"):
            in_style_block = True
            continue
        if in_style_block:
            if not stripped:
                in_style_block = False
            continue

        # Skip timestamp lines
        if _VTT_TIMESTAMP_FULL.search(stripped):
            continue

        # Skip cue identifiers (numeric or text before timestamps)
        if _SRT_CUE_NUMBER.match(stripped):
            continue

        # Skip blank lines
        if not stripped:
            continue

        # Process cue text
        voice_match = _VTT_VOICE_TAG.match(stripped)
        if voice_match:
            speaker = voice_match.group(1).strip()
            cue_text = voice_match.group(2).strip()
            cue_text = _HTML_TAGS.sub("", cue_text).strip()
            if cue_text and cue_text not in seen_text:
                seen_text.add(cue_text)
                output_lines.append(f"{speaker}: {cue_text}")
        else:
            # No voice tag — strip HTML tags and emit
            clean = _HTML_TAGS.sub("", stripped).strip()
            if clean and clean not in seen_text:
                seen_text.add(clean)
                output_lines.append(clean)

    return "\n".join(output_lines)


def parse_srt(text: str) -> str:
    """Parse SubRip (.srt) content into clean plain text.

    Args:
        text: Raw SRT file content.

    Returns:
        Clean plain text with duplicate lines removed.
    """
    lines = text.split("\n")
    output_lines: list[str] = []
    seen_text: set[str] = set()

    for line in lines:
        stripped = line.strip()

        # Skip cue numbers
        if _SRT_CUE_NUMBER.match(stripped):
            continue

        # Skip timestamp lines
        if _VTT_TIMESTAMP_FULL.search(stripped):
            continue

        # Skip blank lines
        if not stripped:
            continue

        # Strip HTML tags (SRT sometimes has <i>, <b>, etc.)
        clean = _HTML_TAGS.sub("", stripped).strip()
        if clean and clean not in seen_text:
            seen_text.add(clean)
            output_lines.append(clean)

    return "\n".join(output_lines)


def parse_txt(text: str) -> str:
    """Parse plain text file — minimal cleanup only.

    Strips leading/trailing whitespace and normalizes blank lines.

    Args:
        text: Raw text file content.

    Returns:
        Cleaned text.
    """
    lines = text.split("\n")
    output_lines: list[str] = []
    prev_blank = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if not prev_blank and output_lines:
                output_lines.append("")
            prev_blank = True
        else:
            output_lines.append(stripped)
            prev_blank = False

    # Remove trailing blank lines
    while output_lines and not output_lines[-1]:
        output_lines.pop()

    return "\n".join(output_lines)


def parse_transcript_file(file_path: str | Path) -> str:
    """Parse a transcript file based on its extension.

    Supported extensions: .vtt, .srt, .txt

    Args:
        file_path: Path to the transcript file.

    Returns:
        Clean plain text from the transcript.

    Raises:
        ValueError: If the file extension is not supported.
        FileNotFoundError: If the file does not exist.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Transcript file not found: {path}")

    content = path.read_text(encoding="utf-8")
    ext = path.suffix.lower()

    if ext == ".vtt":
        return parse_vtt(content)
    elif ext == ".srt":
        return parse_srt(content)
    elif ext == ".txt":
        return parse_txt(content)
    else:
        raise ValueError(f"Unsupported transcript format: {ext} (supported: .vtt, .srt, .txt)")
