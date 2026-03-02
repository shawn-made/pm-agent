# VPMA Quality Assurance Plan

**Last Updated**: 2026-02-25 (updated for Phase 1A)
**Status**: Active — integrated into development workflow

---

## Quality Gates

Every code change passes through these gates in order. If a gate fails, the commit is blocked.

### Gate 1: Pre-Commit (Automatic, <15 seconds)

Runs on every `git commit` via `.pre-commit-config.yaml`:

| Check | Tool | What It Catches |
|-------|------|-----------------|
| Lint | `ruff` | Python style violations, import ordering |
| Format | `ruff-format` | Inconsistent formatting |
| Security | `bandit` | SQL injection, hardcoded secrets, unsafe patterns |
| Smoke tests | `pytest -m smoke` | Broken health check, database init, privacy proxy, critical paths |
| Architecture | `pytest -m smoke` (includes arch tests) | Layer boundary violations, direct SDK imports, circular dependencies |
| File hygiene | `pre-commit-hooks` | Merge conflicts, private keys, large files, trailing whitespace |

**If any check fails**: Fix the issue, re-stage, commit again. Do not use `--no-verify`.

### Gate 2: Full Test Suite (Manual, before PR or merge)

```bash
# Backend (425+ tests, ~5 seconds)
cd backend && python -m pytest tests/ -v

# Frontend (77 tests, ~1 second)
cd frontend && npm test

# Backend with coverage
cd backend && python -m pytest tests/ -v --cov=app --cov-report=term-missing
```

**Coverage target**: Maintain >90% backend coverage. Current: 96%.

### Gate 3: Security Audit (Periodic, monthly or before release)

```bash
# Python dependency vulnerabilities
cd backend && pip-audit

# Frontend dependency vulnerabilities
cd frontend && npm audit

# Python static security analysis (full report)
cd backend && bandit -r app/ -c ../bandit.yaml -f txt
```

**Action**: Fix all HIGH severity findings immediately. MEDIUM within the current sprint.

---

## Test Categories

### Smoke Tests (`@pytest.mark.smoke`)
**Purpose**: 2-second sanity check. Runs on every commit.
**File**: [test_smoke.py](backend/tests/test_smoke.py)
**Coverage**: App boots, database initialized, privacy proxy roundtrip, input validation, artifact types loaded, LPD initialization, context injection, section update roundtrip, intake endpoint reachable.

### Architecture Tests (`@pytest.mark.smoke`)
**Purpose**: Enforce layer boundaries via AST import analysis. Runs on every commit.
**File**: [test_architecture.py](backend/tests/test_architecture.py)
**Coverage**:
- API layer does not directly import database
- Models have no service/api dependencies
- Prompts are pure strings (no app imports)
- Business logic uses abstract LLM client (no direct anthropic/google imports)
- CRUD layer does not import LLM or privacy proxy
- LLM provider adapters only import base client

### Unit Tests
**Purpose**: Test individual functions and classes in isolation.
**Files**: `test_crud.py`, `test_privacy_proxy.py`, `test_llm_client.py`, `test_artifact_manager.py`, `test_lpd_manager.py`, `test_lpd_crud.py`, `test_lpd_schema.py`, `test_log_session.py`, `test_return_path.py`, `test_prompt_refinement.py`, `test_intake.py`, `test_samples.py`
**Pattern**: Mock external dependencies (database, LLM, file system). Use `tmp_path` fixtures for file operations.

### Integration Tests
**Purpose**: Test full request flows through the API.
**Files**: `test_integration.py`, `test_api.py`, `test_context_injection.py`, `test_lpd_routes.py`
**Pattern**: Use `httpx.AsyncClient` with `ASGITransport`. Mock LLM responses with realistic JSON. Verify end-to-end: input → anonymize → LLM → reidentify → response.

### Frontend Tests
**Purpose**: Component rendering, user interaction, API integration.
**Files**: `src/**/*.test.jsx`
**Framework**: Vitest + Testing Library
**Pattern**: Mock API service layer. Test user-visible behavior, not implementation details.

