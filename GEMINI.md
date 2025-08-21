# Gemini Code Assistant Context: ISS Data Analytics System

This document provides a comprehensive overview of the ISS Data Analytics System project for the Gemini Code Assistant. It covers the project's purpose, architecture, key technologies, and development conventions.

## 1. Project Overview

This is a Python-based, real-time telemetry platform that ingests data from the International Space Station (ISS), processes it through a microservices architecture, and enables near-real-time analytics.

- **Purpose**: To reliably ingest, validate, enrich, and analyze ISS telemetry data. A key feature is the "Pee-Bot," which detects specific events and posts notifications to Twitter.
- **Architecture**: The system is a monorepo containing multiple microservices (`ingestion`, `pee-bot`, `event-storage`) and shared libraries (`common`, `test-utils`). It uses a message bus (Kafka) for communication between services.
- **Key Technologies**:
    - **Backend**: Python 3.11, FastAPI
    - **Package Management**: `uv` with workspace support
    - **Message Bus**: Redpanda (Kafka-compatible)
    - **Deployment**: Docker, Coolify
    - **CI/CD**: GitHub Actions
    - **Code Quality**: Ruff, Mypy, Bandit

## 2. Building and Running

The project uses `uv` for dependency management and `docker-compose` for running local infrastructure.

### Setup

1.  **Install Dependencies**: Install all main and development dependencies from the workspace `uv.lock` file.
    ```bash
    uv sync --extra dev
    ```

2.  **Install Pre-commit Hooks**: Set up git hooks to automate linting and formatting before commits.
    ```bash
    uv run pre-commit install
    ```

3.  **Start Local Infrastructure**: Run the local Redpanda (Kafka) message broker using Docker.
    ```bash
    docker-compose -f infrastructure/kafka/docker-compose.yml up -d
    ```

### Running Services

Services are designed to be run individually from their respective directories.

```bash
# Example: Run the Ingestion service
cd services/ingestion
uv run python -m app.main
```

### Running Tests

- **Run all tests** across the entire workspace:
  ```bash
  ./tools/test-all.sh
  ```
- **Run tests for a specific service**:
  ```bash
  # Example for the ingestion service
  cd services/ingestion
  uv run pytest
  ```
- **Run tests with coverage**:
  ```bash
  uv run pytest --cov=app
  ```

## 3. Development Conventions

### Code Style & Quality

The project enforces a strict code style and quality standard using a combination of tools, configured in `.pre-commit-config.yaml` and `pyproject.toml`.

- **Linting & Formatting**: `ruff` is used for both linting and formatting. To check the entire project, run:
  ```bash
  ./tools/lint.sh
  ```
  Or run the commands individually:
  ```bash
  uv run ruff check .
  uv run ruff format --check .
  ```
- **Type Checking**: `mypy` is used for static type checking.
  ```bash
  uv run mypy services/ libs/ --ignore-missing-imports
  ```
- **Security Analysis**: `bandit` is used to find common security issues.
  ```bash
  uv run bandit -r services/ libs/
  ```

### CI/CD and Deployment

The project uses a branch-based deployment strategy automated with GitHub Actions.

- **Branches**:
    - `development`: All feature development happens in branches off `main`.
    - `staging`: A pre-production branch. Merging a feature branch here deploys it to the **Staging** environment.
    - `main`: The production branch. Merging `staging` into `main` deploys the code to the **Production** environment.
- **CI Pipeline (`pr-validation.yml`)**: Pull requests to `staging` and `main` trigger a validation workflow that runs linting, formatting checks, type checking, security scans, and unit tests.
- **Deployment**: Deployments are handled by Coolify, triggered by webhooks on pushes to the `staging` and `main` branches. The architecture is detailed in `docs/system-solution/devops-architecture.md`.

### Workspace Management

The monorepo is managed as a `uv` workspace.

- **Members**: Services and libraries are defined as members in the root `pyproject.toml`.
- **Dependencies**: Shared libraries (e.g., `iss-common`) are referenced as workspace dependencies in the `pyproject.toml` files of individual services.
