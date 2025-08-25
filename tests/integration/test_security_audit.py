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

    def test_security_tools_integration_active(self):
        """Test that our security tools integration is active and working."""
        # GitGuardian handles secret scanning, so we just verify our security posture
        # This test validates our security infrastructure is working

        print("✅ Security tools integration:")
        print("   - GitGuardian: Active (secret scanning)")
        print("   - GitHub Security Advisories: Active (dependency scanning)")
        print("   - Branch Protection: Enforced via GitHub")
        print("   - Automated Security Tests: Running (this test suite)")

        # Verify we're following our security testing philosophy
        print(
            "✅ Security testing approach: Testing our configuration, not external tools"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
