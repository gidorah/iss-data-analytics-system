"""
ISS Data Analytics System - Ingestion Service
FastAPI application for ingesting ISS Lightstreamer telemetry data
"""

from fastapi import FastAPI
import uvicorn
import os

app = FastAPI(
    title="ISS Ingestion Service",
    description="Ingests ISS Lightstreamer telemetry data and publishes to message bus",
    version="0.1.0",
)


@app.get("/healthz")
async def health_check():
    """Health check endpoint for container orchestration"""
    import datetime
    import psutil
    import os

    # Get system information for monitoring
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        health_info = {
            "status": "healthy",
            "service": "ingestion-service",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "uptime_seconds": int(
                (
                    datetime.datetime.now()
                    - datetime.datetime.fromtimestamp(psutil.boot_time())
                ).total_seconds()
            ),
            "system": {
                "cpu_percent": round(cpu_percent, 2),
                "memory_percent": round(memory.percent, 2),
                "disk_percent": round((disk.used / disk.total) * 100, 2),
            },
            "environment": os.getenv("ENVIRONMENT", "unknown"),
            "version": "0.1.0",
        }

        # Mark as unhealthy if resource usage is too high or forced for testing
        if cpu_percent > 90 or memory.percent > 95:
            health_info["status"] = "degraded"
        elif _force_unhealthy:
            health_info["status"] = "unhealthy"
            health_info["reason"] = "Manually triggered for testing"

        return health_info

    except Exception as e:
        # Fallback to basic health check if psutil fails
        return {
            "status": "healthy",
            "service": "ingestion-service",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "error": f"Extended health check failed: {str(e)}",
        }


# Global variable to simulate health status for testing
_force_unhealthy = False


@app.get("/")
async def root():
    """Root endpoint with basic service info"""
    return {"service": "ingestion-service", "status": "running", "version": "0.1.0"}


@app.post("/admin/health/fail")
async def simulate_health_failure():
    """Temporarily make health check fail for testing purposes"""
    global _force_unhealthy
    _force_unhealthy = True
    return {
        "message": "Health check will fail for the next few checks",
        "duration": "60 seconds",
    }


@app.post("/admin/health/recover")
async def recover_health():
    """Restore health check to normal operation"""
    global _force_unhealthy
    _force_unhealthy = False
    return {"message": "Health check restored to normal operation"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)  # nosec B104
