- **T001 - Confirm Requirements and Scope**
  - **Description:** Validate requirements, resolve open questions (topics/partitions/retention, Redpanda version and sizing, LS items/field mapping, metrics standards, TLS/allowlists), and finalize scope for the ingestion service and message bus.
  - **Dependencies:** None

- **T002 - Prepare Access, Repositories, and Environment**
  - **Description:** Establish Coolify/VPS access and readiness, create GitHub repo with Actions enabled and required secrets, verify environment setup, and configure SSL automation via Let's Encrypt.
  - **Dependencies:** T001

- **T003 - Baseline Architecture and Design**
  - **Description:** Define subscriber reconnect/resume behavior, non-blocking pipeline and backpressure policy, retry/circuit-breaker and graceful shutdown, event schema and deterministic event_id, schema versioning policy, security model for test endpoint and exposure, observability (metrics/logging), message bus topic and producer configuration (idempotence, acks, batching, compression, keying), and container/CI approach.
  - **Dependencies:** T001

- **T004 - Provision Message Bus on VPS**
  - **Description:** Set up a single-node Redpanda (Kafka API) on the VPS with localhost binding, configured data directory and retention, and enable metrics exposure.
  - **Dependencies:** T003

- **T005 - Configure Topics and Policies**
  - **Description:** Create `telemetry.raw.v1` with defined partitions, retention, cleanup policy, and verify topic configuration and retention behavior.
  - **Dependencies:** T004

- **T006 - Develop Core Ingestion Pipeline**
  - **Description:** Build Lightstreamer subscriber with reconnect/resume, validate/normalize payloads, enrich with deterministic event_id and ingest_ts, and implement a bounded non-blocking queue with backpressure.
  - **Dependencies:** T003

- **T007 - Integrate Event Publishing**
  - **Description:** Integrate confluent-kafka producer with idempotence and tuned timeouts/batching/compression, implement per-item keying by item_id, and surface delivery callbacks/metrics.
  - **Dependencies:** T006, T004

- **T008 - Add HTTP API and Operational Endpoints**
  - **Description:** Provide `POST /api/v1/ingest/test` for controlled injection, `GET /healthz` for liveness, and `GET /metrics` for Prometheus format.
  - **Dependencies:** T006

- **T009 - Apply Security and Configuration Management**
  - **Description:** Enforce Bearer token authentication for the test endpoint, secure exposure behind reverse proxy with automatic SSL certificates/IP allowlists, and implement environment-based configuration loading with secrets handling.
  - **Dependencies:** T008

- **T010 - Establish Observability**
  - **Description:** Emit structured JSON logs and instrument Prometheus metrics for ingestion rate, queue depth, latencies, publish results, retries, and reconnects; optionally surface Kafka client metrics.
  - **Dependencies:** T006

- **T011 - Add Reliability Controls and Graceful Shutdown**
  - **Description:** Implement retry with jitter and circuit breaker for transient failures and ensure producer flush and safe task cancellation on shutdown.
  - **Dependencies:** T007

- **T012 - Define and Execute Testing Strategy**
  - **Description:** Deliver unit tests (validation, event_id determinism, auth, config), integration tests (ingest enqueuing, publish/acks, per-item ordering, idempotence), reliability/performance tests (throughput baseline, backpressure 429 and subscriber pause, LS reconnects with circuit breaker, broker downtime and recovery), security tests (401/403, payload and timeout constraints), and publish test reports.
  - **Dependencies:** T006, T007, T008, T009, T011

- **T013 - Containerization and CI/CD Setup**
  - **Description:** Create Dockerfile for the FastAPI service and implement CI workflows to run tests and build/push the image, with deploy triggers.
  - **Dependencies:** T012

- **T014 - Staging Deployment and Smoke Testing**
  - **Description:** Deploy via Coolify to staging with health checks, SSL automation, and environment configuration, then run a smoke test to ingest a sample and verify the message in the Kafka topic.
  - **Dependencies:** T013, T005

- **T015 - Monitoring and Alerts Configuration**
  - **Description:** Configure Prometheus to scrape ingestion service and Redpanda metrics, and set alerts for queue depth high watermark, publish failures, broker disk usage, broker restarts, and reconnect churn.
  - **Dependencies:** T014

- **T016 - Production Release**
  - **Description:** Promote the image and configuration to production in Coolify with SSL certificate validation and execute a release validation with a documented rollback plan.
  - **Dependencies:** T015

- **T017 - Runbook and Operational Documentation**
  - **Description:** Publish operational runbook (startup/shutdown order, backup guidance, incident steps), consumer replay/time-seek instructions, and environment/configuration reference.
  - **Dependencies:** T016

- **T018 - Project Governance and PM Cadence**
  - **Description:** Establish weekly status check-ins with concise progress reports and maintain a risk register with owners and mitigations.
  - **Dependencies:** T001

- **T019 - High-Load Performance Validation**
  - **Description:** Execute synthetic high-load tests to evaluate throughput and P99 latency against the 10k msg/s design target; if constrained by the VPS, validate scaled configuration in a suitable environment and document findings.
  - **Dependencies:** T013
