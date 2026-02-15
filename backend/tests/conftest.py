"""Test fixtures — use a temporary SQLite database for each test."""

from unittest.mock import patch

import pytest_asyncio
from app.services import database


@pytest_asyncio.fixture(autouse=True)
async def tmp_database(tmp_path):
    """Override DB_PATH to use a temp file for each test."""
    test_db = tmp_path / "test_vpma.db"

    with patch.object(database, "DB_PATH", test_db), \
         patch.object(database, "VPMA_DIR", tmp_path):
        await database.init_db()
        yield test_db
