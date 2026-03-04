"""Architecture enforcement tests — validate layer boundaries.

These tests ensure architectural rules are permanently enforced:
- API layer never DIRECTLY imports database
- Services never DIRECTLY import from the API layer
- All LLM calls go through the abstract client (not direct SDK imports)
- Models/schemas have no service-layer dependencies
- Prompt templates are pure strings with no runtime dependencies

Uses AST parsing to check DIRECT imports only (not transitive).
This avoids false positives from legitimate chains like:
  routes → artifact_sync → llm_client → llm_claude → anthropic

Run time: <1 second. These parse import graphs, they don't execute app code.
"""

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.smoke  # Fast enough to run as smoke tests

# Path to the app package
APP_DIR = Path(__file__).parent.parent / "app"


def _get_direct_imports(module_path: Path) -> set[str]:
    """Parse a Python file and return all directly imported module names."""
    source = module_path.read_text()
    tree = ast.parse(source)
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)
    return imports


def _module_directly_imports(module_path: Path, forbidden_prefix: str) -> list[str]:
    """Check if a module directly imports anything matching the forbidden prefix."""
    direct = _get_direct_imports(module_path)
    return [imp for imp in direct if imp.startswith(forbidden_prefix)]


class TestLayerBoundaries:
    """Enforce that direct dependencies flow downward: api -> services -> models."""

    def test_api_does_not_directly_import_database(self):
        """API routes must go through services/crud, never touch database.py directly."""
        violations = _module_directly_imports(
            APP_DIR / "api" / "routes.py", "app.services.database"
        )
        assert violations == [], f"routes.py directly imports database: {violations}"

    def test_models_do_not_import_services(self):
        """Pydantic models must be pure data definitions — no service dependencies."""
        for py_file in (APP_DIR / "models").glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            violations = _module_directly_imports(py_file, "app.services")
            assert violations == [], f"{py_file.name} imports services: {violations}"

    def test_models_do_not_import_api(self):
        """Models must never depend on API layer."""
        for py_file in (APP_DIR / "models").glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            violations = _module_directly_imports(py_file, "app.api")
            assert violations == [], f"{py_file.name} imports api: {violations}"

    def test_prompts_are_pure_strings(self):
        """Prompt templates must have no app-level imports (services, models, api)."""
        for py_file in (APP_DIR / "prompts").glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            imports = _get_direct_imports(py_file)
            app_imports = [i for i in imports if i.startswith("app.")]
            assert app_imports == [], f"{py_file.name} has app imports: {app_imports}"

    def test_database_does_not_directly_import_crud(self):
        """Database module must not directly import crud (crud depends on database, not vice versa)."""
        violations = _module_directly_imports(
            APP_DIR / "services" / "database.py", "app.services.crud"
        )
        assert violations == [], f"database.py directly imports crud: {violations}"

    def test_database_does_not_directly_import_models(self):
        """Database module should not directly depend on Pydantic models."""
        violations = _module_directly_imports(APP_DIR / "services" / "database.py", "app.models")
        assert violations == [], f"database.py directly imports models: {violations}"


class TestLLMAbstraction:
    """Enforce that business logic uses the abstract LLM client, not provider SDKs directly."""

    @pytest.mark.parametrize(
        "service_file",
        [
            "artifact_sync.py",
            "privacy_proxy.py",
            "crud.py",
            "artifact_manager.py",
            "lpd_manager.py",
            "intake.py",
            "content_gate.py",
            "transcript_watcher.py",
            "vtt_parser.py",
            "deep_strategy.py",
            "risk_prediction.py",
            "reconciliation.py",
        ],
    )
    def test_services_do_not_import_anthropic_sdk(self, service_file):
        """Business logic must use llm_client.py, never import anthropic SDK directly."""
        path = APP_DIR / "services" / service_file
        if not path.exists():
            pytest.skip(f"{service_file} not found")
        violations = _module_directly_imports(path, "anthropic")
        assert violations == [], f"{service_file} directly imports anthropic: {violations}"

    @pytest.mark.parametrize(
        "service_file",
        [
            "artifact_sync.py",
            "privacy_proxy.py",
            "crud.py",
            "artifact_manager.py",
            "lpd_manager.py",
            "intake.py",
            "content_gate.py",
            "transcript_watcher.py",
            "vtt_parser.py",
            "deep_strategy.py",
            "risk_prediction.py",
            "reconciliation.py",
        ],
    )
    def test_services_do_not_import_google_genai_sdk(self, service_file):
        """Business logic must use llm_client.py, never import google.genai directly."""
        path = APP_DIR / "services" / service_file
        if not path.exists():
            pytest.skip(f"{service_file} not found")
        violations = _module_directly_imports(path, "google")
        assert violations == [], f"{service_file} directly imports google: {violations}"

    def test_api_does_not_import_anthropic(self):
        """API routes must never directly reference LLM provider SDKs."""
        violations = _module_directly_imports(APP_DIR / "api" / "routes.py", "anthropic")
        assert violations == [], f"routes.py directly imports anthropic: {violations}"

    def test_api_does_not_import_google_genai(self):
        """API routes must never directly reference Google GenAI."""
        violations = _module_directly_imports(APP_DIR / "api" / "routes.py", "google")
        assert violations == [], f"routes.py directly imports google: {violations}"


class TestPrivacyBoundaries:
    """Enforce privacy proxy pattern integrity."""

    def test_crud_does_not_import_llm(self):
        """Database CRUD layer must never call LLM services."""
        violations = _module_directly_imports(
            APP_DIR / "services" / "crud.py", "app.services.llm_client"
        )
        assert violations == [], f"crud.py directly imports llm_client: {violations}"

    def test_crud_does_not_import_privacy_proxy(self):
        """CRUD layer must not depend on the privacy proxy."""
        violations = _module_directly_imports(
            APP_DIR / "services" / "crud.py", "app.services.privacy_proxy"
        )
        assert violations == [], f"crud.py directly imports privacy_proxy: {violations}"

    def test_llm_providers_only_import_base_client(self):
        """LLM provider adapters must only import from llm_client base, not other services."""
        for provider_file in ["llm_claude.py", "llm_gemini.py", "llm_ollama.py"]:
            path = APP_DIR / "services" / provider_file
            if not path.exists():
                continue
            imports = _get_direct_imports(path)
            service_imports = [
                i
                for i in imports
                if i.startswith("app.services.") and i != "app.services.llm_client"
            ]
            assert service_imports == [], (
                f"{provider_file} imports non-base services: {service_imports}"
            )
