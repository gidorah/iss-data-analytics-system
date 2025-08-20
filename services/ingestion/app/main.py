"""
ISS Data Analytics System - Ingestion Service
FastAPI application for ingesting ISS Lightstreamer telemetry data
"""

import datetime
import os

import psutil
import uvicorn
from fastapi import FastAPI

app = FastAPI(
    title="ISS Ingestion Service",
    description="Ingests ISS Lightstreamer telemetry data and publishes to message bus",
    version="0.1.0",
)


@app.get("/healthz")
async def health_check():
    """Health check endpoint for container orchestration"""

    # Get system information for monitoring
    try:
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk_usage_percent = psutil.disk_usage("/").percent

        health_info = {
            "status": "healthy",
            "service": "ingestion-service",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat() + "Z",
            "uptime_seconds": int(
                (
                    datetime.datetime.now(datetime.timezone.utc)
                    - datetime.datetime.fromtimestamp(
                        psutil.boot_time(), tz=datetime.timezone.utc
                    )
                ).total_seconds()
            ),
            "system": {
                "cpu_percent": round(cpu_percent, 2),
                "memory_percent": round(memory.percent, 2),
                "disk_percent": round(disk_usage_percent, 2),
            },
            "environment": os.getenv("ENVIRONMENT", "unknown"),
            "version": "0.1.0",
        }

        # Mark as unhealthy if resource usage is too high or forced for testing
        if cpu_percent > 90 or memory.percent > 95 or disk_usage_percent > 80:
            health_info["status"] = "degraded"

        return health_info

    except Exception as e:
        # Fallback to basic health check if psutil fails
        return {
            "status": "healthy",
            "service": "ingestion-service",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat() + "Z",
            "error": f"Extended health check failed: {str(e)}",
        }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)  # nosec B104
