"""Tests for post_gen.py helper functions.

These tests verify:
- is_copier_temp_directory() correctly identifies copier's temp directories
- resolve_pyproject_conflicts() properly handles conflict markers, preserving custom license
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add scripts directory to path for importing post_gen
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from post_gen import is_copier_temp_directory, resolve_pyproject_conflicts


class TestIsCopierTempDirectory:
    """Tests for is_copier_temp_directory() function."""

    @pytest.mark.parametrize(
        "cwd,expected",
        [
            # Copier temp directories (should be detected)
            ("/tmp/copier._main.new_copy.5c_dx15j", True),  # copier update diff
            ("/tmp/copier._main.new_copy.5c_dx15j/project", True),  # subdir of temp
            ("/tmp/copier._vcs.clone.fvvn1ivq", True),  # copier clone
            ("/tmp/copier._vcs.clone.fvvn1ivq/repo/subdir", True),  # nested in clone
            # macOS copier temp directories (should be detected)
            ("/var/folders/ab/cd123/T/copier._main.new_copy.xyz12345", True),
            # Windows copier temp directories (should be detected)
            ("C:\\Users\\test\\AppData\\Local\\Temp\\copier._main.new_copy.xyz12345", True),
            # Python tempfile directories (should NOT be detected - not copier)
            ("/tmp/tmpabcd1234/my_project", False),
            ("/tmp/tmp_xyz7890/subdir", False),
            # Test directories with suffixes (should NOT be detected)
            ("/tmp/tmp0_odqejbdata-project/docker_test_project", False),
            # Actual project directories (should NOT be detected)
            ("/home/user/projects/my_project", False),
            ("/home/user/workspace/data-science", False),
            # User's intentional /tmp usage (should NOT be detected)
            ("/tmp/my_custom_dir/project", False),
            ("/tmp/test_project", False),
            ("/home/user/tmp/project", False),
            # Edge cases
            ("/", False),
            ("/home", False),
            (".", False),
        ],
    )
    def test_temp_directory_detection(self, cwd, expected):
        """Test that temp directory patterns are correctly detected."""
        with patch("os.getcwd", return_value=cwd):
            assert is_copier_temp_directory() == expected


class TestResolvePyprojectConflicts:
    """Tests for resolve_pyproject_conflicts() function."""

    def test_no_conflicts_unchanged(self, tmp_path):
        """Test that file without conflicts is unchanged."""
        pyproject = tmp_path / "pyproject.toml"
        original_content = """\