---

## Architecture Enforcement Rules

These rules are tested automatically on every commit. Violating them requires removing the test (which should trigger a DECISIONS.md entry explaining why).

| Rule | Enforced In | Rationale |
|------|------------|-----------|
| API → services only (not database) | `test_architecture.py` | API layer delegates to services, never touches storage directly |
| Models → no app imports | `test_architecture.py` | Pydantic models are pure data shapes |
| Prompts → no app imports | `test_architecture.py` | Prompt templates are plain strings |
| Services → llm_client only (not anthropic/google) | `test_architecture.py` | Abstract LLM client pattern (D1) |
| CRUD → no LLM/privacy deps | `test_architecture.py` | Data access layer is below business logic |
| LLM adapters → base client only | `test_architecture.py` | Provider adapters are leaf nodes |

---

## Security Scanning

### Automated (Pre-Commit)
- **Bandit**: Scans all Python in `backend/app/` for OWASP-style vulnerabilities
- **detect-private-key**: Catches accidentally committed keys/certs
- **check-added-large-files**: Prevents binary blobs (>500KB)

### Periodic (Monthly)
- **pip-audit**: Checks Python dependencies against OSV database
- **npm audit**: Checks JS dependencies against npm advisory database
- Run both before any release or major merge

### Configuration
- Bandit config: [bandit.yaml](bandit.yaml)
- Pre-commit config: [.pre-commit-config.yaml](.pre-commit-config.yaml)

---

## When to Run What

| Trigger | What Runs | Time |
|---------|-----------|------|
| Every commit | Pre-commit hooks (Gate 1) | <15s |
| After code changes | Full test suite (Gate 2) | ~6s |
| Before merge/PR | Full suite + coverage + lint | ~10s |
| Monthly / before release | Security audit (Gate 3) | ~30s |
| After adding new service | Update architecture tests | 5 min |
| After adding new model | Verify models test passes | Automatic |

---

## Adding New Tests

### New service module
1. Create `test_<module>.py` in `backend/tests/`
2. Add the module to the parametrized lists in `test_architecture.py` (LLM abstraction checks)
3. Write unit tests with mocked dependencies
4. Add one smoke test if it's a critical path

### New API endpoint
1. Add integration test in `test_api.py` or `test_integration.py`
2. Test both success and error paths (400, 404, 502)
3. Mock LLM responses with realistic JSON
4. If the endpoint modifies artifacts or LPD, verify side effects

### New frontend component
1. Create `<Component>.test.jsx` alongside the component
2. Mock API calls via `vi.mock('../services/api')`
3. Test rendering, user interaction, and error states
4. Use `screen.getByRole()` over `getByTestId()` where possible

---

## Tier 2 Roadmap (Planned, Not Yet Implemented)

These are researched and ready to implement when capacity allows:

| Practice | Tool | Status | Priority |
|----------|------|--------|----------|
| API contract testing | Schemathesis | Researched | High — auto-tests from OpenAPI spec |
| Test data factories | Polyfactory | Researched | Medium — eliminates hand-crafted Pydantic instances |
| Mutation testing | mutmut | Researched | Medium — periodic audit on privacy_proxy, crud |
| Snapshot testing | syrupy | Researched | Medium — catch prompt template drift |
| Dead code detection | Vulture + Knip | Researched | Low — one-time cleanup |
| Complexity metrics | Radon | Researched | Low — flag functions with CC > 10 |

---

## Key Decisions

- **D-QA1**: Architecture tests use AST parsing for direct imports only (not transitive). Transitive violations are expected (routes → services → database) and not bugs.
- **D-QA2**: Smoke tests run as pre-commit gate. Full suite is manual. This balances speed with thoroughness.
- **D-QA3**: Security scanning (bandit) excludes test files — tests intentionally use mock credentials and patterns that would trigger false positives.
- **D-QA4**: ~~`database.py → crud` circular import~~ — **Resolved.** Moved `ensure_default_project()` from `database.init_db()` to `main.py` lifespan startup hook. Architecture test now passes cleanly (no xfail).
