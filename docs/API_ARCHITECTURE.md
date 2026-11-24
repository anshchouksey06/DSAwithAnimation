# AI DSA Studio — API Architecture

**Document Version:** 1.0
**Status:** Initial API Specification
**Backend:** Python + FastAPI
**Frontend:** Next.js + TypeScript
**Database:** MongoDB
**Background Jobs:** Celery + Redis
**Video Renderer:** Remotion
**API Base Path:** `/api/v1`

---

## 1. Purpose

This document defines the API architecture for AI DSA Studio.

It specifies:

- API design principles.
- Backend module organization.
- API endpoint groups.
- Request and response formats.
- Authentication and authorization.
- Video-generation job management.
- Pipeline communication.
- Artifact management.
- Publishing APIs.
- Error handling.
- Validation.
- API security.
- Versioning and documentation.

The API must support the complete lifecycle of educational video generation, from user input to final MP4 delivery.

## 2. API Architecture Overview

The frontend communicates with the FastAPI backend through REST APIs.

The backend manages business logic, database operations, authorization, and job orchestration.

Long-running operations are delegated to background workers.

```text
                 NEXT.JS FRONTEND
                        |
                        |
                    HTTPS / REST
                        |
                        v
                 FASTAPI BACKEND
                        |
          +-------------+-------------+
          |             |             |
          v             v             v
       MongoDB        Redis       External APIs
          |             |
          |             v
          |        Celery Workers
          |             |
          |      +------+------+
          |      |      |      |
          |      v      v      v
          |     AI     TTS   Renderer
          |   Engine         (Remotion)
          |      |      |      |
          |      +------+------+
          |             |
          |             v
          |           FFmpeg
          |             |
          v             v
       Job Data     Video Artifacts
                        |
                        v
                    File Storage
```

**Important:**

- The frontend must never communicate directly with MongoDB.
- The frontend must never communicate directly with Redis.
- The frontend must never execute video rendering.
- Celery workers must not depend on frontend requests remaining open.
- MongoDB stores persistent job state.
- Redis is used for background task transport.

## 3. API Design Principles

### 3.1 RESTful design

Use resource-oriented endpoints.

Examples:

```text
POST   /api/v1/generations
GET    /api/v1/generations/{job_id}
GET    /api/v1/videos
GET    /api/v1/videos/{video_id}
POST   /api/v1/publishing
```

### 3.2 JSON communication

Requests and responses use JSON unless the endpoint explicitly handles file uploads.

Default headers:

```text
Content-Type: application/json
Accept: application/json
```

### 3.3 Consistent responses

Successful response:

```json
{
  "success": true,
  "data": {},
  "meta": {}
}
```

Failed response:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The supplied input is invalid",
    "details": []
  }
}
```

Do not expose internal stack traces or sensitive infrastructure details to clients.

### 3.4 API versioning

All application endpoints use:

```text
/api/v1/
```

Breaking changes should use a new API version.

### 3.5 Long-running operations

Video generation, rendering, and publishing must be asynchronous.

The API should:

1. Validate the request.
2. Create a persistent job record.
3. Enqueue background work.
4. Return a job identifier.
5. Allow the frontend to query progress.

Never keep a normal HTTP request open until a video finishes rendering.

## 4. Backend Module Architecture

Suggested backend structure:

```text
backend/
└── app/
    ├── main.py
    │
    ├── api/
    │   ├── router.py
    │   ├── dependencies.py
    │   └── routes/
    │       ├── health.py
    │       ├── auth.py
    │       ├── generations.py
    │       ├── videos.py
    │       ├── artifacts.py
    │       ├── library.py
    │       ├── topics.py
    │       ├── social_accounts.py
    │       ├── publishing.py
    │       ├── notifications.py
    │       └── analytics.py
    │
    ├── core/
    │   ├── config.py
    │   ├── security.py
    │   ├── exceptions.py
    │   └── logging.py
    │
    ├── schemas/
    │   ├── common.py
    │   ├── generation.py
    │   ├── video.py
    │   ├── artifact.py
    │   └── publishing.py
    │
    ├── models/
    ├── repositories/
    ├── services/
    ├── workers/
    ├── orchestration/
    ├── problem_processor/
    ├── explanation_engine/
    ├── verification/
    ├── scene_planner/
    ├── narration/
    ├── rendering/
    └── publishing/