[project]
name = "my-project"
version = "0.1.0"
license = "MIT"
"""
        pyproject.write_text(original_content)

        with patch("os.getcwd", return_value=str(tmp_path)):
            # Need to also patch Path to work in the function's context
            original_path = Path
            with patch("post_gen.Path", side_effect=lambda x: tmp_path / x if x == "pyproject.toml" else original_path(x)):
                resolve_pyproject_conflicts()

        assert pyproject.read_text() == original_content

    def test_license_conflict_keeps_user_version(self, tmp_path):
        """Test that license conflicts preserve user's custom license."""
        pyproject = tmp_path / "pyproject.toml"
        content_with_conflict = """\
[project]
name = "my-project"
version = "0.1.0"
<<<<<<< before updating
[project.license]
text = "Proprietary - Kolomolo LTD"
=======
license = "MIT"
>>>>>>> after updating
"""
        expected = """\
[project]
name = "my-project"
version = "0.1.0"
[project.license]
text = "Proprietary - Kolomolo LTD"
"""
        pyproject.write_text(content_with_conflict)

        with patch("os.getcwd", return_value=str(tmp_path)):
            original_path = Path
            with patch("post_gen.Path", side_effect=lambda x: tmp_path / x if x == "pyproject.toml" else original_path(x)):
                resolve_pyproject_conflicts()

        assert pyproject.read_text() == expected

    def test_version_conflict_keeps_user_version(self, tmp_path):
        """Test that version conflicts preserve user's bumped version."""
        pyproject = tmp_path / "pyproject.toml"
        content_with_conflict = """\
[project]
name = "my-project"
<<<<<<< before updating
version = "1.2.6"
=======
version = "0.1.0"
>>>>>>> after updating
"""
        expected = """\
[project]
name = "my-project"
version = "1.2.6"
"""
        pyproject.write_text(content_with_conflict)

        with patch("os.getcwd", return_value=str(tmp_path)):
            original_path = Path
            with patch("post_gen.Path", side_effect=lambda x: tmp_path / x if x == "pyproject.toml" else original_path(x)):
                resolve_pyproject_conflicts()

        assert pyproject.read_text() == expected

    def test_multiple_conflicts_mixed_resolution(self, tmp_path):
        """Test multiple conflicts with mixed resolution (license and version kept, others updated)."""
        pyproject = tmp_path / "pyproject.toml"
        content_with_conflicts = """\
[project]
name = "my-project"
<<<<<<< before updating
version = "1.2.6"
=======
version = "0.1.0"
>>>>>>> after updating
<<<<<<< before updating
[project.license]
text = "Proprietary - Custom License"
=======
license = "MIT"
>>>>>>> after updating
<<<<<<< before updating
description = "Old description"
=======
description = "New description"
>>>>>>> after updating
"""
        expected = """\
[project]
name = "my-project"
version = "1.2.6"
[project.license]
text = "Proprietary - Custom License"
description = "New description"
"""
        pyproject.write_text(content_with_conflicts)

        with patch("os.getcwd", return_value=str(tmp_path)):
            original_path = Path
            with patch("post_gen.Path", side_effect=lambda x: tmp_path / x if x == "pyproject.toml" else original_path(x)):
                resolve_pyproject_conflicts()

        assert pyproject.read_text() == expected

    def test_no_pyproject_file(self, tmp_path):
        """Test that missing pyproject.toml doesn't cause errors."""
        with patch("os.getcwd", return_value=str(tmp_path)):
            original_path = Path
            with patch("post_gen.Path", side_effect=lambda x: tmp_path / x if x == "pyproject.toml" else original_path(x)):
                # Should not raise any exception
                resolve_pyproject_conflicts()

    def test_license_keyword_in_before_section(self, tmp_path):
        """Test that 'license' keyword anywhere in before section triggers preservation."""
        pyproject = tmp_path / "pyproject.toml"
        content_with_conflict = """\
[project]
<<<<<<< before updating
license = { file = "LICENSE.txt" }
=======
license = "Apache-2.0"
>>>>>>> after updating
"""
        expected = """\
[project]
license = { file = "LICENSE.txt" }
"""
        pyproject.write_text(content_with_conflict)

        with patch("os.getcwd", return_value=str(tmp_path)):
            original_path = Path
            with patch("post_gen.Path", side_effect=lambda x: tmp_path / x if x == "pyproject.toml" else original_path(x)):
                resolve_pyproject_conflicts()

        assert pyproject.read_text() == expected

    def test_multiline_dev_dependencies_conflict(self, tmp_path):
        """Test that multi-line dev dependencies conflict is resolved to template version."""
        pyproject = tmp_path / "pyproject.toml"
        content_with_conflict = """\
[project]
name = "my-project"

[project.optional-dependencies]
<<<<<<< before updating
dev = [ "build", "ipykernel", "ipython", "nbdime", "pip", "pytest", "pytest-cov", "toml", "ruff",]
=======
dev = [
    "build",
    "ipykernel",
    "ipython",
    "nbdime",
    "pip",
    "pytest",
    "pytest-cov",
    "toml",
    "ruff",
    "twine",
]
>>>>>>> after updating
"""
        expected = """\
[project]
name = "my-project"

[project.optional-dependencies]
dev = [
    "build",
    "ipykernel",
    "ipython",
    "nbdime",
    "pip",
    "pytest",
    "pytest-cov",
    "toml",
    "ruff",
    "twine",
]
"""
        pyproject.write_text(content_with_conflict)

        with patch("os.getcwd", return_value=str(tmp_path)):
            original_path = Path
            with patch("post_gen.Path", side_effect=lambda x: tmp_path / x if x == "pyproject.toml" else original_path(x)):
                resolve_pyproject_conflicts()

        assert pyproject.read_text() == expected
