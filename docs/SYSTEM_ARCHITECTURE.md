# AI DSA Studio — System Architecture

**Document version:** 1.0
**Architecture status:** Initial baseline

| Layer | Choice |
|---|---|
| Frontend | Next.js + TypeScript |
| Backend | Python + FastAPI |
| Database | MongoDB |
| Video renderer | Remotion |
| Background processing | Celery + Redis |
| Media assembly | FFmpeg |

---

## 1. Architecture Goals

The system architecture must support:

- Independent frontend, backend, and rendering services.
- Long-running video-generation jobs.
- Reusable pipeline stages.
- Structured and versioned contracts.
- Secure code execution.
- Replaceable AI and TTS providers.
- Reliable job retries.
- Local development before paid infrastructure.
- Future deployment without major architectural changes.

## 2. Technology Stack

| Layer | Technology | Responsibility |
|---|---|---|
| Frontend | Next.js + TypeScript | User interface |
| Styling | Tailwind CSS | UI styling |
| Backend API | Python + FastAPI | API and orchestration |
| Database | MongoDB | Persistent application data |
| ODM/data access | PyMongo or Beanie | MongoDB access from Python |
| Background jobs | Celery | Asynchronous task execution |
| Message broker | Redis | Job transport and queueing |
| Video rendering | Remotion + React | Deterministic scene rendering |
| Media processing | FFmpeg | Audio/video assembly |
| Local TTS | Piper candidate | Local narration generation |
| Containers | Docker | Reproducible services |
| Version control | Git + GitHub | Source management |

Use one MongoDB access approach consistently in the backend. Do not introduce Mongoose; it is intended for Node.js applications, while this backend is Python-based.

## 3. High-Level Architecture

```text
                  USER
                   |
                   v
          NEXT.JS FRONTEND
                   |
              HTTPS / API
                   |
                   v
             FASTAPI BACKEND
                   |
          +--------+---------+
          |                  |
          v                  v
       MONGODB             REDIS
          |                  |
          |                  v
          |             CELERY WORKERS
          |                  |
          |        +---------+---------+
          |        |         |         |
          |        v         v         v
          |    AI/Logic     TTS     Rendering
          |    Pipeline   Service    Service
          |        |         |         |
          |        +---------+---------+
          |                  |
          |                  v
          |              FFMPEG
          |                  |
          v                  v
       JOB DATA         MEDIA ARTIFACTS
                             |
                             v
                      STORAGE SYSTEM
```

This is a logical architecture. The initial prototype may run multiple components locally in fewer processes. The interfaces should still remain modular.

## 4. Frontend Architecture

### Technology

- Next.js
- TypeScript
- App Router
- Tailwind CSS

### Main sections

```text
frontend/
└── src/
    ├── app/
    │   ├── dashboard/
    │   ├── learning-studio/
    │   ├── creator-studio/
    │   ├── library/
    │   ├── calendar/
    │   └── settings/
    ├── components/
    ├── features/
    │   ├── video-generation/
    │   ├── learning/
    │   ├── creator/
    │   ├── publishing/
    │   └── library/
    ├── lib/
    ├── services/
    ├── hooks/
    └── types/
```

### Responsibilities

- Collect user input.
- Allow language and duration selection.
- Submit generation jobs.
- Display generation progress.
- Display validation results.
- Preview generated videos.
- Manage content library.
- Manage publishing approvals and schedules.
- Display job errors and retry options.

### The frontend must not

- Store private API credentials.
- Run video rendering.
- Execute untrusted user code.
- Directly access private backend services.

## 5. Backend Architecture

### Technology

Python + FastAPI.

### Responsibilities

- API endpoints.
- Input validation.
- User and ownership authorization.
- Job creation.
- Job status retrieval.
- Pipeline orchestration.
- Database access.
- Scheduling and publishing coordination.
- Artifact metadata management.

### Suggested structure

```text
backend/
└── app/
    ├── main.py
    ├── api/
    │   ├── routes/
    │   └── dependencies/
    ├── core/
    │   ├── config.py
    │   ├── security.py
    │   └── logging.py
    ├── models/
    ├── repositories/
    ├── schemas/
    ├── services/
    ├── problem_processor/
    ├── explanation_engine/
    ├── verification/
    ├── scene_planner/
    ├── narration/
    ├── orchestration/
    ├── publishing/
    └── workers/
```

Keep business logic outside API route handlers.

API routes should validate requests, call the relevant service, and return structured responses.

## 6. Background Job Architecture

Video generation is a long-running operation and must not execute inside a normal HTTP request.

Use:

- Celery for background task execution.
- Redis as the initial broker.
- MongoDB as the persistent source of truth for application job records.

### Job flow

1. Frontend submits a generation request.
2. FastAPI validates the request.
3. Backend creates a job record in MongoDB.
4. Backend enqueues a Celery task.
5. Worker executes pipeline stages.
6. Worker updates persistent job status.
7. Frontend polls the status endpoint initially.
8. Frontend displays completion or failure.

