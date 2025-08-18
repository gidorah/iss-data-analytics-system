### 1. Executive Summary

This project establishes a real-time telemetry platform that ingests ISS Lightstreamer data, validates and enriches it, publishes to a durable message bus, enables near-real-time analytics (initially a Pee-Bot that detects urination events and posts on Twitter), and persists events for future dashboards and analysis. The initial phase delivers ingestion, Kafka-based transport, the Pee-Bot analytics service with replay and cooldown safeguards, and foundational storage aligned to stated latency, throughput, ordering, and durability objectives.

### 2. Business Objectives

- **BO-1:** Reliably ingest, validate, enrich, and deliver ISS telemetry with strict per-item ordering and no duplicates.
- **BO-2:** Detect urination events in near real-time and post to Twitter with guardrails (cooldown and retries).
- **BO-3:** Persist events and support replay to enable future dashboards and analytics.
- **BO-4:** Meet stated latency and throughput targets now (~70 msg/s) and scale to 10,000 msg/s.
- **BO-5:** Provide operational visibility, error handling, and stability (metrics, health, backpressure).

### 3. User Personas and Stories

- **Persona: Platform Operator**
  - **Description:** Operates the telemetry platform; monitors health, lag, and stability; reacts to incidents.
  - **User Stories:**
    - "As a Platform Operator, I can view ingestion lag, queue depth, publish/consume rates, and health so I can maintain SLAs."
    - "As a Platform Operator, I can throttle or circuit-break ingestion when downstream is unhealthy to stabilize the system."

- **Persona: Analytics Service Developer**
  - **Description:** Builds streaming consumers using the message bus; needs ordered, replayable data.
  - **User Stories:**
    - "As an Analytics Developer, I can subscribe to telemetry streams and replay from offsets to validate and iterate on logic."
    - "As an Analytics Developer, I can rely on strict per-item ordering to implement windowed computations."

- **Persona: Pee-Bot Maintainer**
  - **Description:** Owns the Pee-Bot service; ensures correct detection, posting reliability, and guardrails.
  - **User Stories:**
    - "As a Pee-Bot Maintainer, I can auto-replay from the last decision time on startup so missed events are detected."
    - "As a Pee-Bot Maintainer, I can see errors and retry outcomes so I can troubleshoot posting issues."

- **Persona: Data Analyst [Inference]**
  - **Description:** Uses persisted events to build dashboards and metrics (e.g., pee per day, tank levels). Justification: The source states saving events for future dashboards.
  - **User Stories:**
    - "As a Data Analyst, I can query persisted urination events by time window so I can build trend dashboards."

### 4. Functional Requirements (FR)

- **Feature: Ingestion Service**
  - **FR-001:** The system shall maintain a persistent connection to the ISS Lightstreamer ISSLIVE feed and subscribe to configured items. (BO: BO-1, BO-4)
  - **FR-002:** The system shall validate incoming messages against a defined schema and reject malformed data. (BO: BO-1, BO-5)
  - **FR-003:** The system shall enrich each message with a unique event ID and an ingestion timestamp. (BO: BO-1, BO-3, BO-5)
  - **FR-004:** The system shall provide an HTTP endpoint to manually inject test messages for validation and troubleshooting. (BO: BO-5)
  - **FR-005:** The system shall apply bounded backpressure, retries with jitter, and circuit-breakers for stability. (BO: BO-5, BO-4)
  - **FR-006:** The system shall publish validated, enriched events to the message bus. (BO: BO-1)
  - **FR-007:** The system shall expose process health and ingestion lag metrics. (BO: BO-5)
  - **FR-008:** The system shall preserve strict per-telemetry-item ordering end-to-end. (BO: BO-1)
  - **FR-009:** The system shall ensure that no duplicate events are delivered downstream or persisted. (BO: BO-1)

- **Feature: Message Bus**
  - **FR-010:** The platform shall provide an Apache Kafka event bus as the durable transport for telemetry and derived events. (BO: BO-1, BO-4)
  - **FR-011:** Consumers shall be able to replay from stored offsets to reprocess historical data. (BO: BO-3)
  - **FR-012:** The bus shall guarantee strict ordering to consumers for messages associated with the same telemetry item identifier. (BO: BO-1, BO-4)
  - **FR-013:** Consumers shall be able to seek by timestamp to begin replay from a chosen point in time. [Inference: required to start from the last decision time] (BO: BO-3)

- **Feature: Pee-Bot Analytics Service**
  - **FR-014:** The service shall subscribe to the urine tank level stream from the message bus. (BO: BO-2)
  - **FR-015:** The service shall detect urination events using a sliding window over tank level changes. (BO: BO-2)
  - **FR-016:** The service shall enforce a 5-minute cooldown between posts. (BO: BO-2)
  - **FR-017:** The service shall attempt to post to Twitter up to 3 times on failure and shall log all errors. (BO: BO-2, BO-5)
  - **FR-018:** On startup, the service shall obtain the timestamp of the latest urination decision and replay from the bus to detect any missed events. (BO: BO-2, BO-3)
  - **FR-019:** The service shall persist each detected urination event for future dashboards. (BO: BO-3)
  - **FR-020:** The service shall expose a health endpoint and metrics (e.g., detection rate, tweet success rate, retry counts). (BO: BO-5)
  - **FR-021:** The service shall generate a joke/haiku for each detected event and post it to Twitter. (BO: BO-2)
  - **FR-022:** The service shall not enforce a maximum daily post limit. (BO: BO-2)

- **Feature: Data Lake / Event Storage**
  - **FR-023:** The platform shall configure hot data retention in Kafka topics for 1 week and retain cold data for at least 1 month in the data lake (initial targets). (BO: BO-3)
  - **FR-024:** The platform shall support querying persisted urination events by time window. [Inference: needed for stated dashboard use] (BO: BO-3)

