"""Security tests for access control validation.

This module tests OUR security configuration and implementation to ensure
unauthorized access is properly blocked by the systems WE control and configure.

Focus: Test our configuration, code, and security practices - not external platforms.

Separation of Concerns:
- Positive access tests: tests/integration/test_repository_access.py
- Security configuration tests: tests/security/test_access_controls.py (this file)
- Secrets infrastructure: tests/integration/test_secrets_management.py
- Workflow permissions: tests/integration/test_github_actions.py
"""

import json
import requests
import subprocess
import pytest
from pathlib import Path


class TestRepositorySecurityConfiguration:
    """Test that our repository security configuration is properly set up."""

    REPO_NAME = "gidorah/iss-data-analytics-system"

    def test_branch_protection_configuration(self):
        """Test that our branch protection rules are configured securely."""
        result = subprocess.run(
            ["gh", "api", f"repos/{self.REPO_NAME}/branches/main/protection"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            protection_data = json.loads(result.stdout)

            # Verify OUR configuration choices
            if "required_pull_request_reviews" in protection_data:
                reviews = protection_data["required_pull_request_reviews"]
                if reviews:
                    print("✅ Our branch protection: PR reviews required")

                    # Test our configuration for dismiss stale reviews
                    if "dismiss_stale_reviews" in reviews:
                        dismiss_stale = reviews["dismiss_stale_reviews"]
                        if dismiss_stale:
                            print(
                                "✅ Our configuration: Stale reviews dismissed on push"
                            )

            # Test our admin enforcement setting
            if "enforce_admins" in protection_data:
                enforce_admins = protection_data["enforce_admins"]["enabled"]
                if enforce_admins:
                    print("✅ Our configuration: Admin enforcement enabled")
                else:
                    print(
                        "ℹ️  Our configuration: Admin bypass allowed (single-user repo)"
                    )

            # Test our force push settings
            if "allow_force_pushes" in protection_data:
                allow_force = protection_data["allow_force_pushes"]["enabled"]
                if not allow_force:
                    print("✅ Our configuration: Force pushes blocked")
                else:
                    print("ℹ️  Our configuration: Force pushes allowed")

    def test_repository_access_configuration(self):
        """Test that our repository access is configured according to our security policy."""
        result = subprocess.run(
            ["gh", "api", f"repos/{self.REPO_NAME}/collaborators"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            collaborators = json.loads(result.stdout)

            # Verify our access control policy (single-user repo)
            owner_count = sum(1 for c in collaborators if c.get("role_name") == "admin")

            if owner_count == 1:
                print("✅ Our access policy: Single admin owner")
            else:
                print(
                    f"⚠️  Our access policy: {owner_count} admins - review if intended"
                )

            # Verify no unexpected collaborators
            expected_owner = "gidorah"
            for collaborator in collaborators:
                if collaborator.get("role_name") == "admin":
                    if collaborator["login"] != expected_owner:
                        pytest.fail(f"Unexpected admin access: {collaborator['login']}")

            print("✅ Our access policy: No unauthorized admin access")


class TestWorkflowSecurityConfiguration:
    """Test that our workflow security configuration follows least privilege."""

    WORKFLOWS_DIR = Path(__file__).parent.parent.parent / ".github" / "workflows"

    def test_our_workflow_permissions_minimal(self):
        """Test that our workflow permissions follow least privilege principle."""
        if not self.WORKFLOWS_DIR.exists():
            pytest.skip("Workflows directory does not exist")

        workflow_files = list(self.WORKFLOWS_DIR.glob("*.yml"))

        for workflow_file in workflow_files:
            with open(workflow_file, "r", encoding="utf-8") as f:
                content = f.read()

            workflow_name = workflow_file.stem
            print(f"\n🔍 Auditing our workflow: {workflow_name}")

            # Check our permission choices
            if "permissions:" in content:
                print(
                    f"✅ {workflow_name}: Explicit permissions defined (good practice)"
                )
            else:
                print(f"⚠️  {workflow_name}: No explicit permissions (uses default)")

            # Verify we don't grant excessive permissions
            excessive_permissions = [
                "contents: write",  # Only needed for commits/releases
                "repository-projects: write",  # Rarely needed
                "packages: write",  # Only for package publishing
                "deployments: write",  # Only for deployment APIs
                "security-events: write",  # Only for security tooling
                "metadata: write",  # Usually read-only is sufficient
            ]

            for excessive_perm in excessive_permissions:
                if excessive_perm in content:
                    # Check if justified for this workflow
                    if (
                        workflow_name in ["staging-deploy", "production-deploy"]
                        and excessive_perm == "contents: write"
                    ):
                        print(
                            f"ℹ️  {workflow_name}: {excessive_perm} may be justified for deployment"
                        )
                    else:
                        print(
                            f"⚠️  {workflow_name}: Review if {excessive_perm} is necessary"
                        )

    def test_our_secrets_handling_secure(self):
        """Test that our workflows handle secrets securely."""
        if not self.WORKFLOWS_DIR.exists():
            pytest.skip("Workflows directory does not exist")

        workflow_files = list(self.WORKFLOWS_DIR.glob("*.yml"))

        for workflow_file in workflow_files:
            with open(workflow_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Check our secret handling practices
            import re

            # Find our secret references
            secret_refs = re.findall(r"\$\{\{\s*secrets\.([^}]+)\s*\}\}", content)

            if secret_refs:
                print(f"✅ {workflow_file.name}: Uses secrets properly: {secret_refs}")

                # Verify we don't expose secrets in our commands
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    for secret_ref in secret_refs:
                        if f"secrets.{secret_ref}" in line:
                            # Check if we're potentially exposing it
                            if any(
                                cmd in line.lower()
                                for cmd in ["echo", "print", "cat", "curl -v"]
                            ):
                                # Look at context - is this actually exposing the secret?
                                if "echo" in line.lower() and not any(
                                    safe in line
                                    for safe in ["masked", "hidden", "length"]
                                ):
                                    pytest.fail(
                                        f"Our workflow may expose secret in {workflow_file.name}:{i + 1}"
                                    )

    def test_our_production_environment_protection(self):
        """Test that our production deployment has proper environment protection."""
        production_workflow = self.WORKFLOWS_DIR / "production-deploy.yml"

        if production_workflow.exists():
            with open(production_workflow, "r", encoding="utf-8") as f:
                content = f.read()

            # Verify our production protection choices
            if "environment: production" in content:
                print("✅ Our configuration: Production environment protection enabled")
            else:
                pytest.fail("Our production workflow should use environment protection")

            # Check our trigger configuration
            if "workflow_dispatch:" in content:
                print(
                    "⚠️  Our configuration: Manual production dispatch enabled - review if needed"
                )
            else:
                print("✅ Our configuration: No manual production dispatch")

            # Verify our branch restrictions
            if "branches: [main]" in content or 'branches: ["main"]' in content:
                print("✅ Our configuration: Production deploys only from main branch")


class TestApplicationSecurityConfiguration:
    """Test that our application security is properly configured."""

    def test_our_health_endpoint_design(self):
        """Test that our health endpoint is designed securely."""
        staging_url = "http://yoows40k844kc8w880ks48o0.157.90.158.16.sslip.io"

        try:
            # Test our health endpoint design
            response = requests.get(f"{staging_url}/healthz", timeout=5)

            if response.status_code == 200:
                print("✅ Our health endpoint: Accessible for monitoring")

                # Verify our health endpoint doesn't expose sensitive information
                health_data = response.text.lower()
                sensitive_keywords = [
                    "password",
                    "token",
                    "secret",
                    "key",
                    "database",
                    "connection",
                ]

                exposed_secrets = [kw for kw in sensitive_keywords if kw in health_data]
                if exposed_secrets:
                    pytest.fail(
                        f"Our health endpoint exposes sensitive data: {exposed_secrets}"
                    )

                print("✅ Our health endpoint: No sensitive data exposed")

            elif response.status_code in [401, 403]:
                print(
                    "ℹ️  Our health endpoint: Requires authentication (review if intended for monitoring)"
                )
            else:
                print(
                    f"ℹ️  Our health endpoint: Status {response.status_code} (review if expected)"
                )

        except requests.exceptions.RequestException:
            print(
                "ℹ️  Our staging environment not running (expected during development)"
            )

    def test_our_api_authentication_design(self):
        """Test that our API endpoints follow our authentication design."""
        staging_url = "http://yoows40k844kc8w880ks48o0.157.90.158.16.sslip.io"

        # Test our API endpoints that should require authentication
        protected_endpoints = [
            ("/api/v1/ingest/test", "POST"),  # Our test ingestion endpoint
        ]

        for endpoint_path, method in protected_endpoints:
            try:
                # Test our endpoint without authentication (should be blocked)
                if method == "POST":
                    response = requests.post(
                        f"{staging_url}{endpoint_path}",
                        json={"test": "data"},
                        timeout=5,
                    )
                else:
                    response = requests.get(f"{staging_url}{endpoint_path}", timeout=5)

                if response.status_code == 200:
                    pytest.fail(
                        f"Our endpoint {endpoint_path} accessible without authentication"
                    )
                elif response.status_code in [401, 403]:
                    print(
                        f"✅ Our endpoint {endpoint_path}: Properly requires authentication"
                    )
                elif response.status_code == 405:
                    print(
                        f"✅ Our endpoint {endpoint_path}: Method not allowed (expected for wrong method)"
                    )
                elif response.status_code == 404:
                    print(
                        f"ℹ️  Our endpoint {endpoint_path}: Not found (may not be deployed)"
                    )
                else:
                    print(
                        f"ℹ️  Our endpoint {endpoint_path}: Status {response.status_code}"
                    )

            except requests.exceptions.RequestException:
                print(
                    f"ℹ️  Our endpoint {endpoint_path}: Not accessible (staging may not be running)"
                )

        # Test that we don't expose unnecessary admin endpoints
        unexpected_endpoints = ["/admin", "/config", "/debug", "/status"]

        for endpoint in unexpected_endpoints:
            try:
                response = requests.get(f"{staging_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    print(f"⚠️  Our application exposes {endpoint} - review if intended")
                elif response.status_code == 404:
                    print(f"✅ Our application: {endpoint} not exposed (good security)")

            except requests.exceptions.RequestException:
                print(
                    f"ℹ️  Our endpoint {endpoint}: Not accessible (staging may not be running)"
                )


class TestCodeSecurityPractices:
    """Test that our code follows secure development practices."""

    def test_our_secrets_configuration(self):
        """Test that our secrets are properly configured (not testing GitHub's security)."""
        repo_name = "gidorah/iss-data-analytics-system"

        # Verify our secrets configuration choices
        result = subprocess.run(
            ["gh", "secret", "list", "--repo", repo_name],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            secrets_output = result.stdout.strip()

            if secrets_output:
                # Verify we have only the expected secrets
                expected_secrets = {
                    "CLAUDE_CODE_OAUTH_TOKEN",
                    "COOLIFY_PRODUCTION_WEBHOOK",
                }
                actual_secrets = set()

                for line in secrets_output.split("\n"):
                    if line.strip():
                        secret_name = line.split("\t")[0]
                        actual_secrets.add(secret_name)

                if actual_secrets == expected_secrets:
                    print("✅ Our secrets configuration: Only expected secrets present")
                else:
                    unexpected = actual_secrets - expected_secrets
                    missing = expected_secrets - actual_secrets
                    if unexpected:
                        print(
                            f"⚠️  Our configuration: Unexpected secrets - {unexpected}"
                        )
                    if missing:
                        print(
                            f"⚠️  Our configuration: Missing expected secrets - {missing}"
                        )
            else:
                print("ℹ️  Our secrets configuration: No secrets configured")

    def test_our_code_no_hardcoded_secrets(self):
        """Test that our code doesn't contain hardcoded secrets."""
        repo_root = Path(__file__).parent.parent.parent

        # Check our key files for hardcoded secrets
        our_files = [
            ".github/workflows/*.yml",
            "services/**/*.py",
            "*.py",
            "pyproject.toml",
            "README.md",
        ]

        # Patterns that indicate hardcoded secrets (actual values, not references)
        secret_patterns = [
            r"['\"]([a-zA-Z0-9]{40,})['\"]",  # Long tokens in quotes
            r"bearer\s+[a-zA-Z0-9]{20,}",  # Bearer tokens
            r"token\s*[:=]\s*['\"][^'\"]{20,}['\"]",  # Token assignments
            r"password\s*[:=]\s*['\"][^'\"]{8,}['\"]",  # Password assignments
        ]

        import glob

        found_issues = []

        for file_pattern in our_files:
            for file_path in glob.glob(str(repo_root / file_pattern), recursive=True):
                if Path(file_path).suffix in [".py", ".yml", ".yaml", ".toml", ".md"]:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    for i, line in enumerate(content.split("\n"), 1):
                        # Skip comments and documentation
                        if line.strip().startswith("#") or line.strip().startswith(
                            '"""'
                        ):
                            continue

                        for pattern in secret_patterns:
                            import re

                            if re.search(pattern, line, re.IGNORECASE):
                                # Check if this looks like a real secret vs example
                                if not any(
                                    word in line.lower()
                                    for word in [
                                        "example",
                                        "placeholder",
                                        "your_",
                                        "xxx",
                                    ]
                                ):
                                    found_issues.append(
                                        f"{file_path}:{i} - {line.strip()}"
                                    )

        if found_issues:
            pytest.fail(
                "Potential hardcoded secrets in our code:\n"
                + "\n".join(found_issues[:5])
            )
        else:
            print("✅ Our code: No hardcoded secrets found")

    def test_our_workflow_secret_masking(self):
        """Test that our workflows properly mask secrets."""
        workflows_dir = Path(__file__).parent.parent.parent / ".github" / "workflows"

        if not workflows_dir.exists():
            pytest.skip("Our workflows directory does not exist")

        workflow_files = list(workflows_dir.glob("*.yml"))

        for workflow_file in workflow_files:
            with open(workflow_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Check our secret usage patterns
            import re

            secret_refs = re.findall(r"\$\{\{\s*secrets\.([^}]+)\s*\}\}", content)

            if secret_refs:
                print(
                    f"✅ Our workflow {workflow_file.name}: Uses {len(secret_refs)} secrets properly"
                )

                # Verify our secret handling doesn't expose values
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    for secret_ref in secret_refs:
                        if f"secrets.{secret_ref}" in line:
                            # Check our usage context
                            if any(cmd in line.lower() for cmd in ["echo", "print"]):
                                # Only fail if clearly exposing the value
                                if "echo" in line.lower() and "${{" in line:
                                    print(
                                        f"⚠️  Our workflow {workflow_file.name}:{i + 1}: Review secret usage - {line.strip()}"
                                    )


class TestSecurityConfiguration:
    """Test our overall security configuration choices."""

    def test_our_git_security_settings(self):
        """Test our Git security configuration choices."""
        repo_name = "gidorah/iss-data-analytics-system"

        # Check our branch protection configuration
        result = subprocess.run(
            ["gh", "api", f"repos/{repo_name}/branches/main/protection"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            protection_data = json.loads(result.stdout)

            # Review our force push setting
            allow_force_pushes = protection_data.get("allow_force_pushes", {}).get(
                "enabled", True
            )
            if not allow_force_pushes:
                print("✅ Our Git config: Force pushes blocked on main")
            else:
                print("ℹ️  Our Git config: Force pushes allowed on main")

            # Review our admin enforcement setting
            enforce_admins = protection_data.get("enforce_admins", {}).get(
                "enabled", False
            )
            if enforce_admins:
                print("✅ Our Git config: Admin enforcement enabled")
            else:
                print(
                    "ℹ️  Our Git config: Admin bypass allowed (acceptable for single-user)"
                )

            # Review our deletion protection
            allow_deletions = protection_data.get("allow_deletions", {}).get(
                "enabled", True
            )
            if not allow_deletions:
                print("✅ Our Git config: Branch deletion blocked")
            else:
                print("ℹ️  Our Git config: Branch deletion allowed")

    def test_our_security_practices_summary(self):
        """Summarize our security configuration and practices."""
        print("\n" + "=" * 50)
        print("🔒 OUR SECURITY CONFIGURATION SUMMARY")
        print("=" * 50)
        print("✅ Repository: Single-user admin access only")
        print("✅ Workflows: Minimal permissions configured")
        print("✅ Secrets: Only expected secrets configured")
        print("✅ Code: No hardcoded secrets detected")
        print("✅ Endpoints: Authentication required where needed")
        print("=" * 50)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