```

### Responsibility separation

**API routes** — Handle HTTP requests, authentication dependencies, request validation, and response serialization.

**Services** — Contain application business logic.

**Repositories** — Handle MongoDB queries and persistence.

**Workers** — Execute asynchronous jobs.

**Orchestration** — Controls pipeline stage order, state transitions, and retries.

**Schemas** — Define validated request and response structures.

## 5. API Endpoint Groups

| Module | Base endpoint | Responsibility |
|---|---|---|
| Health | `/health` | Service health |
| Authentication | `/auth` | User authentication |
| Generations | `/generations` | Create and monitor video jobs |
| Videos | `/videos` | Manage generated videos |
| Artifacts | `/artifacts` | Access intermediate and final files |
| Library | `/library` | User content library |
| Topics | `/topics` | DSA topic library |
| Social Accounts | `/social-accounts` | Connect Instagram |
| Publishing | `/publishing` | Publish and schedule videos |
| Notifications | `/notifications` | User notifications |
| Analytics | `/analytics` | Basic available analytics |

## 6. Health API

`GET /api/v1/health`

**Purpose:** Check whether the API service is running.

Response:

```json
{
  "success": true,
  "data": {
    "status": "ok",
    "service": "ai-dsa-studio-api",
    "version": "1.0.0"
  }
}
```

This endpoint should not expose sensitive environment information.

An optional internal readiness endpoint may separately check database and Redis connectivity.

## 7. Authentication APIs

Authentication provider is not finalized yet.

The API architecture should support an interchangeable authentication implementation.

### Suggested endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/auth/register` | Register user |
| POST | `/auth/login` | Authenticate user |
| POST | `/auth/logout` | End session |
| GET | `/auth/me` | Get current user |
| POST | `/auth/refresh` | Refresh session if supported |

The final implementation may use a managed authentication provider instead of implementing password management directly.

### Authentication requirements

- Use secure authentication.
- Validate access tokens on protected routes.
- Enforce ownership of user resources.
- Keep authentication secrets out of frontend source code.
- Use secure cookie settings if cookie-based sessions are selected.
- Apply CSRF protection where required by the selected session design.

All user-owned API resources must require authentication.

## 8. Video Generation APIs

This is the most important API group.

### 8.1 Create a generation job

`POST /api/v1/generations`

**Purpose:** Submit a new video-generation request.

Request example:

```json
{
  "input_type": "problem",
  "problem": {
    "title": "Two Sum",
    "statement": "Given an array of integers...",
    "source_url": null
  },
  "programming_language": "cpp",
  "duration_preference": {
    "mode": "recommended",
    "target_seconds": null
  },
  "video_preferences": {
    "aspect_ratio": "9:16",
    "resolution": "1080x1920",
    "narration_language": "en",
    "subtitles_enabled": true
  }
}
```

Supported `input_type` values:

- `prompt`
- `topic`
- `problem`

Supported programming languages:

- `cpp`
- `java`
- `python`
- `javascript`

Duration preference modes:

- `recommended`
- `target`
- `range`

The API schema must validate fields according to the selected mode.

For example, a range preference must include minimum and maximum duration.

**Response**

HTTP `202 Accepted`

```json
{
  "success": true,
  "data": {
    "job_id": "job_123456",
    "status": "queued",
    "message": "Video generation has been queued"
  }
}
```

The job ID is used to track the generation.

### 8.2 Get generation status

`GET /api/v1/generations/{job_id}`

Response:

```json
{
  "success": true,
  "data": {
    "job_id": "job_123456",
    "status": "processing",
    "current_stage": "generating_audio",
    "progress": {
      "completed_stages": 6,
      "total_stages": 10
    },
    "created_at": "2026-11-24T12:00:00Z",
    "updated_at": "2026-11-24T12:03:00Z",
    "error": null
  }
}
```

Progress stage count is an approximate indicator, not a guaranteed percentage of remaining execution time.

Suggested job statuses:

- `queued`
- `processing`
- `completed`
- `failed`
- `cancelled`

Suggested pipeline stages:

