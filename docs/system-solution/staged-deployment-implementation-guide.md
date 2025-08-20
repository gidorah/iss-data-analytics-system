# Staged Deployment Implementation Guide
## Transition from Flawed to Proper DevOps Architecture

### Overview

This guide documents the transition from the current flawed deployment architecture (both environments deploy simultaneously) to a proper staged deployment pipeline with manual production control.

### Current Architecture Issues ❌

**Critical Problems:**
1. **Simultaneous Deployment**: Both staging and production deploy on every push to main
2. **No Production Gate**: Zero manual control over production deployments
3. **High Risk**: Production failures affect users immediately
4. **No Release Management**: No versioning or rollback strategy

**Current Workflow (Broken):**
```
Push to main → CI/CD Pipeline → Deploy to Staging + Production (simultaneously)
```

### New Staged Architecture ✅

**Proper DevOps Flow:**
```
Push to main → Deploy to Staging → Manual Validation → Release Tag → Deploy to Production
```

**Key Improvements:**
- Staging serves as integration environment for continuous testing
- Production requires explicit release decision via Git tags
- Clear rollback capability via previous tags
- Proper release management with semantic versioning

## Implementation Plan

### Phase 1: Update GitHub Actions Workflows

#### Current Workflow Structure
```
.github/workflows/
├── pr-validation.yml     # ✅ Keep as-is
└── ci-cd.yml            # ❌ Replace with staged workflows
```

#### New Workflow Structure
```
.github/workflows/
├── pr-validation.yml        # ✅ Existing - no changes needed
├── staging-deploy.yml       # 🆕 New - auto-deploy to staging
└── production-deploy.yml    # 🆕 New - deploy to production on tags
```

### Phase 2: GitHub Actions Workflow Definitions

#### 1. Keep Existing: `pr-validation.yml`
No changes needed - continues to validate pull requests.

#### 2. Create New: `staging-deploy.yml`
```yaml
name: Deploy to Staging

on:
  push:
    branches: [main]

permissions:
  contents: read
  actions: read
  checks: write

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Install dependencies
        run: uv sync --all-packages

      - name: Run tests
        run: uv run pytest

      - name: Security scan
        run: uv run bandit -r services/ingestion/

      - name: Lint code
        run: uv run ruff check .

      - name: Validate workflows
        run: |
          curl -LsSf https://github.com/rhysd/actionlint/releases/latest/download/actionlint_linux_amd64.tar.gz | tar xz
          ./actionlint

  deploy-staging:
    needs: test
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - name: Deploy to Staging via Coolify
        run: |
          echo "🚀 Deploying to staging environment..."
          # Coolify webhook trigger will auto-deploy from main branch
          echo "✅ Staging deployment initiated"

      - name: Validate staging deployment
        run: |
          echo "🏥 Validating staging deployment..."
          sleep 30  # Wait for deployment
          curl -f http://yoows40k844kc8w880ks48o0.157.90.158.16.sslip.io/healthz
          echo "✅ Staging deployment validated"
```

#### 3. Create New: `production-deploy.yml`
```yaml
name: Deploy to Production

on:
  push:
    tags:
      - 'v*.*.*'  # Triggers on semantic version tags (v1.0.0, v1.2.3, etc.)

permissions:
  contents: read
  actions: read

jobs:
  deploy-production:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Validate tag format
        run: |
          TAG=${GITHUB_REF#refs/tags/}
          echo "🏷️  Deploying tag: $TAG"
          if [[ ! $TAG =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
            echo "::error::Invalid tag format. Use semantic versioning (v1.0.0)"
            exit 1
          fi

      - name: Generate release notes
        run: |
          TAG=${GITHUB_REF#refs/tags/}
          echo "## Release $TAG" >> release-notes.md
          echo "Deployed at: $(date -u)" >> release-notes.md
          echo "Commit: $GITHUB_SHA" >> release-notes.md

      - name: Deploy to Production via Coolify
        run: |
          echo "🚀 Deploying $TAG to production environment..."
          # Production Coolify webhook will trigger from this tag
          echo "✅ Production deployment initiated"

      - name: Validate production deployment
        run: |
          echo "🏥 Validating production deployment..."
          sleep 45  # Wait for deployment
          # Update URL when production domain is configured
          echo "⚠️  Production URL validation pending - manual verification required"
          echo "✅ Production deployment process completed"

      - name: Create GitHub Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          body_path: release-notes.md
          draft: false
          prerelease: false
```

### Phase 3: Coolify Configuration Changes

#### Current Configuration Issues
Both environments currently deploy from the same webhook trigger (main branch).

