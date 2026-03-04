"""Tests for VPMA Folder Browser endpoint.

Tests cover: security constraints (path traversal, symlinks, hidden dirs),
happy path navigation, edge cases.
"""

from unittest.mock import patch

import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


@pytest.fixture
def mock_home(tmp_path):
    """Create a mock home directory with test structure."""
    # Create directory structure
    (tmp_path / "Documents").mkdir()
    (tmp_path / "Projects").mkdir()
    (tmp_path / "Projects" / "MyProject").mkdir()
    (tmp_path / "Downloads").mkdir()
    (tmp_path / ".hidden_dir").mkdir()
    (tmp_path / ".config").mkdir()

    # Create a regular file (should not be listed)
    (tmp_path / "README.txt").write_text("test")

    # Create a symlink (should not be listed)
    (tmp_path / "link_dir").symlink_to(tmp_path / "Documents")

    return tmp_path


class TestBrowseFolders:
    def test_returns_home_directory_by_default(self, mock_home):
        with patch("pathlib.Path.home", return_value=mock_home):
            response = client.get("/api/settings/browse-folders")

        assert response.status_code == 200
        data = response.json()
        assert data["current_path"] == str(mock_home)
        assert data["parent_path"] is None  # Can't go above home

    def test_lists_only_directories(self, mock_home):
        with patch("pathlib.Path.home", return_value=mock_home):
            response = client.get("/api/settings/browse-folders")

        data = response.json()
        names = [d["name"] for d in data["directories"]]
        # Should include visible directories
        assert "Documents" in names
        assert "Projects" in names
        assert "Downloads" in names
        # Should NOT include files
        assert "README.txt" not in names

    def test_skips_hidden_directories(self, mock_home):
        with patch("pathlib.Path.home", return_value=mock_home):
            response = client.get("/api/settings/browse-folders")

        data = response.json()
        names = [d["name"] for d in data["directories"]]
        assert ".hidden_dir" not in names
        assert ".config" not in names

    def test_skips_symlinks(self, mock_home):
        with patch("pathlib.Path.home", return_value=mock_home):
            response = client.get("/api/settings/browse-folders")

        data = response.json()
        names = [d["name"] for d in data["directories"]]
        assert "link_dir" not in names

    def test_navigates_into_subdirectory(self, mock_home):
        with patch("pathlib.Path.home", return_value=mock_home):
            response = client.get(
                "/api/settings/browse-folders",
                params={"path": str(mock_home / "Projects")},
            )

        data = response.json()
        assert data["current_path"] == str(mock_home / "Projects")
        assert data["parent_path"] == str(mock_home)
        names = [d["name"] for d in data["directories"]]
        assert "MyProject" in names

    def test_rejects_path_outside_home(self, mock_home):
        with patch("pathlib.Path.home", return_value=mock_home):
            response = client.get(
                "/api/settings/browse-folders",
                params={"path": "/etc"},
            )

        assert response.status_code == 403
        assert "outside home" in response.json()["detail"].lower()

    def test_rejects_path_traversal(self, mock_home):
        with patch("pathlib.Path.home", return_value=mock_home):
            response = client.get(
                "/api/settings/browse-folders",
                params={"path": str(mock_home / ".." / "..")},
            )

        assert response.status_code == 403

    def test_returns_404_for_nonexistent_directory(self, mock_home):
        with patch("pathlib.Path.home", return_value=mock_home):
            response = client.get(
                "/api/settings/browse-folders",
                params={"path": str(mock_home / "nonexistent")},
            )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_directories_sorted_alphabetically(self, mock_home):
        with patch("pathlib.Path.home", return_value=mock_home):
            response = client.get("/api/settings/browse-folders")

        data = response.json()
        names = [d["name"] for d in data["directories"]]
        assert names == sorted(names)

    def test_parent_path_none_at_home(self, mock_home):
        with patch("pathlib.Path.home", return_value=mock_home):
            response = client.get("/api/settings/browse-folders")

        data = response.json()
        assert data["parent_path"] is None

    def test_parent_path_set_in_subdirectory(self, mock_home):
        with patch("pathlib.Path.home", return_value=mock_home):
            response = client.get(
                "/api/settings/browse-folders",
                params={"path": str(mock_home / "Projects" / "MyProject")},
            )

        data = response.json()
        assert data["parent_path"] == str(mock_home / "Projects")

    def test_empty_directory(self, mock_home):
        (mock_home / "EmptyDir").mkdir()
        with patch("pathlib.Path.home", return_value=mock_home):
            response = client.get(
                "/api/settings/browse-folders",
                params={"path": str(mock_home / "EmptyDir")},
            )

        data = response.json()
        assert data["directories"] == []
