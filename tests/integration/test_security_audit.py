"""Integration tests for security audit validation and compliance.

This module validates that our security audit schedule is being followed
and triggers failures when audits are due.

Separation of Concerns:
- Security configuration tests: tests/security/test_access_controls.py
- Repository access tests: tests/integration/test_repository_access.py
- Secrets infrastructure: tests/integration/test_secrets_management.py
- Security audit validation: tests/integration/test_security_audit.py (this file)
"""

from datetime import datetime, timedelta
import pytest


class TestSecurityAuditSchedule:
    """Test that security audit schedule is being followed."""

    # Based on docs/security/audit-trail.md
    LAST_AUDIT_DATE = datetime(2025, 8, 22)  # 22 August 2025
    QUARTERLY_REVIEW_INTERVAL = 90  # days
    ANNUAL_ASSESSMENT_INTERVAL = 365  # days

    def test_quarterly_security_review_not_overdue(self):
        """Test that quarterly security review is not overdue."""
        today = datetime.now()
        next_quarterly_due = self.LAST_AUDIT_DATE + timedelta(
            days=self.QUARTERLY_REVIEW_INTERVAL
        )

        # Fail if quarterly review is overdue
        if today > next_quarterly_due:
            pytest.fail(
                f"🔴 SECURITY AUDIT OVERDUE: Quarterly review was due {next_quarterly_due.strftime('%Y-%m-%d')}. "
                f"Current date: {today.strftime('%Y-%m-%d')}. "
                f"Last audit: {self.LAST_AUDIT_DATE.strftime('%Y-%m-%d')}. "
                f"\n\n📋 TO PERFORM AUDIT:"
                f"\n1. Use the AI Agent Security Audit Prompt in docs/security/audit-trail.md"
                f"\n2. Update 'Last Audit' date to today's date"
                f"\n3. Update 'Next Review' date to {(today + timedelta(days=self.QUARTERLY_REVIEW_INTERVAL)).strftime('%Y-%m-%d')}"
                f"\n4. Document any findings in the Security Incidents log"
                f"\n\n📄 See: docs/security/audit-trail.md (lines 185-231)"
            )

        # Warn if review is due soon (within 14 days)
        if today > (next_quarterly_due - timedelta(days=14)):
            print(
                f"⚠️  Quarterly security review due soon: {next_quarterly_due.strftime('%Y-%m-%d')}. "
                f"Please schedule review using prompt in docs/security/audit-trail.md"
            )

    def test_annual_security_assessment_not_overdue(self):
        """Test that annual security assessment is not overdue."""
        today = datetime.now()
        next_annual_due = self.LAST_AUDIT_DATE + timedelta(
            days=self.ANNUAL_ASSESSMENT_INTERVAL
        )

        # Fail if annual assessment is overdue
        if today > next_annual_due:
            pytest.fail(
                f"🔴 SECURITY AUDIT OVERDUE: Annual assessment was due {next_annual_due.strftime('%Y-%m-%d')}. "
                f"Current date: {today.strftime('%Y-%m-%d')}. "
                f"Last audit: {self.LAST_AUDIT_DATE.strftime('%Y-%m-%d')}. "
                f"\n\n📋 TO PERFORM ANNUAL ASSESSMENT:"
                f"\n1. Use the AI Agent Security Audit Prompt in docs/security/audit-trail.md"
                f"\n2. Conduct comprehensive security review of entire system"
                f"\n3. Update 'Last Audit' date to today's date"
                f"\n4. Update 'Next Review' date to {(today + timedelta(days=self.QUARTERLY_REVIEW_INTERVAL)).strftime('%Y-%m-%d')} (next quarterly)"
                f"\n5. Document findings and update security attestation"
                f"\n\n📄 See: docs/security/audit-trail.md (lines 185-231)"
            )

        # Warn if assessment is due soon (within 30 days)
        if today > (next_annual_due - timedelta(days=30)):
            print(
                f"⚠️  Annual security assessment due soon: {next_annual_due.strftime('%Y-%m-%d')}. "
                f"Please schedule comprehensive assessment using prompt in docs/security/audit-trail.md"
            )

    def test_audit_schedule_status(self):
        """Display current audit schedule status."""
        today = datetime.now()
        next_quarterly = self.LAST_AUDIT_DATE + timedelta(
            days=self.QUARTERLY_REVIEW_INTERVAL
        )
        next_annual = self.LAST_AUDIT_DATE + timedelta(
            days=self.ANNUAL_ASSESSMENT_INTERVAL
        )

        print("\n📅 Security Audit Schedule Status:")
        print(f"   Last Audit: {self.LAST_AUDIT_DATE.strftime('%Y-%m-%d')}")
        print(f"   Current Date: {today.strftime('%Y-%m-%d')}")
        print(f"   Next Quarterly Review: {next_quarterly.strftime('%Y-%m-%d')}")
        print(f"   Next Annual Assessment: {next_annual.strftime('%Y-%m-%d')}")

    def test_security_best_practices_compliance(self):
        """Test compliance with security best practices."""
        import os
        from pathlib import Path

        repo_root = Path(__file__).parent.parent.parent

        # Test that sensitive files are not committed to repository
        sensitive_patterns = [
            ".env",
            "id_rsa",
            "private_key",
            "secret_key",
            ".pem",
            ".p12",
            ".pfx",
            "credentials.json",
            "service-account.json",
        ]

        # Check that sensitive files are not committed to repository
        all_files = []
        for root, dirs, files in os.walk(repo_root):
            # Skip .git directory and other VCS directories
            if any(vcs_dir in root for vcs_dir in [".git", ".svn", ".hg"]):
                continue
            # Skip node_modules and other dependency directories
            if any(
                dep_dir in root
                for dep_dir in ["node_modules", "__pycache__", ".pytest_cache"]
            ):
                continue
            all_files.extend([os.path.join(root, f) for f in files])

        sensitive_files_found = []
        for file_path in all_files:
            file_name = os.path.basename(file_path).lower()
            for pattern in sensitive_patterns:
                if pattern in file_name:
                    # Allow some exceptions (like documentation files)
                    if not any(
                        allowed in file_path.lower()
                        for allowed in [
                            "readme",
                            "doc",
                            "example",
                            "sample",
                            "template",
                            ".md",
                        ]
                    ):
                        sensitive_files_found.append(file_path)

        if sensitive_files_found:
            pytest.fail(
                "🔴 SECURITY VIOLATION: Potentially sensitive files found in repository:\n"
                + "\n".join([f"  - {f}" for f in sensitive_files_found])
                + "\n\nThese files should be:"
                "\n1. Removed from repository if they contain secrets"
                "\n2. Added to .gitignore to prevent future commits"
                "\n3. Secrets moved to GitHub repository secrets or environment variables"
            )

        print(
            "✅ Security best practices compliance verified - no sensitive files detected"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