- `input_processing`
- `problem_normalization`
- `explanation_generation`
- `technical_verification`
- `scene_planning`
- `narration_generation`
- `audio_generation`
- `subtitle_generation`
- `video_rendering`
- `video_assembly`
- `quality_check`

### 8.3 List generation jobs

`GET /api/v1/generations`

Query parameters:

```text
?page=1
&limit=20
&status=completed
```

Purpose:

- Show generation history.
- Filter by status.
- Support pagination.

### 8.4 Retry a failed job

`POST /api/v1/generations/{job_id}/retry`

Request:

```json
{
  "from_stage": "audio_generation"
}
```

The backend must verify that the selected stage is safe to retry and that all required upstream artifacts are valid.

Do not blindly restart the entire pipeline.

### 8.5 Cancel a generation job

`POST /api/v1/generations/{job_id}/cancel`

**Purpose:** Request cancellation of an active generation job.

Cancellation should be cooperative. Workers must check cancellation state between safe stage boundaries.

Response:

```json
{
  "success": true,
  "data": {
    "job_id": "job_123456",
    "status": "cancellation_requested"
  }
}
```

## 9. Video APIs

### 9.1 List generated videos

`GET /api/v1/videos`

Query parameters:

```text
?page=1
&limit=20
&search=two-sum
```

Response:

```json
{
  "success": true,
  "data": [
    {
      "video_id": "video_001",
      "title": "Two Sum Explained",
      "status": "ready",
      "duration_seconds": 112,
      "created_at": "2026-11-24T12:30:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 1
  }
}
```

### 9.2 Get video details

`GET /api/v1/videos/{video_id}`

Return:

- Video metadata.
- Generation job reference.
- Duration.
- Resolution.
- Programming language.
- Validation status.
- QA status.
- Artifact references.
- Creation timestamp.

### 9.3 Delete a video

`DELETE /api/v1/videos/{video_id}`

**Purpose:** Delete a user's video and associated eligible artifacts.

Deletion must verify ownership.

If a video is referenced by an active publishing job, apply a defined conflict policy rather than deleting it unexpectedly.

## 10. Artifact APIs

Artifacts are intermediate or final files produced during generation.

Examples:

- Problem JSON.
- Explanation JSON.
- Validation report.
- Scene plan.
- Narration script.
- Audio.
- Subtitles.
- Silent video.
- Final MP4.
- QA report.

### 10.1 List artifacts

`GET /api/v1/videos/{video_id}/artifacts`

Response:

```json
{
  "success": true,
  "data": [
    {
      "artifact_id": "artifact_001",
      "type": "final_video",
      "format": "mp4",
      "size_bytes": 12400000
    },
    {
      "artifact_id": "artifact_002",
      "type": "subtitles",
      "format": "srt",
      "size_bytes": 4200
    }
  ]
}
```

### 10.2 Get artifact access URL

`GET /api/v1/artifacts/{artifact_id}/access`

**Purpose:** Obtain an authorized download or playback URL.

For local development, this can return an authenticated backend download route.

For future object storage, it may return a short-lived signed URL.

Never expose raw server filesystem paths.

### 10.3 Download artifact

`GET /api/v1/artifacts/{artifact_id}/download`

The backend must verify artifact ownership before streaming the file or redirecting to a secure signed URL.

## 11. Library APIs

The library organizes generated videos for the user.

