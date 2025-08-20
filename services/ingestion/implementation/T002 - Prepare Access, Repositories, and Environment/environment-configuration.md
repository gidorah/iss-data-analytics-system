# Environment Configuration Documentation
## T002 Task 2.5.5 - Environment-Specific Deployment Settings

### Overview

This document describes the environment-specific configuration for the ISS Data Analytics System ingestion service deployed on Coolify Cloud platform.

### Environment Summary

| Environment | Status | Purpose | Domain Type |
|-------------|--------|---------|-------------|
| Staging | ✅ Active | Development testing, feature validation | Auto-generated sslip.io |
| Production | ✅ Active | Production workload | Auto-generated sslip.io |

### Environment Variables Configuration

#### Staging Environment
```bash
ENVIRONMENT=staging
LOG_LEVEL=DEBUG
SERVICE_NAME=ingestion-service
API_V1_PREFIX=/api/v1
```

#### Production Environment
```bash
ENVIRONMENT=production
LOG_LEVEL=INFO
SERVICE_NAME=ingestion-service
API_V1_PREFIX=/api/v1
```

### Coolify Configuration Settings

#### Common Settings (Both Environments)
- **Build Pack**: Dockerfile
- **Base Directory**: `/` (repository root for monorepo workspace access)
- **Dockerfile Location**: `services/ingestion/Dockerfile`
- **Port Exposed**: 8000
- **Health Check**: Automatic via Dockerfile `HEALTHCHECK` directive
- **SSL**: Automatic Let's Encrypt with HTTP redirect
- **Build Context**: Full repository for shared library access

#### Environment Variable Flags
For all environment variables:
- **Is Build Variable?**: ❌ (Runtime variables)
- **Is Multiline?**: ❌ (Single-line values)
- **Is Literal?**: ❌ (Standard variable interpolation)

### Deployment Architecture

#### Service Communication
```
Internet → Traefik Reverse Proxy → Ingestion Service Container
                                     ↓
                              Future: Redpanda Message Bus
```

#### Container Configuration
- **Base Image**: `python:3.11-slim`
- **User**: Non-root execution (`appuser:appgroup`)
- **Resource Limits**: Not set (default container limits)
- **Health Check**: `/healthz` endpoint every 30s

### Environment Validation

#### Staging Environment
- **URL**: `http://yoows40k844kc8w880ks48o0.157.90.158.16.sslip.io`
- **Health Check**: `curl {URL}/healthz` should return 200
- **Environment**: Returns DEBUG-level logging
- **Purpose**: Feature validation before production

#### Production Environment
- **URL**: Auto-generated Coolify domain
- **Health Check**: `curl {URL}/healthz` should return 200
- **Environment**: Returns INFO-level logging
- **Purpose**: Live production workload

### Deployment Process

#### Automated Deployment (via GitHub Actions)
1. Code pushed to `main` branch
2. CI/CD pipeline runs tests
3. Webhook triggers Coolify deployment
4. Coolify pulls from Git repository
5. Docker build process executes
6. Health checks validate deployment
7. Service becomes available

#### Manual Validation Steps
1. **Health Check**: `curl {environment_url}/healthz`
2. **Environment Verification**: Check logs for correct LOG_LEVEL
3. **SSL Validation**: Access via HTTPS (when configured)
4. **Container Status**: Verify in Coolify dashboard

### Environment Parity

Both environments use:
- ✅ Identical Docker images
- ✅ Same health check configuration
- ✅ Same build process and dependencies
- ✅ Same container security settings
- ✅ Same SSL/TLS configuration
- ✅ Different only in environment variables

### Future Enhancements

#### Planned Additions
- [ ] Custom production domain configuration
- [ ] Resource limits and scaling settings
- [ ] Kafka broker connection configuration
- [ ] Prometheus metrics endpoint configuration
- [ ] Advanced health check parameters

#### Monitoring Integration (Future)
```bash
# Additional environment variables for monitoring
PROMETHEUS_ENABLED=true
METRICS_PORT=9090
SENTRY_DSN={environment_specific_dsn}
```

### Operational Procedures

#### Environment Health Check
```bash
# Check staging
curl -f http://yoows40k844kc8w880ks48o0.157.90.158.16.sslip.io/healthz

# Check production (update URL as needed)
curl -f {production_url}/healthz
```

#### Log Level Verification
Staging logs should show DEBUG messages, production should only show INFO and above.

#### Rolling Deployment Process
1. Changes deploy to staging automatically
2. Manual validation in staging
3. Same changes deploy to production automatically
4. Production health validation

### Security Considerations

#### Container Security
- Non-root user execution
- No secrets in environment variables
- Minimal runtime dependencies
- Regular base image updates

#### Network Security
- HTTPS-only access (when SSL configured)
- Internal service communication
- No exposed admin ports

### Troubleshooting

#### Common Issues
1. **Service Won't Start**: Check environment variables and Docker logs
2. **Health Check Fails**: Verify `/healthz` endpoint and container status
3. **SSL Issues**: Check Let's Encrypt certificate provisioning
4. **Build Failures**: Verify workspace dependencies and Docker build context

#### Validation Commands
```bash
# Test environment variable configuration
curl {environment_url}/healthz | jq

# Check SSL certificate
curl -I https://{domain} | grep -i ssl

# Verify environment differentiation
# Staging should have debug logs, production should have info logs
```

This configuration provides environment parity with appropriate differentiation for development and production workloads while maintaining security and operational best practices.
