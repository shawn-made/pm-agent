"""VPMA Database — SQLite connection and initialization."""

from pathlib import Path

import aiosqlite

# Database lives in <project_root>/data/ (kept out of git via .gitignore)
_PROJECT_ROOT = Path(__file__).resolve().parents[3]  # backend/app/services → project root
VPMA_DIR = _PROJECT_ROOT / "data"
DB_PATH = VPMA_DIR / "vpma.db"


async def get_db() -> aiosqlite.Connection:
    """Get a database connection."""
    db = await aiosqlite.connect(str(DB_PATH))
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return db


async def init_db():
    """Create tables if they don't exist. Called on app startup."""
    VPMA_DIR.mkdir(parents=True, exist_ok=True)

    # Ensure subdirectories exist
    for subdir in ["artifacts", "privacy", "feedback", "analytics"]:
        (VPMA_DIR / subdir).mkdir(exist_ok=True)

    db = await get_db()
    try:
        await db.executescript(SCHEMA)
        await db.commit()
    finally:
        await db.close()


SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    project_id TEXT PRIMARY KEY,
    project_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    landscape_config TEXT DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS artifacts (
    artifact_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    artifact_type TEXT NOT NULL,
    file_path TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

CREATE TABLE IF NOT EXISTS artifact_versions (
    version_id TEXT PRIMARY KEY,
    artifact_id TEXT NOT NULL,
    version_number INTEGER NOT NULL,
    content_snapshot TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id TEXT,
    FOREIGN KEY (artifact_id) REFERENCES artifacts(artifact_id),
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tab_used TEXT,
    user_input TEXT,
    agent_output TEXT,
    persona_used TEXT,
    tokens_used INTEGER DEFAULT 0,
    llm_model TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

CREATE TABLE IF NOT EXISTS pii_vault (
    token TEXT PRIMARY KEY,
    original_value TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS lpd_sections (
    section_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    section_name TEXT NOT NULL,
    content TEXT DEFAULT '',
    section_order INTEGER NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verified_at TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    UNIQUE(project_id, section_name)
);

CREATE TABLE IF NOT EXISTS lpd_session_summaries (
    summary_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    session_id TEXT,
    summary_text TEXT NOT NULL,
    entities_extracted TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
"""