Suggested endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/library` | List library items |
| POST | `/library` | Add an item if manual organization is supported |
| PATCH | `/library/{item_id}` | Update metadata |
| DELETE | `/library/{item_id}` | Remove library item |

Library items can reference existing video records rather than duplicating media metadata.

## 12. DSA Topic APIs

`GET /api/v1/topics`

**Purpose:** Return the available DSA topic library.

Query parameters:

```text
?category=arrays
&search=binary-search
```

Example response:

```json
{
  "success": true,
  "data": [
    {
      "topic_id": "binary-search",
      "title": "Binary Search",
      "category": "searching",
      "difficulty": "easy"
    }
  ]
}
```

`GET /api/v1/topics/{topic_id}`

Return topic details and the information needed to initiate generation.

The topic library should be independent of generated video records.

## 13. Instagram Account APIs

The application will support one Instagram Professional account per user in V1.

Use official Meta authorization and publishing APIs.

### 13.1 Start account connection

`GET /api/v1/social-accounts/instagram/connect`

**Purpose:**

- Initiate the OAuth authorization flow.
- Redirect the user to the official authorization process.

The frontend should navigate to the returned authorization URL or follow the backend redirect.

### 13.2 OAuth callback

`GET /api/v1/social-accounts/instagram/callback`

**Purpose:**

- Receive the authorization response.
- Validate state.
- Exchange authorization credentials as supported.
- Retrieve account metadata.
- Securely store authorized credentials.

The callback must validate the OAuth state parameter to protect against CSRF.

### 13.3 Get connected account

`GET /api/v1/social-accounts`

Return connected account metadata.

Do not return access tokens.

### 13.4 Disconnect account

`DELETE /api/v1/social-accounts/{account_id}`

Disconnect the user's social account and revoke or delete stored credentials as appropriate.

## 14. Publishing APIs

Publishing is separate from video generation.

A completed video is not automatically published unless the user has explicitly enabled an appropriate automatic-publishing workflow.

### 14.1 Publish a video

`POST /api/v1/publishing`

Request:

```json
{
  "video_id": "video_001",
  "account_id": "instagram_account_001",
  "mode": "approval_required",
  "caption": "Learn Two Sum with a visual explanation!",
  "hashtags": [
    "DSA",
    "Coding",
    "Programming"
  ],
  "scheduled_at": null
}
```

Supported modes:

- `approval_required`
- `automatic`

The backend must validate that the video is complete, technically validated, and eligible for publishing.

For approval-required mode, the job must wait for explicit approval.

For automatic mode, the job may proceed only if the user has explicitly authorized that workflow.

Response:

```json
{
  "success": true,
  "data": {
    "publishing_job_id": "publish_001",
    "status": "pending_approval"
  }
}
```

### 14.2 Approve publishing

`POST /api/v1/publishing/{publishing_job_id}/approve`

**Purpose:** Explicitly approve an approval-required publishing job.

### 14.3 Schedule publishing

`POST /api/v1/publishing/{publishing_job_id}/schedule`

Request:

```json
{
  "scheduled_at": "2026-11-25T12:00:00Z"
}
```

The backend must:

- Validate the scheduled time.
- Store it persistently.
- Avoid duplicate scheduling.
- Enqueue the publishing operation when due.

### 14.4 Get publishing status

`GET /api/v1/publishing/{publishing_job_id}`

Return:

- Publishing status.
- Video ID.
- Account metadata.
- Scheduled time.
- External publishing reference, if available.
- Error information.

### 14.5 Publishing status values

- `pending_approval`
- `scheduled`
- `queued`
- `processing`
- `published`
- `failed`
- `cancelled`

The system must use idempotency controls to prevent duplicate publishing.

## 15. Notifications APIs

`GET /api/v1/notifications`

Return paginated notifications.

`PATCH /api/v1/notifications/{notification_id}/read`

Mark a notification as read.

Notification events can include:

- Video generation completed.
- Video generation failed.
- Technical validation failed.
- Video ready for approval.
- Publishing completed.
- Publishing failed.
- Instagram account needs reauthorization.

## 16. Analytics APIs

`GET /api/v1/analytics/overview`

Return only analytics supported by the connected platform and available permissions.

Possible fields:

- Total generated videos.
- Total published videos.
- Successful publishing count.
- Failed publishing count.
- Available engagement metrics.

Do not fabricate missing metrics.

## 17. Request Validation

Use Pydantic models for API request and response validation.

Example:

```python
from typing import Literal
from pydantic import BaseModel, Field


class VideoPreferences(BaseModel):
    aspect_ratio: Literal["9:16"] = "9:16"
    resolution: Literal["1080x1920"] = "1080x1920"
    narration_language: Literal["en"] = "en"
    subtitles_enabled: bool = True


class GenerationRequest(BaseModel):
    input_type: Literal["prompt", "topic", "problem"]
    programming_language: Literal[
        "cpp",
        "java",
        "python",
        "javascript"
    ]
    video_preferences: VideoPreferences
