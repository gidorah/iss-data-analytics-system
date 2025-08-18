# ISS Data Analytics System

A real-time telemetry platform that ingests ISS Lightstreamer data, validates and enriches it, publishes to a durable message bus, enables near-real-time analytics (initially a Pee-Bot that detects urination events and posts on Twitter), and persists events for future dashboards and analysis.

## 🎯 Business Objectives

- **BO-1:** Reliably ingest, validate, enrich, and deliver ISS telemetry with strict per-item ordering and no duplicates
- **BO-2:** Detect urination events in near real-time and post to Twitter with guardrails (cooldown and retries)
- **BO-3:** Persist events and support replay to enable future dashboards and analytics
- **BO-4:** Meet stated latency and throughput targets now (~70 msg/s) and scale to 10,000 msg/s
- **BO-5:** Provide operational visibility, error handling, and stability (metrics, health, backpressure)

## 🏗️ Architecture Overview

This system follows a microservices architecture with three core services:

- **Ingestion Service**: ISS Lightstreamer connection, validation, enrichment, and Kafka publishing
- **Pee-Bot Analytics Service**: Urination event detection with Twitter posting and replay capabilities
- **Event Storage**: Data persistence for analytics and dashboards

The platform uses Apache Kafka (via Redpanda) as the central message bus for durable, ordered telemetry transport.

## 📁 Workspace Structure

This project uses **uv workspaces** for monorepo management, providing fast dependency resolution and consistent versioning across services.

```
iss-data-analytics-system/
├── pyproject.toml                 # Workspace root configuration
├── uv.lock                        # Single lockfile for entire workspace
├── services/                      # Microservices
│   ├── ingestion/
│   │   ├── app/                   # FR-001 to FR-009: ISS data ingestion
│   │   │   ├── lightstreamer.py        # Persistent ISS connection
│   │   │   ├── validator.py            # Schema validation (FR-002)
│   │   │   ├── enricher.py             # Event ID + timestamp (FR-003)
│   │   │   ├── publisher.py            # Kafka publishing (FR-006)
│   │   │   └── main.py
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   ├── pee-bot/
│   │   ├── app/                   # FR-014 to FR-022: Analytics service
│   │   │   ├── detector.py             # Urination event detection (FR-015)
│   │   │   ├── twitter.py              # Twitter posting + jokes (FR-017, FR-021)
│   │   │   ├── replay.py               # Startup replay logic (FR-018)
│   │   │   └── main.py
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   └── event-storage/
│       ├── app/                   # FR-023, FR-024: Data persistence
│       │   ├── writer.py               # Event persistence
│       │   ├── query.py                # Time-window queries
│       │   └── main.py
│       ├── tests/
│       ├── Dockerfile
│       └── pyproject.toml
├── libs/                          # Shared libraries
│   ├── common/
│   │   ├── src/
│   │   │   └── iss_common/
│   │   │       ├── schemas/            # NFR-013: Versioned schemas
│   │   │       │   ├── telemetry.py
│   │   │       │   └── events.py
│   │   │       ├── kafka/             # FR-010 to FR-013: Message bus
│   │   │       │   ├── client.py
│   │   │       │   └── consumer.py
│   │   │       ├── observability/     # FR-025, NFR-011: Metrics + logging
│   │   │       │   ├── metrics.py
│   │   │       │   ├── logging.py
│   │   │       │   └── health.py
│   │   │       └── utils/
│   │   ├── tests/
│   │   └── pyproject.toml
│   └── test-utils/
│       ├── src/
│       │   └── iss_test_utils/    # Shared test utilities
│       │       ├── fixtures.py
│       │       └── mocks.py
│       ├── tests/
│       └── pyproject.toml
├── infrastructure/                # Not part of uv workspace
│   ├── kafka/
│   │   └── docker-compose.yml     # Redpanda setup
│   └── deployment/
│       └── coolify/               # VPS deployment configs
└── tools/                        # Development utilities
    ├── setup.sh                  # Environment setup
    ├── test-all.sh              # Run all tests
    └── lint.sh                  # Linting across workspace
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- Docker (for local Kafka/Redpanda)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd iss-data-analytics-system
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Start local infrastructure**
   ```bash
   docker-compose -f infrastructure/kafka/docker-compose.yml up -d
   ```

4. **Run services individually**
   ```bash
   # Ingestion service
   cd services/ingestion
   uv run python -m app.main
   
   # Pee-Bot analytics
   cd services/pee-bot
   uv run python -m app.main
   
   # Event storage
   cd services/event-storage
   uv run python -m app.main
   ```

## 🔧 Development

### Workspace Management

Add new workspace members to the root `pyproject.toml`:
```toml
[tool.uv.workspace]
members = [
    "services/*",
    "libs/*"
]
```

### Shared Dependencies

Common libraries are declared as workspace dependencies:
```toml
[project]
dependencies = [
    "iss-common",      # Workspace library
    "fastapi>=0.100.0" # External dependency
]

[tool.uv.sources]
iss-common = { workspace = true }
```

### Testing

```bash
# Run all tests
./tools/test-all.sh

# Test specific service
cd services/ingestion
uv run pytest

# Test with coverage
uv run pytest --cov=app
```

### Linting & Formatting

```bash
# Lint entire workspace
./tools/lint.sh

# Format code
uv run ruff format .
uv run ruff check --fix .
```

## 📊 Performance Targets

- **Current throughput**: ~70 messages/second
- **Design target**: 10,000 messages/second
- **P99 latency**: 
  - Ingestion to dashboard-ready: < 1 second
  - Ingestion to persistence: < 5 seconds
- **Pee-Bot posting**: Within 2 minutes (P95) of event detection

## 🔍 Observability

Each service exposes:
- **Health endpoint**: `GET /healthz`
- **Metrics endpoint**: `GET /metrics` (Prometheus format)
- **Structured logging**: JSON to stdout

Key metrics:
- Ingestion lag and throughput
- Queue depth and message rates
- Tweet success/failure rates
- Kafka consumer lag

## 🏢 Deployment

**Target platform**: Coolify-managed VPS (Hetzner)

**Components**:
- Services: Containerized FastAPI applications
- Message bus: Single-node Redpanda (Kafka-compatible)
- Monitoring: Prometheus + Grafana (containerized)

**CI/CD**: GitHub Actions for build, test, and deployment

## 📋 Requirements Traceability

| Functional Requirement | Implementation Location |
|------------------------|-------------------------|
| FR-001 to FR-009 | `services/ingestion/` |
| FR-010 to FR-013 | `libs/common/kafka/` + Infrastructure |
| FR-014 to FR-022 | `services/pee-bot/` |
| FR-023 to FR-024 | `services/event-storage/` |
| FR-025 to FR-026 | `libs/common/observability/` |

## 🎯 Current Phase Scope

**In Scope**:
- ISS telemetry ingestion with validation
- Kafka-based message transport
- Pee-Bot urination detection and Twitter posting
- Event persistence for future dashboards
- Observability and operational metrics

**Out of Scope**:
- Real-time user dashboards (future phase)
- ML forecasting beyond Pee-Bot (future phase)  
- Multi-region deployment
- Comprehensive data governance

## 📚 Documentation

- **High-level requirements**: `docs/system-solution/high-level-requirements.md`
- **Ingestion service architecture**: `ingestion-service/docs/system-solution/ingestion-service-architecture.md`
- **Service-specific READMEs**: Each service contains detailed implementation docs

## 🤝 Contributing

1. Follow the established workspace structure
2. Add new services under `services/`
3. Place shared utilities in `libs/common/`
4. Ensure all services have comprehensive tests
5. Update this README when adding new workspace members

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.