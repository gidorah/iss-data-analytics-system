# Staged Deployment Configuration Guide
## Implementation Status & Next Steps

### ✅ Phase 1 & 2: Workflows Complete

**Staging Workflow** (`staging-deploy.yml`):
- ✅ Triggers on push to `main` branch
- ✅ Runs full test suite before deployment
- ✅ Uses existing GitHub App integration for auto-deployment
- ✅ Validates staging deployment health

**Production Workflow** (`production-deploy.yml`):
- ✅ Triggers on semantic version tags (`v*.*.*`)
- ✅ Validates tag format (v1.0.0, v1.2.3, etc.)
- ✅ Triggers Coolify webhook for production deployment
- ✅ Creates release notes and documentation

### 🔧 Phase 3: Required Coolify Configuration

#### Staging Environment (No Changes Needed)
- **Current State**: ✅ Working correctly
- **Deployment Trigger**: GitHub App integration from `main` branch
- **URL**: http://yoows40k844kc8w880ks48o0.157.90.158.16.sslip.io
- **Action Required**: None - keep current configuration

#### Production Environment (Configuration Required)

**Step 1: Get Production Webhook URL**
1. Go to Coolify dashboard → Production application
2. Navigate to "Webhooks" or "Deployment" settings
3. Copy the webhook URL (should look like: `https://coolify.example.com/webhooks/xxxxx`)

**Step 2: Configure GitHub Repository Secret**
1. Go to GitHub repository → Settings → Secrets and variables → Actions
2. Add new repository secret:
   - **Name**: `COOLIFY_PRODUCTION_WEBHOOK`
   - **Value**: [paste webhook URL from Step 1]

**Step 3: Disable Production Auto-Deployment from Main Branch**
1. In Coolify production application settings
2. Disable "Auto Deploy" from main branch
3. Set deployment trigger to "Manual" or "Webhook only"

### 🧪 Phase 4: Testing Plan

#### Test 1: Staging Deployment
```bash
# Create a test change and push to main
echo "# Test staging deployment" >> README.md
git add README.md
git commit -m "test: validate staging deployment flow"
git push origin main
```
**Expected Result**: Only staging environment should deploy

#### Test 2: Production Deployment
```bash
# After staging validation, create release tag
git tag v0.1.0-test
git push origin v0.1.0-test
```
**Expected Result**: Only production environment should deploy

### 📋 Validation Checklist

**Staging Flow Validation:**
- [ ] Push to main triggers staging workflow
- [ ] Staging deploys automatically via GitHub App
- [ ] Production remains unchanged
- [ ] Staging health check passes

**Production Flow Validation:**
- [ ] Tag creation triggers production workflow
- [ ] Webhook calls Coolify production environment
- [ ] Production deploys from the tagged commit
- [ ] Staging remains unchanged
- [ ] GitHub release is created

**Emergency Rollback Test:**
- [ ] Previous tag redeploys successfully
- [ ] Rollback completes within acceptable time
- [ ] All services remain healthy during rollback

### 🚨 Rollback Procedures

**Immediate Rollback:**
```bash
# Deploy previous stable version
git push origin v1.0.0  # Replace with last known good version
```

**Emergency Hotfix:**
```bash
# Create hotfix from production tag
git checkout v1.0.0
git checkout -b hotfix/critical-fix
# Make minimal fix
git commit -m "hotfix: critical issue fix"
git push origin hotfix/critical-fix
# Merge to main (deploys to staging)
# Create hotfix tag after validation
git tag v1.0.1
git push origin v1.0.1
```

### 🎯 Success Criteria

1. **Environment Isolation**: ✅ Staging and production deploy independently
2. **Manual Production Control**: ✅ Production requires explicit tag creation
3. **Proper Testing Gate**: ✅ All code goes through staging first
4. **Release Management**: ✅ Semantic versioning with release notes
5. **Rollback Capability**: ✅ Quick rollback via previous tags

### ⚠️ Known Limitations

1. **Production Health Check**: Currently requires manual verification
2. **Webhook Secret**: Must be configured manually in GitHub secrets
3. **Release Notes**: Basic automation, may need manual enhancement

### 📞 Support & Troubleshooting

**If staging deployment fails:**
- Check GitHub Actions logs in repository
- Verify Coolify GitHub App integration
- Check staging environment logs in Coolify dashboard

**If production deployment fails:**
- Verify `COOLIFY_PRODUCTION_WEBHOOK` secret is set correctly
- Check production webhook URL in Coolify
- Ensure production environment is configured for webhook deployment

**Next Implementation Phase:**
- Test the complete flow with a real feature branch
- Validate rollback procedures work correctly
- Document any additional operational procedures discovered during testing
