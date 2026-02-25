"""Test fixtures — use a temporary SQLite database and artifacts dir for each test."""

from unittest.mock import patch

import pytest_asyncio
from app.services import artifact_manager, database


@pytest_asyncio.fixture(autouse=True)
async def tmp_database(tmp_path):
    """Override DB_PATH, VPMA_DIR, and ARTIFACTS_DIR to use temp dirs per test."""
    test_db = tmp_path / "test_vpma.db"
    test_artifacts = tmp_path / "artifacts"

    with patch.object(database, "DB_PATH", test_db), \
         patch.object(database, "VPMA_DIR", tmp_path), \
         patch.object(artifact_manager, "ARTIFACTS_DIR", test_artifacts):
        await database.init_db()
        yield test_db
