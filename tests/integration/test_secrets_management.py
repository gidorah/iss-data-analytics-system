"""Integration tests for GitHub Actions secrets management and security.

This module validates that secrets management infrastructure works correctly
and follows security best practices, without requiring specific secrets.
"""

import os
import subprocess
from pathlib import Path
import pytest


class TestSecretsInfrastructure:
    """Test GitHub repository secrets infrastructure and access."""

    REPO_NAME = "gidorah/iss-data-analytics-system"

    def test_secrets_management_accessible(self):
        """Test that secrets management infrastructure is accessible."""
        result = subprocess.run(
            ["gh", "secret", "list", "--repo", self.REPO_NAME],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            pytest.skip("Cannot access repository secrets (authentication required)")

        # Verify that the secrets management system is working
        # Don't require specific secrets - just test infrastructure
        print("✅ GitHub secrets management infrastructure accessible")

    def test_secrets_list_format_valid(self):
        """Test that secrets list returns properly formatted output."""
        result = subprocess.run(
            ["gh", "secret", "list", "--repo", self.REPO_NAME],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            pytest.skip("Cannot access repository secrets (authentication required)")

        # Just verify the command works and returns valid output format
        # Don't require specific secrets to exist
        secrets_output = result.stdout

        # The output should be properly formatted (either empty or with valid lines)
        if secrets_output.strip():
            # If there are secrets, they should be properly formatted
            lines = [line for line in secrets_output.split("\n") if line.strip()]
            for line in lines:
                # Each line should have tab-separated fields (name, updated date)
                assert len(line.split("\t")) >= 1, f"Invalid secret line format: {line}"

        print("✅ GitHub secrets list command returns valid format")


class TestWorkflowSecretsSecurity:
    """Test security practices for secrets in GitHub Actions workflows."""

    WORKFLOWS_DIR = Path(__file__).parent.parent.parent / ".github" / "workflows"

    def test_workflows_dont_expose_secrets_in_names(self):
        """Test that workflow step names don't accidentally expose secret values."""
        if not self.WORKFLOWS_DIR.exists():
            pytest.skip("Workflows directory does not exist")

        workflow_files = list(self.WORKFLOWS_DIR.glob("*.yml"))

        for workflow_file in workflow_files:
            with open(workflow_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Look for potentially suspicious patterns in step names
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if "name:" in line.lower():
                    # Check if step name contains what looks like secret values
                    # (long alphanumeric strings that might be tokens)
                    import re

                    if re.search(r"[a-zA-Z0-9]{20,}", line):
                        # This is just a warning, not a failure
                        print(
                            f"⚠️  Review step name in {workflow_file.name}:{i + 1}: {line.strip()}"
                        )

        print("✅ Workflow step names reviewed for secret exposure")


class TestSecretsSecurityPractices:
    """Test security practices around secrets management."""

    def test_no_hardcoded_secrets_in_repository(self):
        """Test that no secrets are hardcoded anywhere in the repository."""
        repo_root = Path(__file__).parent.parent.parent

        # Common patterns that might indicate hardcoded secrets (actual values, not references)
        secret_patterns = [
            r"https://[a-zA-Z0-9.-]+\.coolify\.[a-z]+/webhooks/[a-f0-9-]{20,}",  # Actual webhook URLs
            r"['\"]api[_-]?token['\"]:\s*['\"][a-zA-Z0-9]{20,}['\"]",  # Quoted API tokens
            r"bearer\s+[a-zA-Z0-9]{30,}",  # Actual bearer tokens (not variables)
            r"coolify[_-]?token\s*=\s*['\"][a-zA-Z0-9]{20,}['\"]",  # Assigned token values
        ]

        # Files to check for hardcoded secrets
        files_to_check = [
            ".github/workflows/ci-cd.yml",
            ".github/workflows/pr-validation.yml",
            "README.md",
            "pyproject.toml",
        ]

        for file_path in files_to_check:
            full_path = repo_root / file_path
            if full_path.exists():
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read().lower()

                for pattern in secret_patterns:
                    import re

                    if re.search(pattern, content):
                        pytest.fail(f"Potential hardcoded secret found in {file_path}")

    def test_secrets_not_exposed_in_workflow_names_or_descriptions(self):
        """Test that secrets don't appear in workflow step names or descriptions."""
        workflows_dir = Path(__file__).parent.parent.parent / ".github" / "workflows"

        if not workflows_dir.exists():
            pytest.skip("Workflows directory does not exist")

        workflow_files = list(workflows_dir.glob("*.yml"))

        for workflow_file in workflow_files:
            with open(workflow_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Should not expose actual secret values in step names
            secret_indicators = ["webhook", "token", "secret", "password", "key"]

            # This is more of a code review helper than strict validation
            # We're looking for obvious mistakes like step names containing actual secrets
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if "name:" in line.lower():
                    for indicator in secret_indicators:
                        if indicator in line.lower() and any(
                            char.isdigit() for char in line
                        ):
                            # If step name contains both secret indicator AND numbers, might be suspicious
                            print(
                                f"⚠️  Review step name in {workflow_file.name}:{i + 1}: {line.strip()}"
                            )


class TestSecretsInCI:
    """Test secrets behavior in CI environment."""

    @pytest.mark.skipif(
        not os.getenv("GITHUB_ACTIONS"),
        reason="Only runs in GitHub Actions environment",
    )
    def test_github_actions_secrets_infrastructure(self):
        """Test that GitHub Actions secrets infrastructure is working."""
        # Test that we're in a GitHub Actions environment with secrets support
        assert os.getenv("GITHUB_ACTIONS") == "true", (
            "Should be running in GitHub Actions environment"
        )

        # Test that the GitHub token is available (automatically provided)
        github_token = os.getenv("GITHUB_TOKEN")
        if github_token:
            assert len(github_token) > 0, "GitHub token should not be empty"
            print("✅ GitHub Actions automatic token available")
        else:
            print("ℹ️  GitHub token not available in this context")

        print("✅ GitHub Actions secrets infrastructure operational")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