WebSockets or server-sent events can be added later if progress updates require them.

### Important rules

- Use idempotency keys for job creation where appropriate.
- Avoid duplicate rendering tasks.
- Persist stage-level status.
- Record error details without exposing secrets.
- Retry only stages that are safe to retry.
- Keep intermediate artifacts.
- Do not treat Redis as the only record of job state.

For the first local prototype, a simple local orchestrator is acceptable before Celery is introduced. Do not build unnecessary distributed infrastructure before the pipeline works.

## 7. MongoDB Architecture

MongoDB is the primary persistent data store.

### Suggested collections

**`users`** — Stores user profile and account metadata.

**`projects`** — Stores video-generation projects or workspaces if required.

**`generation_jobs`** — Stores:

- Job ID.
- Owner ID.
- Input.
- Selected language.
- Requested duration.
- Current state.
- Current stage.
- Error information.
- Created and updated timestamps.

**`artifacts`** — Stores:

- Artifact ID.
- Job ID.
- Owner ID.
- Artifact type.
- Storage path or object key.
- File metadata.
- Content hash.
- Schema version where relevant.

**`videos`** — Stores:

- Video ID.
- Owner ID.
- Job ID.
- Final video artifact.
- Duration.
- Resolution.
- Status.
- Creation timestamp.

**`social_accounts`** — Stores authorized social account metadata and securely protected tokens.

**`publishing_jobs`** — Stores:

- Owner ID.
- Video ID.
- Target account.
- Scheduled time.
- Publishing status.
- External publishing reference.
- Error information.

**`notifications`** — Stores user-facing notifications.

**`audit_logs`** — Stores important security and publishing events.

All user-owned documents must include an owner identifier. Every read and write must enforce ownership authorization.

Do not store large media binaries directly in ordinary MongoDB documents. Store media in the filesystem initially and use object storage when needed. Keep the artifact metadata in MongoDB.

## 8. Shared Contracts

The frontend, backend, and renderer must agree on shared data formats.

Create a root-level `contracts/` directory.

```text
contracts/
├── problem.schema.json
├── explanation.schema.json
├── validation.schema.json
├── scene-plan.schema.json
├── narration.schema.json
└── qa-report.schema.json
```

Requirements:

- Version every contract.
- Validate Python payloads using Pydantic or JSON Schema.
- Validate TypeScript payloads using a compatible validator such as AJV or generated types.
- Keep the contract as the source of truth.
- Do not maintain conflicting manually written definitions in multiple services.

A contract change must be reviewed for compatibility with every component that consumes it.

## 9. Renderer Architecture

### Technology

Remotion + React + SVG/Canvas.

The renderer is a separate application.

### Suggested structure

```text
renderer/
└── src/
    ├── Root.tsx
    ├── compositions/
    ├── scenes/
    │   ├── IntroScene.tsx
    │   ├── ArrayScene.tsx
    │   ├── BruteForceScene.tsx
    │   ├── HashMapScene.tsx
    │   ├── ComplexityScene.tsx
    │   └── SummaryScene.tsx
    ├── components/
    ├── animations/
    ├── themes/
    ├── utils/
    └── types/
```

### The renderer should

- Accept validated scene-plan data.
- Resolve only allowlisted scene components.
- Validate scene props.
- Use deterministic animation logic.
- Produce a silent video.
- Return a structured render result.

The renderer must not execute arbitrary code received from an AI model or user.

## 10. Narration and TTS Architecture

Create a replaceable TTS provider interface.

```text
backend/app/narration/
├── providers/
│   ├── base.py
│   └── piper_provider.py
├── script_generator.py
├── audio_manager.py
├── timing.py
└── subtitles.py
```

Piper is the initial local TTS candidate.

Keep:

- Narration script.
- Segment IDs.
- Audio files.
- Timing manifest.
- Subtitle files.

Separate the provider implementation from the pipeline logic. This allows another local or hosted provider to be introduced later without redesigning the pipeline.

## 11. Secure Code Execution

If the platform compiles or executes generated code, use an isolated execution environment.

Requirements:

- Separate containers or equivalent sandboxing.
- CPU limits.
- Memory limits.
- Execution timeouts.
- Restricted filesystem access.
- No unrestricted network access.
- No access to host secrets.
- No privileged container execution.

Do not execute user-supplied or AI-generated code directly inside the main FastAPI process.

For Prototype 1, use trusted local algorithm implementations and test fixtures. Introduce a general-purpose code execution sandbox only when the product needs it.

## 12. Storage Architecture

### Initial development

Use local filesystem storage.

Suggested layout:

```text
storage/
├── jobs/
├── audio/
├── subtitles/
├── renders/
└── final-videos/
```

Store artifact metadata in MongoDB.

### Future deployment

Move media storage behind a storage interface.

Possible object-storage providers can be selected later. The rest of the application should use artifact IDs or storage keys rather than depending on a specific provider's API.

Do not make a paid storage provider mandatory for the first prototype.

