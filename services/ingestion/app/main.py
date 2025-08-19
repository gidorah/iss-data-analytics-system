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
    return {"status": "healthy", "service": "ingestion-service"}


@app.get("/")
async def root():
    """Root endpoint with basic service info"""
    return {"service": "ingestion-service", "status": "running", "version": "0.1.0"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)  # nosec B104
