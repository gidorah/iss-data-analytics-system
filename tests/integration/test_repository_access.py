"""Integration tests for repository access controls and permissions.

This module validates that the GitHub repository is properly configured with
appropriate access controls, branch protection rules, and security settings.
"""

import os
import subprocess
import pytest
import json


class TestRepositoryAccess:
    """Test repository access controls and security configurations."""

    REPO_NAME = os.getenv("GITHUB_REPOSITORY", "gidorah/iss-data-analytics-system")

    def test_repository_exists_and_accessible(self):
        """Test that the repository exists and is accessible."""
        result = subprocess.run(
            ["gh", "repo", "view", self.REPO_NAME, "--json", "name,owner"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Repository {self.REPO_NAME} is not accessible"

        repo_data = json.loads(result.stdout)
        assert repo_data["name"] == "iss-data-analytics-system"
        assert repo_data["owner"]["login"] == "gidorah"

    def test_repository_visibility_settings(self):
        """Test repository visibility and basic settings."""
        result = subprocess.run(
            ["gh", "repo", "view", self.REPO_NAME, "--json", "visibility,isPrivate"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        repo_data = json.loads(result.stdout)
        # Repository is configured as public per user preference (single-user repository)
        assert repo_data["visibility"] == "PUBLIC"
        assert repo_data["isPrivate"] is False

    def test_default_branch_configuration(self):
        """Test that main branch is set as default."""
        result = subprocess.run(
            ["gh", "repo", "view", self.REPO_NAME, "--json", "defaultBranchRef"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        repo_data = json.loads(result.stdout)
        assert repo_data["defaultBranchRef"]["name"] == "main"

    def test_repository_features_enabled(self):
        """Test that appropriate repository features are enabled."""
        result = subprocess.run(
            [
                "gh",
                "repo",
                "view",
                self.REPO_NAME,
                "--json",
                "hasIssuesEnabled,hasWikiEnabled,hasProjectsEnabled",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        repo_data = json.loads(result.stdout)
        assert repo_data["hasIssuesEnabled"] is True
        assert repo_data["hasWikiEnabled"] is True
        assert repo_data["hasProjectsEnabled"] is True

    def test_repository_has_description(self):
        """Test that repository has proper description."""
        result = subprocess.run(
            ["gh", "repo", "view", self.REPO_NAME, "--json", "description"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        repo_data = json.loads(result.stdout)
        description = repo_data["description"]
        assert description is not None
        assert len(description) > 0
        assert "ISS Telemetry Data Analytics System" in description

    def test_branch_deletion_on_merge_enabled(self):
        """Test that branch deletion on merge is enabled."""
        result = subprocess.run(
            ["gh", "repo", "view", self.REPO_NAME, "--json", "deleteBranchOnMerge"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        repo_data = json.loads(result.stdout)
        assert repo_data["deleteBranchOnMerge"] is True

    @pytest.mark.skipif(
        not os.getenv("GITHUB_TOKEN"), reason="Requires authenticated GitHub access"
    )
    def test_authenticated_access_works(self):
        """Test that authenticated access to the repository works."""
        result = subprocess.run(
            ["gh", "auth", "status"], capture_output=True, text=True
        )
        assert result.returncode == 0
        assert "Logged in to github.com" in result.stderr

    def test_repository_structure_exists(self):
        """Test that basic repository structure files exist."""
        # This test verifies that the local repository structure matches expectations
        required_files = [
            "README.md",
            "LICENSE",
            "CONTRIBUTING.md",
            "pyproject.toml",
            "services/ingestion/pyproject.toml",
            "libs/common/pyproject.toml",
        ]

        repo_root = (
            subprocess.check_output(["git", "rev-parse", "--show-toplevel"])
            .strip()
            .decode("utf-8")
        )

        for file_path in required_files:
            full_path = os.path.join(repo_root, file_path)
            assert os.path.exists(full_path), (
                f"Required file {file_path} does not exist"
            )

    def test_no_sensitive_data_in_repository(self):
        """Test that no obvious sensitive data patterns exist in repository."""
        # Check for common sensitive patterns in key files
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

        sensitive_patterns = ["password", "secret", "token", "api_key", "private_key"]

        check_files = ["README.md", "pyproject.toml"]

        for file_name in check_files:
            file_path = os.path.join(repo_root, file_name)
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().lower()
                    for pattern in sensitive_patterns:
                        # Allow documentation references but not actual values
                        if pattern in content:
                            lines = content.split("\n")
                            for i, line in enumerate(lines):
                                if pattern in line and "=" in line:
                                    pytest.fail(
                                        f"Potential sensitive data in {file_name}:{i + 1}: {line.strip()}"
                                    )


class TestRepositoryAccessViolations:
    """Test scenarios that should be blocked by access controls."""

    REPO_NAME = "gidorah/iss-data-analytics-system"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
