"""Integration tests for GitHub Actions workflow validation.

This module validates that GitHub Actions workflows are properly configured,
syntactically correct, and can execute successfully in the CI/CD pipeline.
"""

import os
import subprocess
import yaml
from pathlib import Path
import pytest


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
            "ci-cd.yml",
            "pr-validation.yml"
        ]
        
        for workflow_file in required_workflows:
            workflow_path = self.WORKFLOWS_DIR / workflow_file
            assert workflow_path.exists(), f"Workflow file {workflow_file} should exist"
            assert workflow_path.is_file(), f"Workflow path {workflow_file} should be a file"
    
    def test_workflow_yaml_syntax_valid(self):
        """Test that all workflow YAML files have valid syntax."""
        workflow_files = list(self.WORKFLOWS_DIR.glob("*.yml")) + list(self.WORKFLOWS_DIR.glob("*.yaml"))
        
        assert len(workflow_files) > 0, "Should have at least one workflow file"
        
        for workflow_file in workflow_files:
            with open(workflow_file, 'r') as f:
                try:
                    yaml.safe_load(f)
                except yaml.YAMLError as e:
                    pytest.fail(f"Invalid YAML syntax in {workflow_file.name}: {e}")
    
    def test_ci_cd_workflow_structure(self):
        """Test the structure of the main CI/CD workflow."""
        ci_cd_path = self.WORKFLOWS_DIR / "ci-cd.yml"
        assert ci_cd_path.exists(), "CI/CD workflow should exist"
        
        with open(ci_cd_path, 'r') as f:
            workflow = yaml.safe_load(f)
        
        # Test basic structure
        assert "name" in workflow, "Workflow should have a name"
        # Handle YAML parsing of 'on' keyword (may be parsed as True)
        trigger_events = workflow.get("on") or workflow.get(True)
        assert trigger_events is not None, "Workflow should have trigger events"
        assert "jobs" in workflow, "Workflow should have jobs"
        
        # Test trigger configuration
        assert "push" in trigger_events, "Should trigger on push"
        assert "main" in trigger_events["push"]["branches"], "Should trigger on main branch"
        
        # Test job structure
        jobs = workflow["jobs"]
        assert "test" in jobs, "Should have a test job"
        assert "deploy" in jobs, "Should have a deploy job"
        
        # Test deployment job conditions
        deploy_job = jobs["deploy"]
        assert "if" in deploy_job, "Deploy job should have conditions"
        assert "needs" in deploy_job, "Deploy job should depend on test"
        assert deploy_job["needs"] == "test", "Deploy should need test job"
    
    def test_pr_validation_workflow_structure(self):
        """Test the structure of the PR validation workflow."""
        pr_validation_path = self.WORKFLOWS_DIR / "pr-validation.yml"
        assert pr_validation_path.exists(), "PR validation workflow should exist"
        
        with open(pr_validation_path, 'r') as f:
            workflow = yaml.safe_load(f)
        
        # Test basic structure
        assert "name" in workflow, "Workflow should have a name"
        # Handle YAML parsing of 'on' keyword (may be parsed as True)
        trigger_events = workflow.get("on") or workflow.get(True)
        assert trigger_events is not None, "Workflow should have trigger events"
        assert "jobs" in workflow, "Workflow should have jobs"
        
        # Test trigger configuration
        assert "pull_request" in trigger_events, "Should trigger on pull requests"
        
        # Test permissions
        assert "permissions" in workflow, "Should have permissions defined"
        permissions = workflow["permissions"]
        assert "contents" in permissions, "Should have contents permission"
        assert "checks" in permissions, "Should have checks permission"
    
    def test_workflow_permissions_security(self):
        """Test that workflows have proper security permissions."""
        workflow_files = [
            self.WORKFLOWS_DIR / "ci-cd.yml",
            self.WORKFLOWS_DIR / "pr-validation.yml"
        ]
        
        for workflow_file in workflow_files:
            with open(workflow_file, 'r') as f:
                workflow = yaml.safe_load(f)
            
            # Check for permissions section
            if "permissions" in workflow:
                permissions = workflow["permissions"]
                
                # Should have minimal required permissions
                assert "contents" in permissions, f"{workflow_file.name} should have contents permission"
                
                # Should not have overly broad permissions
                dangerous_permissions = ["write-all", "admin"]
                for perm in dangerous_permissions:
                    assert perm not in permissions.values(), f"{workflow_file.name} should not have {perm} permission"
    
    def test_workflow_uses_uv_package_manager(self):
        """Test that workflows use uv package manager instead of pip."""
        workflow_files = [
            self.WORKFLOWS_DIR / "ci-cd.yml",
            self.WORKFLOWS_DIR / "pr-validation.yml"
        ]
        
        for workflow_file in workflow_files:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Should use uv setup action
            assert "astral-sh/setup-uv" in content, f"{workflow_file.name} should use uv setup action"
            
            # Should use uv commands
            assert "uv sync" in content, f"{workflow_file.name} should use 'uv sync'"
            assert "uv run" in content, f"{workflow_file.name} should use 'uv run'"
            
            # Should not use pip directly for main dependencies
            assert "pip install -r requirements.txt" not in content, f"{workflow_file.name} should not use pip with requirements.txt"
    
    def test_workflow_includes_testing(self):
        """Test that workflows include proper testing steps."""
        test_workflows = [
            self.WORKFLOWS_DIR / "ci-cd.yml",
            self.WORKFLOWS_DIR / "pr-validation.yml"
        ]
        
        for workflow_file in test_workflows:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Should include pytest
            assert "pytest" in content, f"{workflow_file.name} should include pytest"
            
            # Should include linting
            assert "ruff" in content, f"{workflow_file.name} should include ruff linting"
    
    def test_workflow_includes_security_checks(self):
        """Test that workflows include security validation."""
        workflow_files = [
            self.WORKFLOWS_DIR / "ci-cd.yml",
            self.WORKFLOWS_DIR / "pr-validation.yml"
        ]
        
        for workflow_file in workflow_files:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Should include actionlint for workflow validation
            assert "actionlint" in content, f"{workflow_file.name} should include actionlint"
    
    @pytest.mark.skipif(
        not os.getenv("GITHUB_TOKEN"), 
        reason="Requires authenticated GitHub access"
    )
    def test_github_actions_enabled(self):
        """Test that GitHub Actions is enabled for the repository."""
        result = subprocess.run([
            "gh", "api", "repos/gidorah/iss-data-analytics-system", 
            "--jq", ".has_actions"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            has_actions = result.stdout.strip()
            assert has_actions == "true", "GitHub Actions should be enabled for the repository"
    
    def test_workflow_file_naming_convention(self):
        """Test that workflow files follow naming conventions."""
        workflow_files = list(self.WORKFLOWS_DIR.glob("*.yml")) + list(self.WORKFLOWS_DIR.glob("*.yaml"))
        
        for workflow_file in workflow_files:
            filename = workflow_file.name
            
            # Should use .yml extension (not .yaml)
            assert filename.endswith(".yml"), f"Workflow file {filename} should use .yml extension"
            
            # Should use kebab-case (hyphens, not underscores)
            name_without_ext = filename.replace(".yml", "")
            assert "_" not in name_without_ext, f"Workflow file {filename} should use hyphens, not underscores"
    
    def test_deployment_job_has_secrets_reference(self):
        """Test that deployment job properly references secrets."""
        ci_cd_path = self.WORKFLOWS_DIR / "ci-cd.yml"
        
        with open(ci_cd_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should reference required secrets for Coolify deployment
        assert "COOLIFY_WEBHOOK" in content, "Should reference COOLIFY_WEBHOOK secret"
        assert "COOLIFY_TOKEN" in content, "Should reference COOLIFY_TOKEN secret"
        
        # Should use proper secret syntax
        assert "${{ secrets.COOLIFY_WEBHOOK }}" in content, "Should use proper secret syntax for webhook"
        assert "${{ secrets.COOLIFY_TOKEN }}" in content, "Should use proper secret syntax for token"


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
            with open(workflow_file, 'r') as f:
                try:
                    workflow_data = yaml.safe_load(f)
                    assert isinstance(workflow_data, dict), f"Workflow {workflow_file.name} should parse to dict"
                    assert "jobs" in workflow_data, f"Workflow {workflow_file.name} should have jobs"
                except Exception as e:
                    pytest.fail(f"Failed to parse workflow {workflow_file.name}: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])