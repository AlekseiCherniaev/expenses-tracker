# Expenses Tracker API

A **expense management system** built with **FastAPI**, designed following **Clean Architecture** principles and a full **observability stack**.  
It provides a backend setup with OAuth2 authentication, tracing, profiling, caching, and modular domain-driven structure.

**Fully Deployed & Live**: The entire infrastructure is deployed on **Yandex Cloud** using Docker Compose, including both backend and frontend services. You can explore the live application at:  
**[https://expenses-tracker.online](https://expenses-tracker.online)**

**Frontend Repository**: The React-based frontend is available at:  
**[https://github.com/AlekseiCherniaev/expences-tracker-frontend](https://github.com/AlekseiCherniaev/expences-tracker-frontend)**

---

## Features

- **Clean Architecture** — strict separation of concerns between layers:
  - `domain` (Entities, Repositories, Services)
  - `application` (Use Cases, DTOs, Interfaces)
  - `infrastructure` (APIs, Database, Security, Monitoring)
- **Unit of Work Pattern (UoW)** for transactional integrity
- **Repository Pattern** for abstracting persistence logic
- **DTOs** to isolate application logic from infrastructure
- **Dependency Inversion** through interfaces
- **Domain-Driven Design (DDD)** entities with explicit business logic
- **Asynchronous FastAPI** stack with `asyncpg` + `SQLAlchemy [asyncio]`
- **OAuth2 authentication** with Google & GitHub integrations
- **Email verification and password reset flows**
- **JWT access & refresh tokens**
- **Profiling and metrics endpoints** for performance insights
- **Structured logging** with `structlog` and Sentry integration
- **Distributed tracing** using OpenTelemetry
- **Caching** with Redis
- **MinIO** for S3-compatible object storage (avatars, files)
- **Containerized environment** via Docker Compose
- **Continuous Integration (CI) and Continuous Deployment (CD)** pipelines using **GitHub Actions**:
  - **CI Workflow:** runs on every push or PR to `master`/`dev`, performing linting (Ruff, pre-commit), static type checks (mypy), and running tests with pytest  
  - **CD Workflow:** automatically builds and pushes Docker images to Docker Hub on successful CI runs, then deploys to VPS via SSH (using `appleboy/ssh-action`)
  - Database migrations are automatically applied after deployment (`alembic upgrade head`)
- **Nginx** Configuration with:
  - **SSL/TLS termination** — with Let's Encrypt certificates
  - **Rate limiting** — (5 requests/second per IP for API endpoints)
  - **Security headers** — (HSTS, CSP, X-Frame-Options, etc.)
  - **Static file caching** — with optimized expiration headers
  - **Reverse proxy** — for API, MinIO, Grafana, and Prometheus
- **Automated SSL Certificate Management** with Certbot:
  - **Initial certificate issuance** — for multiple subdomains
  - **Automatic certificate renewal** — checks every 12 hours
- **Full observability stack:**
  - **Prometheus** — metrics collection
  - **Loki** — log aggregation
  - **Tempo** — distributed tracing
  - **Grafana** — visualization and dashboards
- **Comprehensive Testing Suite:**
  - **Unit Tests** — Domain entities, business logic, and pure functions
  - **Integration Tests** — Database repositories, external services, and use cases
  - **End-to-End Tests** — Full API workflows and user scenarios

---

## Tech Stack

**Backend Framework:**
- FastAPI  
- Uvicorn  

**Database:**
- PostgreSQL (Async)  
- SQLAlchemy (Async ORM)  
- Alembic for migrations  

**Caching & Queueing:**
- Redis  

**File Storage:**
- MinIO (S3-compatible)

**Authentication & Security:**
- JWT (Access/Refresh tokens)
- Authlib for OAuth2 (Google, GitHub)
- bcrypt for password hashing
- fastapi-mail for email communication

**Observability:**
- Prometheus — metrics  
- Grafana — dashboards  
- Loki — centralized logs  
- Tempo — distributed traces  
- Pyinstrument — profiler  
- Sentry — error tracking

**Dev Tools:**
- Ruff (linting)
- Mypy (type checking)
- Pytest (+ pytest-asyncio, pytest-cov)
- Testcontainers for integration testing
- Pre-commit hooks

---

## Deployment with Nginx & Let's Encrypt

### Setup

1. Configure `.env` (see `.env.example`):
2. Obtain certificates (first time only):
   ```bash
   docker compose --env-file .env run  --rm -p 80:80 certbot
   ```
3. Start services:
    ```bash
    docker compose up -d --build api migrations postgres redis mimio mimio-init nginx certbot-renew promtail loki prometheus tempo grafana
    ```

## Notes

- nginx serves HTTPS using certificates from certbot
- certbot-renew runs in the background and reloads nginx when certs are renewed.
- All HTTP traffic is redirected to HTTPS

---

### Main Application Screens

<img width="1920" height="868" alt="image" src="https://github.com/user-attachments/assets/cdfd00e5-2dcc-4876-83e2-c2c78b1f7a20" />

---

<img width="1920" height="868" alt="image" src="https://github.com/user-attachments/assets/bc8fa36e-ca42-43be-aed0-a7e5b89f0d80" />

---

<img width="1920" height="868" alt="image" src="https://github.com/user-attachments/assets/99c0f477-927b-48ed-9b74-37c924eb40b6" />

---

### Grafana Dashboards

<img width="1920" height="868" alt="image" src="https://github.com/user-attachments/assets/4757e50c-11e0-4a1d-97d2-f164b45f3479" />