## 13. Instagram Integration

Use the official Meta APIs.

Architecture:

```text
Creator Studio
      |
      v
FastAPI Publishing Service
      |
      v
Publishing Job Queue
      |
      v
Meta API Adapter
      |
      v
Instagram Professional Account
```

Requirements:

- OAuth-based authorization.
- Secure token storage.
- Token refresh or reauthorization handling as supported.
- Permission and account eligibility checks.
- Publishing status tracking.
- Duplicate prevention.
- Rate-limit and error handling.

Keep Meta-specific API logic in a separate adapter. Do not mix it into the video-generation pipeline.

The integration must comply with current Meta API requirements and supported publishing capabilities.

## 14. Scheduler Architecture

Scheduled publishing should use persistent database records.

The scheduler should:

1. Find due publishing jobs.
2. Confirm the job has not already been processed.
3. Verify the video is eligible for publishing.
4. Enqueue the publishing task.
5. Record the result.
6. Retry eligible transient failures safely.

A scheduler must not depend solely on an in-memory timer because the application may restart.

## 15. API Groups

Initial API groups:

```text
/api/v1/health

/api/v1/auth

/api/v1/generations
/api/v1/generations/{job_id}
/api/v1/generations/{job_id}/retry

/api/v1/videos
/api/v1/videos/{video_id}

/api/v1/library

/api/v1/social-accounts
/api/v1/publishing
/api/v1/publishing/{publishing_job_id}

/api/v1/notifications
```

The exact request and response schemas should be finalized after the shared contracts and initial data model are approved.

Long-running generation endpoints should return a job ID rather than waiting for the final video.

## 16. Deployment Strategy

### Initial development

- Frontend: local Next.js development server.
- Backend: local FastAPI server.
- MongoDB: local Docker container or MongoDB Atlas development database.
- Redis: local Docker container when background jobs are introduced.
- Renderer: local Remotion environment.
- TTS: local voice-generation environment.
- FFmpeg: local installation.

### Later deployment

Keep services independently deployable:

- Frontend.
- Backend API.
- Background workers.
- Renderer.
- Database.
- Redis.
- Media storage.

Vercel can be used for the frontend initially. Backend and worker deployment should use an environment capable of running persistent Python services and rendering workloads.

Do not assume serverless request handlers are suitable for long-running video rendering.

## 17. Environment Configuration

Use environment variables for configuration.

Example `.env.example`:

```bash
APP_ENV=development
APP_NAME=AI DSA Studio

BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000

MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=ai_dsa_studio

REDIS_URL=redis://localhost:6379/0

STORAGE_MODE=local
LOCAL_STORAGE_PATH=./storage

TTS_PROVIDER=piper
```

Do not commit real secrets or production credentials.

Keep `.env` out of Git. Commit only `.env.example` with placeholder values.

## 18. Suggested Root Repository Structure

```text
ai-dsa-studio/
├── frontend/
├── backend/
├── renderer/
├── contracts/
├── examples/
│   └── two-sum/
├── assets/
│   ├── fonts/
│   ├── music/
│   └── voices/
├── storage/
├── output/
├── infrastructure/
│   └── docker-compose.yml
├── docs/
│   ├── PRD.md
│   ├── PIPELINE_DESIGN.md
│   └── SYSTEM_ARCHITECTURE.md
├── .env.example
├── .gitignore
└── README.md
```

The repository can start smaller during Prototype 1. Do not create empty modules just to match the final structure.

## 19. Development Principles

1. Build the smallest working end-to-end pipeline first.
2. Keep modules independent.
3. Define contracts before integrating components.
4. Use deterministic fixtures for early pipeline testing.
5. Introduce AI generation after deterministic validation works.
6. Use local/free tools where practical.
7. Avoid unnecessary paid services.
8. Never execute arbitrary AI-generated renderer code.
9. Preserve intermediate artifacts.
10. Make retries safe and idempotent.
11. Keep secrets on the backend.
12. Test every milestone before moving forward.

## 20. Architecture Decisions and Deferred Decisions

### Confirmed

- Next.js + TypeScript frontend.
- Python + FastAPI backend.
- MongoDB database.
- Remotion rendering.
- FFmpeg media assembly.
- Celery + Redis for background jobs as the production-oriented job architecture.
- Local storage initially.
- Docker for reproducible services.
- Local TTS for Prototype 1.
- Hybrid AI and deterministic verification.
- Independently deployable frontend, backend, and worker services.

### Deferred

- Final authentication provider.
- Final production hosting provider for backend and workers.
- Production object-storage provider.
- Production AI model/provider.
- Final local TTS voice model.
- Detailed MongoDB indexes.
- Complete API request and response contracts.
- Production monitoring provider.

These decisions should be made when the relevant implementation milestone is reached, rather than introducing unnecessary dependencies now.

---

> **Architecture principle:** Keep the system modular, portable, testable, and inexpensive to develop. The first priority is a reliable end-to-end video pipeline, not premature infrastructure complexity.