#### Required Changes

**Staging Environment (Keep Current):**
- ✅ **Git Branch**: `main` (keep current webhook)
- ✅ **Auto-deploy**: Enabled on push to main
- ✅ **Environment Variables**: `ENVIRONMENT=staging`, `LOG_LEVEL=DEBUG`

**Production Environment (Reconfigure):**
- ❌ **Change Git Branch**: From `main` to tag-based deployment
- ❌ **Change Auto-deploy**: From main branch to tag triggers only
- ✅ **Environment Variables**: `ENVIRONMENT=production`, `LOG_LEVEL=INFO`

#### Production Environment Reconfiguration Steps

1. **Access Production Environment in Coolify**
2. **Update Git Configuration**:
   - Change from branch-based to tag-based deployment
   - Disable auto-deployment from main branch
   - Configure webhook to trigger only on tag creation

3. **Update Environment Variables** (if not already set):
   ```bash
   ENVIRONMENT=production
   LOG_LEVEL=INFO
   SERVICE_NAME=ingestion-service
   API_V1_PREFIX=/api/v1
   ```

### Phase 4: Workflow Migration Process

#### Step 1: Backup Current Configuration
```bash
# Document current Coolify settings
# Export environment variables
# Note current webhook URLs
```

#### Step 2: Create New Workflow Files
1. Rename `ci-cd.yml` to `staging-deploy.yml`
2. Update `staging-deploy.yml` with staging-specific configuration
3. Create new `production-deploy.yml` for tag-based deployment

#### Step 3: Test Staging Deployment
1. Push a test change to main branch
2. Verify only staging environment deploys
3. Validate staging deployment success

#### Step 4: Configure Production for Tag-Based Deployment
1. Update Coolify production environment settings
2. Change webhook trigger from main branch to tags
3. Test with a pre-release tag (e.g., `v0.1.0-test`)

#### Step 5: Validate Complete Flow
1. Create a feature branch
2. Open PR → Verify PR validation runs
3. Merge to main → Verify staging-only deployment
4. Create release tag → Verify production-only deployment

### Phase 5: Release Management Process

#### Creating Releases

**Standard Release:**
```bash
# After staging validation
git tag v1.0.0
git push origin v1.0.0
# Triggers production deployment
```

**Hotfix Release:**
```bash
# Create hotfix branch from production tag
git checkout v1.0.0
git checkout -b hotfix/critical-fix
# Make fixes, test in staging
git tag v1.0.1
git push origin v1.0.1
# Triggers production deployment
```

**Rollback:**
```bash
# Deploy previous version
git push origin v1.0.0
# Re-deploys previous stable version
```

### Phase 6: Validation and Testing

#### Test Scenarios

1. **Feature Development Flow**:
   - Create feature branch
   - PR validation ✅
   - Merge to main → Staging deployment only ✅
   - Manual staging validation ✅

2. **Production Release Flow**:
   - Create release tag → Production deployment only ✅
   - Verify production health ✅
   - Verify staging unchanged ✅

3. **Emergency Rollback**:
   - Push previous tag ✅
   - Verify rollback deployment ✅
   - Verify system restoration ✅

#### Success Criteria

- ✅ Staging deploys automatically on main branch merge
- ✅ Production deploys only on release tag creation
- ✅ Environments are isolated (staging changes don't affect production)
- ✅ Clear rollback capability via previous tags
- ✅ Proper release management with semantic versioning

## Benefits of New Architecture

### Risk Reduction
- **Staging Gate**: All changes validated in staging before production
- **Manual Control**: Production deployments require explicit action
- **Rollback Safety**: Clear rollback path via previous tags

### Operational Excellence
- **Release Management**: Proper versioning and release notes
- **Environment Isolation**: Clear separation between staging and production
- **Deployment Visibility**: Clear audit trail of production releases

### Development Workflow
- **Continuous Integration**: Immediate staging feedback on main branch
- **Release Flexibility**: Deploy production when ready, not automatically
- **Emergency Response**: Fast rollback capability for critical issues

## Implementation Timeline

**Phase 1**: Update documentation and plan (Complete)
**Phase 2**: Create new GitHub Actions workflows (1-2 hours)
**Phase 3**: Reconfigure Coolify production environment (30 minutes)
**Phase 4**: Test and validate new flow (1 hour)
**Phase 5**: Document and train on new release process (30 minutes)

**Total Estimated Time**: 3-4 hours

This implementation will transform the deployment architecture from a high-risk simultaneous deployment to a professional-grade staged deployment pipeline with proper controls and rollback capability.
