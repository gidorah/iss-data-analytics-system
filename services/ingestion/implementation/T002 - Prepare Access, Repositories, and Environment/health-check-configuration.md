# Health Check Configuration - Task 2.5.4

## Overview

This document details the health check and monitoring configuration for the ISS Data Analytics System Ingestion Service deployed via Coolify. The implementation follows the requirements from T002-FR08 and provides comprehensive service monitoring.

## Health Check Implementation

### Application Layer Health Check

**Endpoint**: `/healthz`
- **URL**: `http://yoows40k844kc8w880ks48o0.157.90.158.16.sslip.io/healthz`
- **Method**: GET
- **Response Format**: JSON
- **Expected Response**:
  ```json
  {
    "status": "healthy",
    "service": "ingestion-service"
  }
  ```
- **Response Time**: ~160ms (validated)
- **HTTP Status**: 200 OK

### Container Layer Health Check

**Docker HEALTHCHECK Configuration** (services/ingestion/Dockerfile:64-66):
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/healthz || exit 1
```

**Parameters**:
- **Interval**: 30 seconds between health checks
- **Timeout**: 10 seconds maximum wait time per check
- **Start Period**: 30 seconds grace period after container start
- **Retries**: 3 consecutive failures before marking unhealthy
- **Command**: `curl -f http://localhost:8000/healthz`

## Coolify Platform Configuration

### Required Coolify Settings

1. **Health Check Configuration**:
   - Health Check URL: `/healthz`
   - Health Check Port: `8000`
   - Check Interval: `30 seconds`
   - Timeout: `10 seconds`
   - Failure Threshold: `3 consecutive failures`
   - Start Period: `30 seconds`

2. **Container Restart Policy**:
   - Restart Policy: `unless-stopped` or `always`
   - Automatic restart on health check failure: `enabled`
   - Maximum restart attempts: `3-5 attempts`

3. **Resource Limits** (per design specifications):
   - CPU Limit: `0.5 cores (500m)`
   - Memory Limit: `512MB`
   - Memory Reservation: `256MB`

## Monitoring Parameters

### Resource Monitoring

**CPU Monitoring**:
- Alert threshold: CPU usage > 80% for 5 minutes
- Critical threshold: CPU usage > 95% for 2 minutes

**Memory Monitoring**:
- Alert threshold: Memory usage > 90% for 2 minutes
- Critical threshold: Memory usage > 95% for 1 minute

**Container Health Monitoring**:
- Monitor container restart events
- Track health check failure patterns
- Alert on repeated health check failures

### Logging Configuration

**Log Collection**:
- Container logs collected via Coolify
- Log retention: 7-14 days (recommended)
- Log format: JSON structured logs to stdout

**Key Log Events**:
- Application startup and shutdown
- Health check requests and responses
- Error conditions and exceptions
- Resource usage warnings

## Validation Results

### Health Check Functionality Test

**Test Date**: August 20, 2025
**Test Results**:
- ✅ Health endpoint responds correctly: `{"status":"healthy","service":"ingestion-service"}`
- ✅ HTTP Status Code: 200 OK
- ✅ Response Time: 0.161202s (within 10s timeout)
- ✅ Service endpoint accessible: `http://yoows40k844kc8w880ks48o0.157.90.158.16.sslip.io/healthz`
- ✅ Root endpoint operational: `{"service":"ingestion-service","status":"running","version":"0.1.0"}`

### Container Health Check Test

**Docker Health Check Status**:
- Container HEALTHCHECK directive properly configured
- Health check command: `curl -f http://localhost:8000/healthz`
- Expected behavior: Container marked unhealthy after 3 consecutive failures
- Automatic restart: Configured via Coolify restart policy

## Troubleshooting Guide

### Common Health Check Issues

1. **Health Check Endpoint Not Responding**:
   - Verify service is running: `curl http://service-url/`
   - Check container logs for application errors
   - Verify network connectivity to container

2. **Health Check Timing Out**:
   - Current timeout: 10 seconds (should be sufficient)
   - Check for application performance issues
   - Monitor resource usage (CPU/memory)

3. **Container Restart Loop**:
   - Check health check failure patterns
   - Review application startup logs
   - Verify resource limits are appropriate

### Monitoring Checklist

**Daily Monitoring**:
- [ ] Service health status in Coolify dashboard
- [ ] Container restart events (should be rare)
- [ ] Resource usage trends (CPU/memory)

**Weekly Monitoring**:
- [ ] Health check response time trends
- [ ] Error rate analysis from logs
- [ ] Resource optimization opportunities

## Integration with Task Requirements

### T002-FR08 Compliance
- ✅ Service health checks configured and operational
- ✅ Monitoring parameters defined and implemented
- ✅ Automatic restart on failure configured
- ✅ Resource limits and monitoring established

### T002-NR02 Compliance (Reliability Requirements)
- ✅ 99.9% uptime expectation supported via health monitoring
- ✅ Automatic recovery through container restart
- ✅ Performance monitoring within acceptable thresholds

## Next Steps

1. **Phase 2.5.5**: Configure environment-specific deployment settings
2. **Phase 2.5.6**: Create integration test for Coolify deployment validation
3. **Future Enhancement**: Integrate with Prometheus/Grafana for advanced monitoring

## Security Considerations

- Health check endpoint exposed but provides minimal information
- No sensitive data exposed in health check response
- Container runs as non-root user (appuser:appgroup)
- Resource limits prevent resource exhaustion attacks

This health check configuration provides robust monitoring foundation for the ingestion service while maintaining security and performance requirements.
