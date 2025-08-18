# Contributing to ISS Data Analytics System

Thank you for your interest in contributing to the ISS Data Analytics System! This document provides guidelines for contributing to this project.

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- Docker (for local Kafka/Redpanda)
- Git

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/[your-username]/iss-data-analytics-system.git
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

4. **Run tests to verify setup**
   ```bash
   ./tools/test-all.sh
   ```

## 🔄 Development Workflow

### Branch Naming Convention

Use descriptive branch names with the following prefixes:
- `feature/` - New features or enhancements
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test improvements

Examples:
- `feature/add-ssl-support`
- `fix/ingestion-memory-leak`
- `docs/update-deployment-guide`

### Code Review Process

1. **Create a Pull Request**
   - Push your branch to your fork
   - Create a PR against the `main` branch
   - Use a descriptive title and detailed description
   - Link any related issues

2. **PR Requirements**
   - All CI checks must pass
   - At least one approving review required
   - No conflicts with the base branch
   - All conversations must be resolved

3. **Review Criteria**
   - Code follows project conventions
   - Tests cover new functionality
   - Documentation is updated if needed
   - Performance impact is considered

### Commit Message Guidelines

Use conventional commit format:
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types:
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `style` - Code style changes (formatting, etc.)
- `refactor` - Code refactoring
- `test` - Adding or updating tests
- `chore` - Maintenance tasks

Examples:
```
feat(ingestion): add SSL certificate validation
fix(pee-bot): resolve Twitter API rate limiting
docs(readme): update deployment instructions
```

## 🏗️ Project Structure

### Workspace Organization

This project uses **uv workspaces** for monorepo management:

```
services/          # Microservices
├── ingestion/     # ISS telemetry ingestion
├── pee-bot/       # Analytics and Twitter posting
└── event-storage/ # Data persistence

libs/              # Shared libraries
├── common/        # Common utilities and schemas
└── test-utils/    # Shared test utilities

infrastructure/    # Deployment and infrastructure
tools/            # Development utilities
```

### Adding New Services

1. Create service directory under `services/`
2. Follow the existing structure (app/, tests/, pyproject.toml, Dockerfile)
3. Add to workspace in root `pyproject.toml`
4. Update main README with service description

### Shared Libraries

- Place reusable code in `libs/common/`
- Add workspace dependency in service's `pyproject.toml`
- Follow the established module structure

## ✅ Code Quality Standards

### Testing Requirements

- **Unit tests**: All new code must have unit tests
- **Integration tests**: Required for API endpoints and external integrations
- **Test coverage**: Maintain >85% coverage for new code
- **Performance tests**: Include for performance-critical paths

### Code Style

- **Formatter**: Use `ruff format`
- **Linter**: Use `ruff check`
- **Type hints**: Required for all public functions
- **Documentation**: Docstrings for all public classes and functions

### Running Quality Checks

```bash
# Format code
uv run ruff format .

# Check linting
uv run ruff check .

# Run all tests
./tools/test-all.sh

# Check type hints
uv run mypy services/ingestion/app/

# Test with coverage
uv run pytest --cov=app --cov-report=term-missing
```

## 🔒 Security Guidelines

### Sensitive Data

- **Never commit secrets** to the repository
- Use environment variables for configuration
- Mask secrets in logs and error messages
- Follow principle of least privilege

### Dependencies

- Keep dependencies up to date
- Review security advisories for new dependencies
- Use pinned versions in production

### API Security

- Validate all input data
- Implement proper authentication/authorization
- Use HTTPS in production
- Rate limit external-facing endpoints

## 📊 Performance Considerations

### Current Targets

- **Throughput**: ~70 msg/s (current), 10k msg/s (design target)
- **Latency**: P99 < 200ms for ingestion pipeline
- **Memory**: Efficient memory usage, no leaks
- **CPU**: Minimize blocking operations

### Performance Testing

- Include performance tests for critical paths
- Monitor resource usage in tests
- Profile code for bottlenecks
- Consider async/await patterns for I/O

## 📝 Documentation

### Requirements

- Update relevant documentation for changes
- Include code examples where helpful
- Keep README.md current with workspace changes
- Document API changes in service READMEs

### Documentation Locations

- **Main README**: Project overview and getting started
- **Service READMEs**: Service-specific documentation
- **Architecture docs**: `docs/system-solution/`
- **API docs**: Auto-generated from FastAPI

## 🐛 Issue Reporting

### Bug Reports

Include:
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Relevant logs or error messages

### Feature Requests

Include:
- Clear description of the feature
- Use case and business justification
- Proposed implementation approach
- Any breaking changes

## 🎯 Development Priorities

### Current Focus Areas

1. **Reliability**: Error handling, retries, circuit breakers
2. **Observability**: Metrics, logging, health checks
3. **Performance**: Throughput optimization, latency reduction
4. **Security**: Input validation, secret management

### Future Enhancements

- Real-time dashboards
- ML-based analytics beyond Pee-Bot
- Multi-region deployment
- Advanced data governance

## 🤝 Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the issue, not the person
- Help create a welcoming environment

### Communication

- Use GitHub issues for bug reports and feature requests
- Use pull request comments for code-specific discussions
- Be clear and concise in communications
- Ask questions if something is unclear

## 📞 Getting Help

- **Issues**: Create a GitHub issue for bugs or questions
- **Documentation**: Check README and service-specific docs
- **Architecture**: Review `docs/system-solution/` for design context

Thank you for contributing to the ISS Data Analytics System! 🚀