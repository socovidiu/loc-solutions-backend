# loc-solutions-backend

Backend service for managing **localisation workflows**, integrating a **Translation Management System (TMS)** and **LLM-based Quality Control (QC)** behind a clean **REST API**.

This project is designed as a job-based localisation platform backend, handling:
- job lifecycle management
- TMS integration (project-based job creation)
- webhook-driven updates
- future AI/LLM-powered QC pipelines

---

## Key Features

- **REST API (FastAPI)** for job submission, status tracking, and results
- **PostgreSQL** persistence with UUIDs and JSONB for localisation content
- **TMS integration** (Phrase / Memsource–style APIs)
- **Webhook handling with idempotency**
  - event-level deduplication
  - job-level safe state transitions
- **Service + repository architecture**
  - thin API layer
  - isolated persistence logic
  - workflow orchestration in services
- **LLM-ready QC pipeline** (designed for async workers)

---

## Architecture & Design

The system follows a service-oriented, workflow-driven architecture tailored for localisation pipelines.

A full technical breakdown—including:
- database design
- job lifecycle
- webhook idempotency strategies
- TMS integration approach
- interview-oriented design explanations

is documented here:

👉 **[Architecture & Workflow Documentation](docs/ARCHITECTURE.md)**

---

## High-level Project Structure

```text
app/                # FastAPI application
  api/              # Routers (jobs, webhooks)
  services/         # Workflow orchestration
  repos/            # Database access layer
  clients/          # External integrations (TMS, LLM)
  db/               # SQLAlchemy models & session
docs/
  ARCHITECTURE.md   # Detailed architecture & interview notes
```