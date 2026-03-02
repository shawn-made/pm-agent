#!/usr/bin/env python3
"""Doc-freshness pre-commit hook.

Compares actual codebase structure against claims in docs/EXECUTIVE_SUMMARY.md.
Warns (never blocks) when documentation is stale.

Checks: API endpoints, DB tables, service modules, components, pages.
Skips: test counts (require running the test suite — handled by session close protocol).
"""

import os
import re
import sys

# Resolve project root (script lives in scripts/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ROUTES_FILE = os.path.join(PROJECT_ROOT, "backend", "app", "api", "routes.py")
DATABASE_FILE = os.path.join(PROJECT_ROOT, "backend", "app", "services", "database.py")
SERVICES_DIR = os.path.join(PROJECT_ROOT, "backend", "app", "services")
COMPONENTS_DIR = os.path.join(PROJECT_ROOT, "frontend", "src", "components")
PAGES_DIR = os.path.join(PROJECT_ROOT, "frontend", "src", "pages")
EXEC_SUMMARY = os.path.join(PROJECT_ROOT, "docs", "EXECUTIVE_SUMMARY.md")


def count_endpoints():
    """Count @router.{method} decorators in routes.py."""
    if not os.path.exists(ROUTES_FILE):
        return -1
    with open(ROUTES_FILE) as f:
        content = f.read()
    return len(re.findall(r"@router\.(get|post|put|delete|patch)\(", content))


def count_tables():
    """Count CREATE TABLE statements in database.py."""
    if not os.path.exists(DATABASE_FILE):
        return -1
    with open(DATABASE_FILE) as f:
        content = f.read()
    return len(re.findall(r"CREATE TABLE IF NOT EXISTS", content, re.IGNORECASE))


def count_services():
    """Count .py service modules (excluding __init__.py)."""
    if not os.path.isdir(SERVICES_DIR):
        return -1
    return len([
        f for f in os.listdir(SERVICES_DIR)
        if f.endswith(".py") and f != "__init__.py"
    ])


def count_jsx_files(directory, exclude_tests=True):
    """Count .jsx files in a directory, optionally excluding test files."""
    if not os.path.isdir(directory):
        return -1
    files = [f for f in os.listdir(directory) if f.endswith(".jsx")]
    if exclude_tests:
        files = [f for f in files if ".test." not in f]
    return len(files)


def parse_executive_summary():
    """Extract claimed counts from EXECUTIVE_SUMMARY.md Codebase Statistics section."""
    if not os.path.exists(EXEC_SUMMARY):
        return {}

    with open(EXEC_SUMMARY) as f:
        content = f.read()

    claimed = {}

    # Pattern: "10 service modules, 8 database tables, 15 API endpoints"
    m = re.search(r"(\d+)\s+service modules?,\s*(\d+)\s+database tables?,\s*(\d+)\s+API endpoints?", content)
    if m:
        claimed["services"] = int(m.group(1))
        claimed["tables"] = int(m.group(2))
        claimed["endpoints"] = int(m.group(3))

    # Pattern: "7 components, 4 pages"
    m = re.search(r"(\d+)\s+components?,\s*(\d+)\s+pages?", content)
    if m:
        claimed["components"] = int(m.group(1))
        claimed["pages"] = int(m.group(2))

    return claimed


def main():
    actual = {
        "endpoints": count_endpoints(),
        "tables": count_tables(),
        "services": count_services(),
        "components": count_jsx_files(COMPONENTS_DIR),
        "pages": count_jsx_files(PAGES_DIR),
    }

    claimed = parse_executive_summary()

    if not claimed:
        print("doc-freshness: Could not parse EXECUTIVE_SUMMARY.md — skipping check")
        return 0

    mismatches = []
    for key, actual_count in actual.items():
        if actual_count == -1:
            continue  # File/dir not found, skip
        claimed_count = claimed.get(key)
        if claimed_count is not None and actual_count != claimed_count:
            mismatches.append(
                f"  {key}: docs say {claimed_count}, actual is {actual_count}"
            )

    if mismatches:
        print("doc-freshness: Documentation is stale!")
        print("\n".join(mismatches))
        print("\nUpdate docs/EXECUTIVE_SUMMARY.md (see CLAUDE.md Session Close Protocol step 5)")
        # Exit 0 — warn but never block the commit
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
