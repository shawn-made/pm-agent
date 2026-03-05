"""VPMA Transcript Watcher — file system watcher for transcript auto-processing.

Monitors a configured folder for new transcript files (.vtt, .srt, .txt) and
automatically processes them through the artifact sync pipeline.

Design decision D43: Runs as a background asyncio task in the FastAPI process
(not a separate daemon). Uses watchdog for filesystem events.

Features:
- Configurable watch folder and processing mode (extract/log_session)
- 2-second debounce for partial writes
- Manifest tracking to avoid reprocessing
- Start/stop/status API
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

from app.services.artifact_sync import run_artifact_sync
from app.services.vtt_parser import parse_transcript_file

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".vtt", ".srt", ".txt"}
DEBOUNCE_SECONDS = 2.0
MANIFEST_FILENAME = "transcript_manifest.json"
MAX_RECENT_FILES = 10


class TranscriptWatcher:
    """Watches a folder for transcript files and processes them.

    Lifecycle:
        watcher = TranscriptWatcher()
        await watcher.start(watch_folder="/path/to/transcripts", mode="extract")
        ...
        await watcher.stop()
    """

    def __init__(self):
        self._running = False
        self._task: asyncio.Task | None = None
        self._watch_folder: str | None = None
        self._mode: str = "extract"
        self._project_id: str = "default"
        self._manifest: dict = {}
        self._manifest_path: Path | None = None
        self._recent_files: list[dict] = []
        self._observer = None  # watchdog observer

    @property
    def is_running(self) -> bool:
        return self._running and self._task is not None and not self._task.done()

    @property
    def watch_folder(self) -> str | None:
        return self._watch_folder

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def recent_files(self) -> list[dict]:
        return self._recent_files[:MAX_RECENT_FILES]

    def status(self) -> dict:
        """Return current watcher status."""
        return {
            "running": self.is_running,
            "watch_folder": self._watch_folder,
            "mode": self._mode,
            "project_id": self._project_id,
            "files_processed": len(self._manifest),
            "recent_files": self.recent_files,
        }

    async def start(
        self,
        watch_folder: str,
        mode: str = "extract",
        project_id: str = "default",
    ) -> bool:
        """Start watching a folder for transcript files.

        Args:
            watch_folder: Path to the folder to watch.
            mode: Processing mode — 'extract' or 'log_session'.
            project_id: Project to associate processed transcripts with.

        Returns:
            True if started successfully, False if already running or invalid folder.
        """
        if self.is_running:
            logger.warning("Transcript watcher already running")
            return False

        folder = Path(watch_folder)
        if not folder.is_dir():
            logger.error("Watch folder does not exist: %s", watch_folder)
            return False

        if mode not in ("extract", "log_session"):
            logger.warning("Invalid mode '%s', defaulting to 'extract'", mode)
            mode = "extract"

        self._watch_folder = watch_folder
        self._mode = mode
        self._project_id = project_id

        # Load or create manifest
        self._manifest_path = folder / MANIFEST_FILENAME
        self._load_manifest()

        # Start the polling loop as a background task
        self._running = True
        self._task = asyncio.create_task(self._watch_loop())
        logger.info(
            "Transcript watcher started: folder=%s, mode=%s, project=%s",
            watch_folder,
            mode,
            project_id,
        )
        return True

    async def stop(self) -> bool:
        """Stop the transcript watcher.

        Returns:
            True if stopped successfully, False if not running.
        """
        if not self.is_running:
            return False

        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

        logger.info("Transcript watcher stopped")
        return True

    async def process_file(self, file_path: str) -> dict:
        """Process a single transcript file through the artifact sync pipeline.

        Args:
            file_path: Path to the transcript file.

        Returns:
            Dict with processing result (status, file, mode, etc.).
        """
        path = Path(file_path)
        result = {
            "file": str(path.name),
            "path": str(path),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "error",
            "mode": self._mode,
        }

        try:
            # Parse the transcript
            parsed_text = parse_transcript_file(path)
            if not parsed_text.strip():
                result["status"] = "skipped"
                result["reason"] = "Empty transcript after parsing"
                logger.info("Skipped empty transcript: %s", path.name)
                self._add_recent(result)
                return result

            # Process through artifact sync pipeline
            sync_result = await run_artifact_sync(
                text=parsed_text,
                project_id=self._project_id,
                mode=self._mode,
            )

            result["status"] = "processed"
            result["suggestion_count"] = len(sync_result.suggestions)
            result["session_id"] = sync_result.session_id
            # Store full sync result for frontend display (Task 41)
            result["sync_result"] = {
                "suggestions": [
                    s.dict() if hasattr(s, "dict") else s for s in sync_result.suggestions
                ],
                "input_type": sync_result.input_type,
                "pii_detected": sync_result.pii_detected,
                "session_id": sync_result.session_id,
                "mode": sync_result.mode,
            }
            if self._mode == "log_session":
                result["lpd_update_count"] = len(sync_result.lpd_updates)
                result["sync_result"]["lpd_updates"] = [
                    u.dict() if hasattr(u, "dict") else u for u in sync_result.lpd_updates
                ]
                result["sync_result"]["session_summary"] = sync_result.session_summary

            # Update manifest
            self._manifest[str(path)] = {
                "processed_at": result["timestamp"],
                "status": "processed",
            }
            self._save_manifest()

            logger.info("Processed transcript: %s (%s)", path.name, self._mode)

        except FileNotFoundError:
            result["status"] = "error"
            result["reason"] = "File not found"
            logger.error("Transcript file not found: %s", path)
        except ValueError as e:
            result["status"] = "error"
            result["reason"] = str(e)
            logger.error("Invalid transcript file: %s — %s", path, e)
        except Exception:
            result["status"] = "error"
            result["reason"] = "Processing failed"
            logger.error("Failed to process transcript: %s", path.name, exc_info=True)

        self._add_recent(result)
        return result

    async def _watch_loop(self):
        """Background polling loop that checks for new files.

        Uses a simple poll-and-debounce approach rather than watchdog's
        Observer for better cross-platform compatibility and simpler
        async integration.
        """
        pending: dict[str, float] = {}  # path → first-seen timestamp

        while self._running:
            try:
                folder = Path(self._watch_folder)
                if not folder.is_dir():
                    await asyncio.sleep(5)
                    continue

                # Scan for new transcript files
                now = time.monotonic()
                for child in folder.iterdir():
                    if not child.is_file():
                        continue
                    if child.suffix.lower() not in SUPPORTED_EXTENSIONS:
                        continue
                    if child.name == MANIFEST_FILENAME:
                        continue

                    file_key = str(child)
                    if file_key in self._manifest:
                        continue  # Already processed

                    if file_key not in pending:
                        pending[file_key] = now
                        continue  # Start debounce

                    # Check if debounce period has elapsed
                    if now - pending[file_key] >= DEBOUNCE_SECONDS:
                        # Check file size stability (debounce for partial writes)
                        try:
                            size1 = child.stat().st_size
                            await asyncio.sleep(0.5)
                            size2 = child.stat().st_size
                            if size1 != size2:
                                # Still being written
                                pending[file_key] = now
                                continue
                        except OSError:
                            continue

                        del pending[file_key]
                        await self.process_file(file_key)

                # Clean up pending entries for files that no longer exist
                for key in list(pending.keys()):
                    if not Path(key).exists():
                        del pending[key]

                await asyncio.sleep(1)  # Poll interval

            except asyncio.CancelledError:
                raise
            except Exception:
                logger.error("Error in transcript watcher loop", exc_info=True)
                await asyncio.sleep(5)

    def _load_manifest(self):
        """Load the processing manifest from disk."""
        if self._manifest_path and self._manifest_path.exists():
            try:
                self._manifest = json.loads(self._manifest_path.read_text())
            except (json.JSONDecodeError, OSError):
                logger.warning("Failed to load transcript manifest, starting fresh")
                self._manifest = {}
        else:
            self._manifest = {}

    def _save_manifest(self):
        """Save the processing manifest to disk."""
        if self._manifest_path:
            try:
                self._manifest_path.write_text(json.dumps(self._manifest, indent=2))
            except OSError:
                logger.error("Failed to save transcript manifest", exc_info=True)

    def _add_recent(self, result: dict):
        """Add a processing result to the recent files list."""
        self._recent_files.insert(0, result)
        self._recent_files = self._recent_files[:MAX_RECENT_FILES]


# Module-level singleton for the watcher
_watcher_instance: TranscriptWatcher | None = None


def get_transcript_watcher() -> TranscriptWatcher:
    """Get the singleton TranscriptWatcher instance."""
    global _watcher_instance
    if _watcher_instance is None:
        _watcher_instance = TranscriptWatcher()
    return _watcher_instance