```

This is an illustrative starting point. The final request model must include conditional validation for each input type and duration preference.

Never trust frontend validation alone.

## 18. Error Handling

Use standard HTTP status codes.

| Status | Meaning |
|---|---|
| 200 | Successful request |
| 201 | Resource created |
| 202 | Asynchronous job accepted |
| 204 | Successful operation without response body |
| 400 | Invalid request |
| 401 | Unauthenticated |
| 403 | Unauthorized |
| 404 | Resource not found |
| 409 | Conflict |
| 422 | Validation error |
| 429 | Rate limit exceeded |
| 500 | Internal server error |
| 503 | Service unavailable |

Suggested application error codes:

```text
VALIDATION_ERROR
AUTHENTICATION_REQUIRED
PERMISSION_DENIED
RESOURCE_NOT_FOUND
JOB_ALREADY_RUNNING
JOB_NOT_RETRYABLE
JOB_CANCELLED
TECHNICAL_VALIDATION_FAILED
RENDERING_FAILED
TTS_GENERATION_FAILED
ARTIFACT_NOT_AVAILABLE
INSTAGRAM_AUTH_REQUIRED
INSTAGRAM_PUBLISH_FAILED
RATE_LIMIT_EXCEEDED
INTERNAL_SERVER_ERROR
```

Error response example:

```json
{
  "success": false,
  "error": {
    "code": "TECHNICAL_VALIDATION_FAILED",
    "message": "The explanation did not pass mandatory validation.",
    "details": [
      {
        "stage": "verification",
        "check": "optimized_algorithm_tests"
      }
    ],
    "request_id": "req_001"
  }
}
```

Never return:

- Stack traces.
- Database connection strings.
- Access tokens.
- Internal server paths.
- Secret environment variables.

## 19. Job and Pipeline Communication

The API creates and manages jobs. Workers execute them.

Example:

```text
Frontend
   |
   | POST /generations
   v
FastAPI
   |
   | Save job
   v
MongoDB
   |
   | Enqueue task
   v
Redis
   |
   v
Celery Worker
   |
   +--> Problem Processor
   |
   +--> Explanation Engine
   |
   +--> Verification Engine
   |
   +--> Scene Planner
   |
   +--> Narration / TTS
   |
   +--> Remotion Renderer
   |
   +--> FFmpeg
   |
   +--> QA
   |
   v
MongoDB: Completed Job
   |
   v
