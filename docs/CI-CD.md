# CI/CD Pipeline Documentation

This document describes the Continuous Integration and Continuous Deployment (CI/CD) pipeline for the FastAPI Shop Application.

## Overview

Our CI/CD pipeline is built using GitHub Actions and includes:

- ✅ **Automated Testing**: Unit and integration tests with coverage reporting
- ✅ **Code Quality**: Linting, formatting, and type checking
- ✅ **Security Scanning**: Vulnerability detection in dependencies and code
- ✅ **Docker Building**: Automated container image builds
- ✅ **Deployment**: Automated deployment to staging and production environments
- ✅ **Notifications**: Team notifications on deployment status

## Workflows

### 1. Main CI/CD Pipeline (`ci-cd.yml`)

**Triggers:**

- Push to `main` or `develop` branches
- Pull requests to `main` branch

**Jobs:**

1. **Test**: Run full test suite with PostgreSQL and Redis
2. **Lint**: Code quality checks (Black, isort, flake8, mypy)
3. **Security**: Security scanning (Bandit, Safety)
4. **Build**: Docker image build and push (main branch only)
5. **Deploy**: Automated deployment to staging/production
6. **Notify**: Team notifications

### 2. Pull Request Tests (`pr-tests.yml`)

**Triggers:**

- Pull request opened, synchronized, or reopened

**Features:**

- Fast feedback on PR quality
- Automated comments with test results
- Prevents merging broken code

### 3. Release Pipeline (`release.yml`)

**Triggers:**

- Git tags matching `v*.*.*` pattern

**Features:**

- Automated release creation
- Changelog generation
- Production deployment
- Version tagging

## Local Development

### Setup Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd fastapi-shop-app

# Set up development environment
make setup-dev

# Install pre-commit hooks
pre-commit install
```

### Available Make Commands

```bash
make help              # Show all available commands
make install           # Install dependencies
make test              # Run tests with coverage
make lint              # Run code linting
make format            # Format code
make security          # Run security scans
make docker-build      # Build Docker image
make docker-run        # Run with Docker Compose
make serve             # Run development server
```

### Running Tests

```bash
# Run all tests
make test

# Run specific test types
make test-unit         # Unit tests only
make test-integration  # Integration tests only

# Run tests with Docker
make docker-test

# Watch mode for development
make test-watch
```

### Code Quality

```bash
# Check code formatting
make format-check

# Format code
make format

# Run linting
make lint

# Run security scans
make security

# Run all quality checks
make check-all
```

## Environment Variables

### Required for CI/CD

Set these secrets in your GitHub repository:

```bash
DOCKER_USERNAME        # Docker Hub username
DOCKER_PASSWORD        # Docker Hub password/token
```

### Application Environment Variables

```bash
DATABASE_URL           # PostgreSQL connection string
JWT_SECRET_KEY         # JWT signing secret
REDIS_HOST            # Redis server host
REDIS_PORT            # Redis server port
REDIS_PASSWORD        # Redis password (optional)
DEBUG                 # Debug mode (0/1)
ENVIRONMENT           # Environment name (development/staging/production)
LOG_LEVEL             # Logging level (DEBUG/INFO/WARNING/ERROR)
```

## Deployment

### Staging Deployment

Automatic deployment to staging occurs when:

- Code is pushed to `develop` branch
- All tests pass
- Docker image builds successfully

### Production Deployment

Production deployment is triggered by:

- Creating a git tag with version format `v*.*.*`
- All tests and security checks pass
- Manual approval (if configured)

### Manual Deployment

```bash
# Create and push a release tag
git tag v1.2.3
git push origin v1.2.3

# This will trigger the release workflow
```

## Monitoring and Notifications

### Test Results

- Test coverage reports are uploaded to Codecov
- Test results are commented on pull requests
- Failed tests prevent merging

### Security

- Bandit scans for common security issues
- Safety checks for vulnerable dependencies
- Security reports are uploaded as artifacts

### Performance

- Docker image size optimization
- Cache utilization for faster builds
- Parallel job execution

## Troubleshooting

### Common Issues

1. **Tests failing locally but passing in CI**

   - Check environment variables
   - Ensure database is running
   - Verify Python version matches CI

2. **Docker build failures**

   - Check Dockerfile syntax
   - Verify all dependencies are listed
   - Test build locally first

3. **Security scan failures**
   - Update vulnerable dependencies
   - Add security exceptions if needed
   - Review Bandit findings

### Getting Help

1. Check workflow logs in GitHub Actions
2. Review error messages and stack traces
3. Ensure all required secrets are configured
4. Test locally with same environment as CI

## Best Practices

### Code Quality

- Write tests for all new features
- Maintain >80% code coverage
- Use type hints consistently
- Follow PEP 8 style guidelines

### Git Workflow

- Create feature branches from `develop`
- Use descriptive commit messages
- Squash commits before merging
- Tag releases with semantic versioning

### Security

- Never commit secrets or API keys
- Regularly update dependencies
- Review security scan results
- Use environment variables for configuration

## Configuration Files

- `.github/workflows/`: GitHub Actions workflows
- `pytest.ini`: Test configuration
- `pyproject.toml`: Tool configuration (Black, isort, mypy)
- `.pre-commit-config.yaml`: Pre-commit hooks
- `Makefile`: Development commands
- `docker-compose.test.yml`: Test environment

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run quality checks: `make check-all`
5. Commit and push your changes
6. Create a pull request

The CI/CD pipeline will automatically:

- Run tests on your pull request
- Check code quality and security
- Provide feedback via comments
- Block merging if checks fail