- **Feature: Observability and Operations**
  - **FR-025:** Services shall emit structured logs and error traces; the Pee-Bot service shall integrate with Sentry for error monitoring. (BO: BO-5)
  - **FR-026:** The platform shall record and expose ingestion lag, in-process queue depth, publish rate, and consumer lag as metrics. (BO: BO-5)

### 5. Non-Functional Requirements (NFR)

- **Performance**
  - **NFR-001:** The platform shall be designed and tested to handle 10,000 messages per second end-to-end. (BO: BO-4)
  - **NFR-002:** P99 end-to-end latency from ingestion to dashboard-usable data shall be < 1 second; P99 latency to persistence sinks shall be < 5 seconds. (BO: BO-4)
  - **NFR-003:** Pee-Bot shall post within 2 minutes (P95) of the underlying event detection. (BO: BO-2)
  - **NFR-014:** The ingestion path shall be non-blocking with bounded concurrency sufficient to sustain 10,000 messages per second without violating the latency targets in NFR-002. [Inference] (BO: BO-4, BO-5)

- **Reliability and Integrity**
  - **NFR-004:** The platform shall preserve strict per-telemetry-item ordering and tolerate 0 duplicates in delivered or persisted events. (BO: BO-1, BO-3)
  - **NFR-005:** Kafka topics (hot data) shall retain messages for at least 7 days to support consumer replay; cold storage shall retain events for at least 30 days. (BO: BO-3)
  - **NFR-006:** Monthly service availability for ingestion and Pee-Bot shall be at least 99.5%. [Inference: initial target suitable for a VPS-hosted system] (BO: BO-5)

- **Scalability**
  - **NFR-007:** The platform shall scale horizontally to meet throughput and latency targets without downtime during scaling operations. [Inference] (BO: BO-4)

- **Security**
  - **NFR-008:** All inter-service and external communications shall be encrypted in transit (TLS). [Inference] (BO: BO-5)
  - **NFR-009:** Secrets (e.g., Twitter tokens, Kafka credentials) shall be stored securely with least-privilege access. [Inference] (BO: BO-5)
  - **NFR-010:** The test ingestion endpoint shall require authentication and authorization. [Inference] (BO: BO-5)

- **Observability and Maintainability**
  - **NFR-011:** Services shall expose metrics for ingestion lag, queue depth, message rates, error rates, tweet success/failure, and retry counts via a standard metrics endpoint. [Inference] (BO: BO-5)
  - **NFR-012:** The Pee-Bot detection logic shall have automated tests (e.g., unit tests) covering sliding-window behavior and cooldown handling. [Inference: tests referenced in tech stack] (BO: BO-5)

- **Data Management**
  - **NFR-013:** Event schemas shall be versioned and maintain backward compatibility to mitigate schema drift. [Inference: risk called out] (BO: BO-1, BO-3)

### 6. Assumptions

- **A-1:** Access to the ISS Lightstreamer ISSLIVE adapter and the list of item IDs to subscribe to will be provided.
- **A-2:** Apache Kafka is available (managed or self-hosted) and reachable from the ingestion and analytics services.
- **A-3:** The message bus is the system of record for replay; Lightstreamer may not retain a history. (Source notes uncertainty.)
- **A-4:** Twitter (X) API access and credentials will be provisioned and allowed for automated posting without manual approval.
- **A-5:** A Sentry project and DSN will be available for error monitoring for Pee-Bot.
- **A-6:** The initial deployment target is a Coolify-managed VPS; networking and TLS termination will be available. [Inference]
- **A-7:** External telemetry schemas (units, bounds) are controlled externally; only validation within known constraints will be applied.
- **A-8:** Lightstreamer fires update events only on data changes; no continuous stream.

### 7. Out of Scope

- **OOS-1:** Real-time user dashboards and their front-end implementation (planned for future).
- **OOS-2:** ML forecasting and advanced analytics beyond the Pee-Bot service (future phase).
- **OOS-3:** Manual approval queue for Pee-Bot posts (explicitly not needed).
- **OOS-4:** Native mobile applications and multilingual UX.
- **OOS-5:** Comprehensive data governance (e.g., full schema registry rollout) beyond versioning requirements stated here. [Inference]

### 8. Clarifying Questions

- **Business**
  - **Q-1:** Confirm KPIs: What are the success metrics for Pee-Bot (e.g., detection precision/recall targets, acceptable false positives)?
  - **Q-2:** Confirm event retention beyond the starter targets (hot 1 week, cold 1 month). Any compliance or data residency constraints?

- **Technical**
  - **Q-3:** Does Lightstreamer retain any replayable history? If yes, for how long and via which API?
  - **Q-4:** Define Kafka topology: cluster availability, replication, partitioning strategy, and topic naming conventions.
  - **Q-5:** Which database will be used for the data lake/archival (ClickHouse, TimescaleDB, InfluxDB)? Any managed offering preferred?
  - **Q-6:** Provide the authoritative list of Lightstreamer items (e.g., urine tank level) and field mapping to the event schema.
  - **Q-7:** Twitter API version, rate limits, content policy constraints, and required posting formats.
  - **Q-8:** Confirm required metrics standard (e.g., format and collection method) and alerting thresholds for lag, errors, and tweet failures.
  - **Q-9:** Confirm security posture: TLS termination point, secret storage mechanism, and access controls for the test ingestion endpoint.

- **User Experience**
  - **Q-10:** For future dashboards, is SSE sufficient or are WebSockets required for client-side filtering and interactivity?
  - **Q-11:** Any content moderation or brand guidelines for Pee-Bot jokes/haikus (e.g., language restrictions)?