Frontend polls job status
```

Workers should update MongoDB at every meaningful stage transition.

Redis must not be the only source of job state.

## 20. Database Mapping

| API Resource | MongoDB Collection |
|---|---|
| User | `users` |
| Generation job | `generation_jobs` |
| Video | `videos` |
| Artifact | `artifacts` |
| Library item | `library_items` |
| Topic | `topics` |
| Social account | `social_accounts` |
| Publishing job | `publishing_jobs` |
| Notification | `notifications` |
| Audit event | `audit_logs` |

Every user-owned resource must include an `owner_id`.

Repositories must enforce ownership checks. A user must never be able to retrieve another user's job or artifact by guessing an ID.

## 21. Security Requirements

### Authentication

- Require authentication on protected endpoints.
- Validate tokens on the backend.
- Apply appropriate session and CSRF protections.

### Authorization

- Check ownership for all user-owned resources.
- Check publishing permissions separately from video access.
- Do not trust user-supplied owner IDs.

### Input security

- Validate and limit request sizes.
- Sanitize external content where appropriate.
- Restrict URL fetching to reduce SSRF risks.
- Never blindly execute code extracted from a problem URL.

### File security

- Do not expose raw filesystem paths.
- Restrict artifact downloads to authorized users.
- Validate file types.
- Use safe file naming and storage paths.

### API protection

- Rate-limit expensive generation endpoints.
- Apply upload size limits.
- Log request IDs and job IDs.
- Never log access tokens or secrets.

## 22. Idempotency and Duplicate Prevention

Generation and publishing endpoints must support safe retries.

For generation:

- Accept an optional `Idempotency-Key` header.
- Store the key with the owner and request identity.
- Return the existing job when the same request is retried within the idempotency window.

For publishing:

- Ensure one logical publishing operation is processed only once.
- Persist external publishing references.
- Record uncertain external outcomes before attempting another publish.
- Do not blindly retry a request if the external platform may already have accepted it.

## 23. Pagination and Filtering

List endpoints should support:

```text
?page=1
&limit=20
&sort=created_at
&order=desc
```

Apply a reasonable maximum page size.

For large collections, cursor-based pagination can be introduced later.

## 24. API Documentation

FastAPI should generate OpenAPI documentation automatically.

Development endpoints:

```text
http://localhost:8000/docs
http://localhost:8000/redoc
http://localhost:8000/openapi.json
```

All important endpoints must include:

- Description.
- Request schema.
- Response schema.
- Authentication requirements.
- Possible error responses.
- Example payloads.

## 25. API Testing Strategy

Use:

- Pytest.
- HTTPX.
- FastAPI TestClient where appropriate.

### Test categories

**Unit tests**

- Request validation.
- Service logic.
- Ownership checks.
- Job state transitions.
- Idempotency logic.

**Integration tests**

- FastAPI and MongoDB.
- Celery task dispatch.
- Artifact creation.
- Worker status updates.
- Publishing adapter behavior with mocked external APIs.

**End-to-end tests**

- Submit a Two Sum generation request.
- Retrieve job status.
- Confirm successful pipeline completion.
- Retrieve video metadata.
- Access the final artifact.
- Confirm unauthorized users cannot access the resource.

External Instagram API tests must use mocked responses or approved test accounts and environments.

## 26. Implementation Phases

### Phase 1 — Prototype API

Implement only what is needed to validate the Two Sum pipeline.

Endpoints:

- `GET /health`
- `POST /generations`
- `GET /generations/{job_id}`
- `POST /generations/{job_id}/retry`
- `GET /videos/{video_id}`
- `GET /videos/{video_id}/artifacts`
- `GET /artifacts/{artifact_id}/download`

Initially, a local single-user development mode may be used, but it must be isolated from production configuration. Do not treat it as production authentication.

### Phase 2 — Learning Studio API

Add:

- Authentication.
- User ownership.
- Generation history.
- Video library.
- Topic library.
- Notifications.

### Phase 3 — Creator Studio API

Add:

- Instagram OAuth.
- Connected account management.
- Publishing approval.
- Scheduled publishing.
- Publishing history.
- Basic analytics.

### Phase 4 — Production Hardening

Add:

- Rate limiting.
- Advanced idempotency.
- More complete observability.
- Persistent scheduling.
- Secure artifact storage.
- Operational health checks.
- Production authentication and authorization.
- API performance and load testing.

## 27. API Definition of Done

The API architecture is implemented successfully when:

- Every endpoint has a defined request and response contract.
- All protected endpoints enforce authentication.
- User-owned resources enforce ownership checks.
- Generation endpoints return job IDs.
- Long-running work runs in background workers.
- MongoDB stores persistent job state.
- Redis is used for task transport.
- Job failures and retries are tracked.
- Artifact access is secure.
- Publishing is separated from generation.
- Duplicate jobs and publishing operations are prevented.
- API documentation is available through OpenAPI.
- Automated tests cover validation, authorization, and job behavior.

---

## 28. Instructions for Codex / Antigravity

Treat this document as the API design specification.

Before implementation:

1. Read `PRD.md`.
2. Read `PIPELINE_DESIGN.md`.
3. Read `SYSTEM_ARCHITECTURE.md`.
4. Read this `API_ARCHITECTURE.md`.
5. Identify inconsistencies between documents.
6. Report proposed corrections before changing finalized decisions.

Implementation rules:

- Use FastAPI and Pydantic.
- Follow service/repository separation.
- Use MongoDB for persistent application state.
- Use Celery and Redis for background execution when introducing distributed jobs.
- Do not render videos inside HTTP request handlers.
- Do not expose filesystem paths or credentials.
- Enforce ownership checks on all user-owned resources.
- Create automated tests for every implemented endpoint.
- Do not implement all future endpoints prematurely.
- Start with the Prototype 1 API scope.
- Keep interfaces compatible with the shared JSON contracts.
- Document any deviations from this specification.

> **Final implementation priority:** Build the smallest reliable API needed to generate, monitor, and retrieve the Two Sum video before implementing the complete SaaS API.
