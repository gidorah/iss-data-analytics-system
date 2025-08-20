# Coolify Configuration Backup
## Pre-Migration Configuration State

### Current Workflow Configuration
- **File**: `.github/workflows/ci-cd.yml`
- **Trigger**: Push to main branch
- **Issue**: Deploys to both staging and production simultaneously

### Environment URLs and Configuration
#### Staging Environment
- **URL**: http://yoows40k844kc8w880ks48o0.157.90.158.16.sslip.io
- **Current Trigger**: Main branch push (via GitHub App integration)
- **Environment Variables**:
  - `ENVIRONMENT=staging` (expected)
  - `LOG_LEVEL=DEBUG` (expected)

#### Production Environment
- **URL**: TBD (not documented in current workflows)
- **Current Trigger**: Main branch push (problematic - needs to change to tag-based)
- **Environment Variables**:
  - `ENVIRONMENT=production` (expected)
  - `LOG_LEVEL=INFO` (expected)

### Migration Notes
1. **Current Problem**: Both environments deploy on main branch push
2. **Target Solution**:
   - Staging: Auto-deploy from main branch (keep current)
   - Production: Deploy only from release tags (requires reconfiguration)

### Required Changes
1. Replace `ci-cd.yml` with separate staging and production workflows
2. Reconfigure Coolify production environment for tag-based deployment
3. Test and validate new deployment flow

### Rollback Plan
If issues occur during migration:
1. Restore original `ci-cd.yml` workflow
2. Revert Coolify production configuration
3. Test deployment functionality
4. Investigate issues before retrying migration

**Migration Date**: $(date -u)
**Current Branch**: staged-deployment-implementation
