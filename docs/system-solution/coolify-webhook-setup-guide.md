# Coolify Webhook Setup Guide
## How to Get Production Webhook URL

### Method 1: Coolify Dashboard - Application Settings

**🧪 Testing staged deployment - staging only deployment validation**

**Step 1: Access Your Production Application**
1. Log into your Coolify dashboard
2. Navigate to your production application/service
3. Look for one of these sections:
   - **"Webhooks"** tab
   - **"Deployment"** settings
   - **"Configuration"** section
   - **"Settings"** → **"Deployment"**

**Step 2: Find Webhook Configuration**
Look for:
- **"Webhook URL"** or **"Deploy Webhook"**
- **"Manual Deployment Trigger"**
- **"API Endpoints"** or **"Deployment API"**
- Button like **"Generate Webhook"** or **"Create Webhook"**

**Step 3: Copy Webhook URL**
The webhook URL typically looks like:
```
https://coolify.yourdomain.com/api/webhooks/[app-id]/[secret-token]
```
or
```
https://coolify.yourdomain.com/webhooks/deploy/[unique-id]
```

### Method 2: Application Overview/Summary

**Alternative Location:**
1. Go to application overview/dashboard
2. Look for **"Quick Actions"** or **"Deployment"** section
3. Find **"Webhook URL"** or **"Deploy API"** link

### Method 3: API/Integration Settings

**If webhook section exists:**
1. Navigate to **"Integrations"** or **"API"** settings
2. Look for **"Deployment Webhooks"**
3. Generate or copy existing webhook URL

### Method 4: Check Application Configuration

**Look in these sections:**
- Application **"Environment"** settings
- **"Build & Deploy"** configuration
- **"Source"** or **"Git"** settings
- **"Advanced"** settings

## What to Look For

### Webhook URL Format
```bash
# Typical Coolify webhook formats:
https://your-coolify-domain.com/api/webhooks/APP_ID/SECRET
https://your-coolify-domain.com/webhooks/deploy/UNIQUE_ID
https://your-coolify-domain.com/api/deploy/APP_NAME
```

### Webhook Authentication
Coolify webhooks may use:
1. **URL-embedded secret** (most common)
2. **Bearer token** in headers
3. **API key** parameter
4. **No authentication** (if configured for simplicity)

## Configuration Steps

### Step 1: Get the Webhook URL
1. Access Coolify dashboard
2. Navigate to production application
3. Find webhook/deployment section
4. Copy the webhook URL

### Step 2: Add to GitHub Secrets
1. Go to GitHub repository
2. Settings → Secrets and variables → Actions
3. Add new repository secret:
   ```
   Name: COOLIFY_PRODUCTION_WEBHOOK
   Value: [paste webhook URL]
   ```

### Step 3: Test Webhook (Optional)
```bash
# Test webhook manually (replace with your URL)
curl -X POST "YOUR_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"ref": "refs/tags/v1.0.0", "sha": "abc123"}'
```

### Step 4: Disable Auto-Deployment from Main
1. In production application settings
2. Find **"Auto Deploy"** or **"Branch Deployment"**
3. Disable auto-deployment from `main` branch
4. Set deployment trigger to **"Manual"** or **"Webhook Only"**

## Troubleshooting

### If No Webhook Section Found:
1. **Check Application Type**: Some application types may not support webhooks
2. **Check Coolify Version**: Older versions might have different UI
3. **Check Permissions**: Ensure you have admin access to the application
4. **Contact Support**: Check Coolify documentation or community

### If Webhook Doesn't Work:
1. **Verify URL**: Ensure webhook URL is correct and accessible
2. **Check Headers**: Some webhooks require specific headers
3. **Check Payload**: Verify JSON payload format
4. **Check Logs**: Look at Coolify application logs for webhook requests

### Alternative: Use GitHub App Integration
If webhooks are not available or working:
1. Keep production using GitHub App integration
2. Create a **separate branch** for production (e.g., `production`)
3. Merge tags to production branch to trigger deployment
4. This maintains tag-based control while using existing integration

## Quick Action Items

**Immediate Steps:**
1. ☐ Log into Coolify dashboard
2. ☐ Navigate to production application
3. ☐ Look for webhook/deployment settings
4. ☐ Copy webhook URL
5. ☐ Add `COOLIFY_PRODUCTION_WEBHOOK` secret to GitHub
6. ☐ Test webhook with a curl command
7. ☐ Disable auto-deployment from main branch

**Fallback Plan:**
If webhooks are not available, we can modify the production workflow to use a production branch instead of webhooks while maintaining tag-based control.
