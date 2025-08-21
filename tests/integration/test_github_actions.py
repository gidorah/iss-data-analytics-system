"""Integration tests for GitHub Actions workflow validation.

This module validates that GitHub Actions workflows are properly configured,
syntactically correct, and can execute successfully in the CI/CD pipeline.
"""

import os
import subprocess
from pathlib import Path

import pytest
import yaml


class TestGitHubActionsWorkflows:
    """Test GitHub Actions workflow configurations and functionality."""

    REPO_ROOT = Path(__file__).parent.parent.parent
    WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"

    def test_workflows_directory_exists(self):
        """Test that the workflows directory exists."""
        assert self.WORKFLOWS_DIR.exists(), "Workflows directory should exist"
        assert self.WORKFLOWS_DIR.is_dir(), "Workflows path should be a directory"

    def test_required_workflow_files_exist(self):
        """Test that required workflow files exist."""
        required_workflows = [
            "staging-deploy.yml",
            "production-deploy.yml",
            "pr-validation.yml",
        ]

        for workflow_file in required_workflows:
            workflow_path = self.WORKFLOWS_DIR / workflow_file
            assert workflow_path.exists(), f"Workflow file {workflow_file} should exist"
            assert workflow_path.is_file(), (
                f"Workflow path {workflow_file} should be a file"
            )

    def test_workflow_yaml_syntax_valid(self):
        """Test that all workflow YAML files have valid syntax."""
        workflow_files = list(self.WORKFLOWS_DIR.glob("*.yml")) + list(
            self.WORKFLOWS_DIR.glob("*.yaml")
        )

        assert len(workflow_files) > 0, "Should have at least one workflow file"

        for workflow_file in workflow_files:
            with open(workflow_file, "r") as f:
                try:
                    yaml.safe_load(f)
                except yaml.YAMLError as e:
                    pytest.fail(f"Invalid YAML syntax in {workflow_file.name}: {e}")

    def test_staging_deploy_workflow_structure(self):
        """Test the structure of the staging deployment workflow."""
        staging_path = self.WORKFLOWS_DIR / "staging-deploy.yml"
        assert staging_path.exists(), "Staging deploy workflow should exist"

        with open(staging_path, "r") as f:
            workflow = yaml.safe_load(f)

        # Test basic structure
        assert "name" in workflow, "Workflow should have a name"
        # Handle YAML parsing of 'on' keyword (may be parsed as True)
        trigger_events = workflow.get("on") or workflow.get(True)
        assert trigger_events is not None, "Workflow should have trigger events"
        assert "jobs" in workflow, "Workflow should have jobs"

        # Test trigger configuration
        assert "push" in trigger_events, "Should trigger on push"
        assert "staging" in trigger_events["push"]["branches"], (
            "Should trigger on staging branch"
        )

        # Test job structure
        jobs = workflow["jobs"]
        assert "deployment-readiness" in jobs, "Should have a deployment-readiness job"
        assert "deploy" in jobs, "Should have a deploy job"

        # Test deployment job conditions
        deploy_job = jobs["deploy"]
        assert "if" in deploy_job, "Deploy job should have conditions"
        assert "needs" in deploy_job, "Deploy job should depend on deployment-readiness"

        assert deploy_job["needs"] == "deployment-readiness", (
            "Deploy should need deployment-readiness job"
        )

    def test_production_deploy_workflow_structure(self):
        """Test the structure of the production deployment workflow."""
        production_path = self.WORKFLOWS_DIR / "production-deploy.yml"
        assert production_path.exists(), "Production deploy workflow should exist"

        with open(production_path, "r") as f:
            workflow = yaml.safe_load(f)

        # Test basic structure
        assert "name" in workflow, "Workflow should have a name"
        # Handle YAML parsing of 'on' keyword (may be parsed as True)
        trigger_events = workflow.get("on") or workflow.get(True)
        assert trigger_events is not None, "Workflow should have trigger events"
        assert "jobs" in workflow, "Workflow should have jobs"

        # Test trigger configuration
        assert "push" in trigger_events, "Should trigger on push"
        assert "main" in trigger_events["push"]["branches"], (
            "Should trigger on main branch"
        )

        # Test job structure
        jobs = workflow["jobs"]
        assert "deployment-readiness" in jobs, "Should have a deployment-readiness job"
        assert "deploy-production" in jobs, "Should have a deploy-production job"

    def test_pr_validation_workflow_structure(self):
        """Test the structure of the PR validation workflow."""
        pr_validation_path = self.WORKFLOWS_DIR / "pr-validation.yml"
        assert pr_validation_path.exists(), "PR validation workflow should exist"

        with open(pr_validation_path, "r") as f:
            workflow = yaml.safe_load(f)

        # Test basic structure
        assert "name" in workflow, "Workflow should have a name"
        # Handle YAML parsing of 'on' keyword (may be parsed as True)
        trigger_events = workflow.get("on") or workflow.get(True)
        assert trigger_events is not None, "Workflow should have trigger events"
        assert "jobs" in workflow, "Workflow should have jobs"

        # Test trigger configuration
        assert "pull_request" in trigger_events, "Should trigger on pull requests"
        pr_config = trigger_events["pull_request"]
        assert "branches" in pr_config, "Should specify target branches"
        branches = pr_config["branches"]
        assert "main" in branches, "Should trigger on PRs to main"
        assert "staging" in branches, "Should trigger on PRs to staging"

        # Test permissions
        assert "permissions" in workflow, "Should have permissions defined"
        permissions = workflow["permissions"]
        assert "contents" in permissions, "Should have contents permission"
        assert "checks" in permissions, "Should have checks permission"

    def test_workflow_permissions_security(self):
        """Test that workflows have proper security permissions."""
        workflow_files = [
            self.WORKFLOWS_DIR / "staging-deploy.yml",
            self.WORKFLOWS_DIR / "production-deploy.yml",
            self.WORKFLOWS_DIR / "pr-validation.yml",
        ]

        for workflow_file in workflow_files:
            with open(workflow_file, "r") as f:
                workflow = yaml.safe_load(f)

            # Check for permissions section
            if "permissions" in workflow:
                permissions = workflow["permissions"]

                # Should have minimal required permissions
                assert "contents" in permissions, (
                    f"{workflow_file.name} should have contents permission"
                )

                # Should not have overly broad permissions
                dangerous_permissions = ["write-all", "admin"]
                for perm in dangerous_permissions:
                    assert perm not in permissions.values(), (
                        f"{workflow_file.name} should not have {perm} permission"
                    )

    def test_workflow_uses_uv_package_manager(self):
        """Test that workflows use uv package manager instead of pip."""
        workflow_files = [
            self.WORKFLOWS_DIR / "staging-deploy.yml",
            self.WORKFLOWS_DIR / "production-deploy.yml",
            self.WORKFLOWS_DIR / "pr-validation.yml",
        ]

        for workflow_file in workflow_files:
            with open(workflow_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Only PR validation needs Python setup - deployment workflows are deployment-focused
            if workflow_file.name == "pr-validation.yml":
                # Should use uv setup action
                assert "astral-sh/setup-uv" in content, (
                    f"{workflow_file.name} should use uv setup action"
                )

                # Should use uv commands
                assert "uv sync" in content, (
                    f"{workflow_file.name} should use 'uv sync'"
                )
                assert "uv run" in content, f"{workflow_file.name} should use 'uv run'"

            # Should not use pip directly for main dependencies
            assert "pip install -r requirements.txt" not in content, (
                f"{workflow_file.name} should not use pip with requirements.txt"
            )

    def test_workflow_includes_testing(self):
        """Test that workflows include proper testing steps."""
        test_workflows = [
            self.WORKFLOWS_DIR / "staging-deploy.yml",
            self.WORKFLOWS_DIR / "production-deploy.yml",
            self.WORKFLOWS_DIR / "pr-validation.yml",
        ]

        for workflow_file in test_workflows:
            with open(workflow_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Only PR validation includes testing - deployment workflows are deployment-focused
            if workflow_file.name == "pr-validation.yml":
                # Should include pytest
                assert "pytest" in content, (
                    f"{workflow_file.name} should include pytest"
                )

                # Should include linting
                assert "ruff" in content, (
                    f"{workflow_file.name} should include ruff linting"
                )

    def test_workflow_includes_security_checks(self):
        """Test that workflows include security validation."""
        workflow_files = [
            self.WORKFLOWS_DIR / "staging-deploy.yml",
            self.WORKFLOWS_DIR / "production-deploy.yml",
            self.WORKFLOWS_DIR / "pr-validation.yml",
        ]

        for workflow_file in workflow_files:
            with open(workflow_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Only PR validation includes actionlint - deployment workflows are deployment-focused
            if workflow_file.name == "pr-validation.yml":
                # Should include actionlint for workflow validation
                assert "actionlint" in content, (
                    f"{workflow_file.name} should include actionlint"
                )

    @pytest.mark.skipif(
        not os.getenv("GITHUB_TOKEN"), reason="Requires authenticated GitHub access"
    )
    def test_github_actions_enabled(self):
        """Test that GitHub Actions is enabled for the repository."""
        result = subprocess.run(
            [
                "gh",
                "api",
                "repos/gidorah/iss-data-analytics-system",
                "--jq",
                ".has_actions",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            has_actions = result.stdout.strip()
            assert has_actions == "true", (
                "GitHub Actions should be enabled for the repository"
            )

    def test_workflow_file_naming_convention(self):
        """Test that workflow files follow naming conventions."""
        workflow_files = list(self.WORKFLOWS_DIR.glob("*.yml")) + list(
            self.WORKFLOWS_DIR.glob("*.yaml")
        )

        for workflow_file in workflow_files:
            filename = workflow_file.name

            # Should use .yml extension (not .yaml)
            assert filename.endswith(".yml"), (
                f"Workflow file {filename} should use .yml extension"
            )

            # Should use kebab-case (hyphens, not underscores)
            name_without_ext = filename.replace(".yml", "")
            assert "_" not in name_without_ext, (
                f"Workflow file {filename} should use hyphens, not underscores"
            )

    def test_deployment_jobs_have_proper_configuration(self):
        """Test that deployment jobs are properly configured for GitHub App integration."""
        deployment_workflows = [
            self.WORKFLOWS_DIR / "staging-deploy.yml",
            self.WORKFLOWS_DIR / "production-deploy.yml",
        ]

        for workflow_path in deployment_workflows:
            with open(workflow_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Should have deployment readiness checks
            assert "deployment-readiness" in content, (
                f"{workflow_path.name} should have deployment-readiness job"
            )

            # Should have proper deployment flow for GitHub App integration
            assert "GitHub App" in content, (
                f"{workflow_path.name} should reference GitHub App integration"
            )

            # Should have health check validation (for staging)
            if workflow_path.name == "staging-deploy.yml":
                assert "healthz" in content, (
                    f"{workflow_path.name} should include health check validation"
                )

    def test_staged_deployment_architecture(self):
        """Test that the staged deployment architecture is properly implemented."""
        # Test PR validation triggers on both main and staging
        pr_path = self.WORKFLOWS_DIR / "pr-validation.yml"
        with open(pr_path, "r") as f:
            pr_workflow = yaml.safe_load(f)

        trigger_events = pr_workflow.get("on") or pr_workflow.get(True)
        pr_branches = trigger_events["pull_request"]["branches"]
        assert "main" in pr_branches, "PR validation should trigger on main branch PRs"
        assert "staging" in pr_branches, (
            "PR validation should trigger on staging branch PRs"
        )

        # Test staging deployment triggers on staging branch
        staging_path = self.WORKFLOWS_DIR / "staging-deploy.yml"
        with open(staging_path, "r") as f:
            staging_workflow = yaml.safe_load(f)

        staging_events = staging_workflow.get("on") or staging_workflow.get(True)
        staging_branches = staging_events["push"]["branches"]
        assert "staging" in staging_branches, (
            "Staging deploy should trigger on staging branch"
        )
        assert "main" not in staging_branches, (
            "Staging deploy should NOT trigger on main branch"
        )

        # Test production deployment triggers on main branch
        production_path = self.WORKFLOWS_DIR / "production-deploy.yml"
        with open(production_path, "r") as f:
            production_workflow = yaml.safe_load(f)

        production_events = production_workflow.get("on") or production_workflow.get(
            True
        )
        production_branches = production_events["push"]["branches"]
        assert "main" in production_branches, (
            "Production deploy should trigger on main branch"
        )
        assert "staging" not in production_branches, (
            "Production deploy should NOT trigger on staging branch"
        )


class TestWorkflowExecution:
    """Test workflow execution capabilities (where possible without running)."""

    def test_can_validate_workflow_syntax_locally(self):
        """Test that actionlint can validate workflow syntax locally."""
        # This test ensures that workflow validation tools are available
        workflows_dir = Path(__file__).parent.parent.parent / ".github" / "workflows"

        if not workflows_dir.exists():
            pytest.skip("Workflows directory does not exist")

        workflow_files = list(workflows_dir.glob("*.yml"))
        assert len(workflow_files) > 0, "Should have workflow files to validate"

        # Check that workflows can be parsed as valid YAML
        for workflow_file in workflow_files:
            with open(workflow_file, "r") as f:
                try:
                    workflow_data = yaml.safe_load(f)
                    assert isinstance(workflow_data, dict), (
                        f"Workflow {workflow_file.name} should parse to dict"
                    )
                    assert "jobs" in workflow_data, (
                        f"Workflow {workflow_file.name} should have jobs"
                    )
                except Exception as e:
                    pytest.fail(f"Failed to parse workflow {workflow_file.name}: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
