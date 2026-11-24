# AI DSA Studio — Database Architecture & MongoDB Schema

**Document Version:** 1.0
**Status:** Finalized
**Database:** MongoDB
**Backend:** Python + FastAPI
**ODM/Data Access:** PyMongo or Beanie
**Project:** AI DSA Studio

---

## 1. Purpose

This document defines the database architecture, MongoDB collections, document structures, relationships, indexes, data ownership rules, and storage policies for AI DSA Studio.

The database must support two main application areas:

1. **Learning Studio:** Generate educational DSA videos from prompts, topics, and coding problems.
2. **Creator Studio:** Manage generated videos and publish them to connected social media accounts.

The design must support the initial Two Sum prototype while remaining extensible for the complete V1 product.

## 2. Final Architecture Decisions

| Decision | Final choice |
|---|---|
| Database | MongoDB |
| User identity | Internal MongoDB ObjectId + managed authentication provider ID |
| User preferences | Separate collection |
| Generation lifecycle | Central `generation_jobs` collection |
| Pipeline outputs | Versioned artifact records |
| Media storage | Local filesystem initially; object storage later |
| Artifact retention | Preserve all artifacts |
| Video regeneration | Create a new video record; preserve previous videos |
| Database access | Python backend using PyMongo or Beanie |
| Timestamps | UTC |
| Internal identifiers | MongoDB ObjectId |

### Important principles

- MongoDB stores application data and metadata.
- Video, audio, and other large files are stored outside MongoDB.
- Every user-owned document must have an `owner_id`.
- Every generation request creates a generation job.
- Every successful generation creates a new video record.
- Intermediate artifacts must remain available for debugging, retries, and future regeneration.
- The backend is responsible for authorization and data ownership enforcement.

---

## 3. Collection Overview

The proposed full V1 database contains the following collections.

| Collection | Purpose | Priority |
|---|---|---|
| `users` | Application user profiles | Prototype |
| `user_preferences` | User-specific settings | Prototype |
| `generation_jobs` | Generation lifecycle and status | Prototype |
| `artifacts` | Pipeline output metadata | Prototype |
| `videos` | Completed generated videos | Prototype |
| `job_events` | Generation history and state transitions | Prototype |
| `topics` | Shared DSA topic catalogue | V1 |
| `social_accounts` | Connected social accounts | V1 |
| `publishing_jobs` | Publishing and scheduling | V1 |
| `notifications` | User-facing notifications | V1 |
| `audit_logs` | Important security and account events | V1 |
| `library_items` | Optional organization metadata | Later V1, if needed |

Do not create all collections immediately. Implement the prototype collections first.

The `library_items` collection is optional because the `videos` collection can initially provide the basic content library.

---

## 4. Collection Schemas

### 4.1 `users`

Stores application-level user information.

Authentication is handled by an external managed authentication provider.

The application database must not store user passwords.

#### Document structure

```json
{
  "_id": "ObjectId",
  "auth": {
    "provider": "managed_provider",
    "provider_user_id": "external_user_123"
  },
  "email": "user@example.com",
  "display_name": "Alex",
  "avatar_url": null,
  "account_status": "active",
  "created_at": "2026-11-24T12:00:00Z",
  "updated_at": "2026-11-24T12:00:00Z"
}
```

#### Fields

| Field | Type | Description |
|---|---|---|
| `_id` | ObjectId | Internal user ID |
| `auth.provider` | String | Authentication provider |
| `auth.provider_user_id` | String | External provider's stable user ID |
| `email` | String | User email |
| `display_name` | String | Display name |
| `avatar_url` | String/null | Profile image |
| `account_status` | String | Account status |
| `created_at` | Date | Creation time |
| `updated_at` | Date | Last update |

#### Rules

- Use the internal MongoDB `_id` for all application relationships.
- Resolve the external identity to the internal user record after verifying the authentication token.
- Never trust a user ID supplied by the frontend as proof of identity.
- Do not store passwords, session tokens, or provider secrets in this collection.
- Email changes must be synchronized from verified authentication-provider information.
- Treat email as a profile attribute, not the primary identity key.

#### Indexes

```javascript
db.users.createIndex(
  {
    "auth.provider": 1,
    "auth.provider_user_id": 1
  },
  { unique: true }
);
```

Optional email lookup index:

```javascript
db.users.createIndex({ email: 1 });
```

Apply email uniqueness only if the chosen provider and account-linking policy guarantee it.

---

### 4.2 `user_preferences`

Stores user-specific application and video generation preferences.

#### Document structure

```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId",
  "default_programming_language": "cpp",
  "narration_language": "en",
  "default_video_format": "9:16",
  "default_resolution": "1080x1920",
  "subtitles_enabled": true,
  "default_duration_mode": "recommended",
  "theme": "system",
  "created_at": "2026-11-24T12:00:00Z",
  "updated_at": "2026-11-24T12:00:00Z"
}
```

#### Fields

| Field | Type | Description |
|---|---|---|
| `_id` | ObjectId | Document ID |
| `user_id` | ObjectId | Reference to user |
| `default_programming_language` | String | Default code language |
| `narration_language` | String | Narration language |
| `default_video_format` | String | Aspect ratio |
| `default_resolution` | String | Video resolution |
| `subtitles_enabled` | Boolean | Subtitle preference |
| `default_duration_mode` | String | Recommended or custom |
| `theme` | String | Interface theme |
| `created_at` | Date | Creation time |
| `updated_at` | Date | Last update |

#### Rules

- One preferences document per user.
- Create default preferences when a user first enters the application.
- Generation requests must snapshot the effective configuration into their own job document.
- Updating preferences must not modify previously created generation jobs.

#### Index

```javascript
db.user_preferences.createIndex(
  { user_id: 1 },
  { unique: true }
);
```

---

### 4.3 `generation_jobs`

This is the central collection of the video generation system.

Every video generation request creates a new job.

The document tracks:

- User input
- Generation configuration
- Overall job status
- Pipeline stage status
- Retry information
- Errors
- Resulting video reference

#### Document structure

```json
{
  "_id": "ObjectId",
  "owner_id": "ObjectId",
  "job_type": "video_generation",

  "input": {
    "input_type": "problem",
    "title": "Two Sum",
    "problem_statement": "Given an array of integers...",
    "source_url": null,
    "topic_id": null
  },

  "configuration": {
    "programming_language": "cpp",
    "duration_mode": "recommended",
    "target_duration_seconds": null,
    "narration_language": "en",
    "aspect_ratio": "9:16",
    "resolution": "1080x1920",
    "frame_rate": 30,
    "subtitles_enabled": true
  },

  "status": "processing",
  "current_stage": "audio_generation",

  "stages": {
    "input_processing": {
      "status": "completed",
      "attempt_count": 1,
      "started_at": "2026-11-24T12:00:00Z",
      "completed_at": "2026-11-24T12:01:00Z"
    },
    "explanation_generation": {
      "status": "completed",
      "attempt_count": 1
    },
    "technical_verification": {
      "status": "completed",
      "attempt_count": 1
    },
    "scene_planning": {
      "status": "completed",
      "attempt_count": 1
    },
    "narration_generation": {
      "status": "completed",
      "attempt_count": 1
    },
    "audio_generation": {
      "status": "processing",
      "attempt_count": 1
    },
    "video_rendering": {
      "status": "pending",
      "attempt_count": 0
    },
    "video_assembly": {
      "status": "pending",
      "attempt_count": 0
    },
    "quality_check": {
      "status": "pending",
      "attempt_count": 0
    }
  },

  "result_video_id": null,

  "retry": {
    "retry_count": 0,
    "max_retries": 3
  },

  "error": null,

  "created_at": "2026-11-24T12:00:00Z",
  "started_at": "2026-11-24T12:00:00Z",
  "completed_at": null,
  "updated_at": "2026-11-24T12:03:00Z"
}
```

#### Input types

Supported input types:

- `prompt`
- `topic`
- `problem`

The `input` object must be validated according to the selected input type.

#### Overall status values

- `queued`
- `processing`
- `completed`
- `failed`
- `cancelled`

#### Pipeline stage status values

- `pending`
- `queued`
- `processing`
- `completed`
- `failed`
- `skipped`

#### Rules

1. Every generation request must have an `owner_id`.
2. Every job must have a unique internal `_id`.
3. The original user input must remain available.
4. The configuration must be stored as a snapshot.
5. A job cannot be marked completed before mandatory validation and final QA pass.
6. Failed mandatory technical validation must block automatic publishing.
7. Retry attempts must be recorded.
8. A retry must not silently erase previous failure information.
9. `result_video_id` must reference the final video document after successful generation.
10. Stage names must follow the versioned pipeline contract.
11. Job updates must be atomic where state transitions require consistency.

#### Indexes

```javascript
db.generation_jobs.createIndex({
  owner_id: 1,
  created_at: -1
});

db.generation_jobs.createIndex({
  status: 1,
  created_at: 1
});

db.generation_jobs.createIndex({
  owner_id: 1,
  status: 1
});
```

Use separate indexes for worker scheduling and user history queries where necessary.

---

### 4.4 `artifacts`

Stores metadata for intermediate and final files generated by the pipeline.

Actual files must be stored outside MongoDB.

#### Artifact types

| Type | Format |
|---|---|
| `problem_input` | JSON |
| `explanation` | JSON |
| `validation_report` | JSON |
| `scene_plan` | JSON |
| `narration_script` | JSON |
| `narration_audio` | WAV |
| `narration_timeline` | JSON |
| `subtitles` | SRT |
| `silent_video` | MP4 |
| `final_video` | MP4 |
| `qa_report` | JSON |

#### Document structure

```json
{
  "_id": "ObjectId",
  "owner_id": "ObjectId",
  "job_id": "ObjectId",
  "video_id": null,

  "artifact_type": "scene_plan",
  "file_format": "json",
  "schema_version": "1.0",

  "version": 1,

  "storage": {
    "provider": "local",
    "path": "jobs/job_123/04_scene_plan.json"
  },

  "content_hash": "sha256_hash_here",
  "size_bytes": 12500,

  "status": "available",

  "created_at": "2026-11-24T12:02:00Z"
}
```

#### Fields

| Field | Type | Description |
|---|---|---|
| `_id` | ObjectId | Artifact ID |
| `owner_id` | ObjectId | Owner |
| `job_id` | ObjectId | Related generation job |
| `video_id` | ObjectId/null | Related final video, when applicable |
| `artifact_type` | String | Artifact category |
| `file_format` | String | File extension/format |
| `schema_version` | String | Artifact contract version |
| `version` | Integer | Version of this artifact type within the job |
| `storage.provider` | String | Storage backend |
| `storage.path` | String | Relative storage key/path |
| `content_hash` | String | Integrity hash |
| `size_bytes` | Integer | File size |
| `status` | String | Artifact availability |
| `created_at` | Date | Creation time |

#### Storage providers

Initially:

```json
{
  "provider": "local",
  "path": "jobs/job_123/04_scene_plan.json"
}
```

Future object storage:

```json
{
  "provider": "object_storage",
  "bucket": "ai-dsa-artifacts",
  "key": "users/user_123/jobs/job_123/04_scene_plan.json"
}
```

Do not store public or permanent signed download URLs as the canonical storage reference.

The backend should generate authorized download URLs or stream files after checking ownership.

#### Retention policy

All artifacts must be preserved.

- Do not automatically delete intermediate files after successful generation.
- Do not overwrite older artifact versions.
- Keep artifacts from failed and retried jobs for debugging.
- Store each new artifact as a new record.
- If an artifact is intentionally removed by an authorized retention or deletion operation, update its metadata and storage state consistently.

#### Indexes

```javascript
db.artifacts.createIndex({
  job_id: 1,
  artifact_type: 1,
  version: -1
});

db.artifacts.createIndex({
  owner_id: 1,
  created_at: -1
});

db.artifacts.createIndex({
  video_id: 1
});
```

---

### 4.5 `videos`

Represents completed educational video content.

A generation job represents the process. A video represents the output.

#### Document structure

```json
{
  "_id": "ObjectId",
  "owner_id": "ObjectId",
  "job_id": "ObjectId",

  "title": "Two Sum Explained",
  "description": "Learn brute force and hash map approaches.",

  "topic_ids": [],

  "programming_language": "cpp",

  "duration_seconds": 112,

  "media": {
    "artifact_id": "ObjectId",
    "format": "mp4",
    "resolution": "1080x1920",
    "aspect_ratio": "9:16",
    "frame_rate": 30,
    "video_codec": "h264",
    "audio_codec": "aac"
  },

  "validation_status": "passed",
  "qa_status": "passed",

  "status": "ready",

  "created_at": "2026-11-24T12:30:00Z",
  "updated_at": "2026-11-24T12:30:00Z"
}
```

#### Status values

- `processing`
- `ready`
- `failed`
- `archived`

Only successfully validated and assembled outputs should normally be available as ready videos.

#### Regeneration and versioning policy

Preserve previous videos.

Every new generation request creates its own job. Every successful job creates a new video record.

For example:

```text
Two Sum
 |
 +-- Video A: First generation
 |
 +-- Video B: Regenerated with updated narration
 |
 +-- Video C: Regenerated using Python
```

All three video records remain available.

Do not overwrite the previous video or its artifact records.

If a user wants to replace or archive an older video in the library, that must be a separate user action.

#### Indexes

```javascript
db.videos.createIndex({
  owner_id: 1,
  created_at: -1
});

db.videos.createIndex({
  job_id: 1
});

db.videos.createIndex({
  owner_id: 1,
  status: 1
});
```

---

### 4.6 `job_events`

Stores the history of generation job state transitions and important pipeline events.

This collection is append-oriented.

#### Document structure

```json
{
  "_id": "ObjectId",
  "owner_id": "ObjectId",
  "job_id": "ObjectId",

  "event_type": "stage_completed",

  "stage": "technical_verification",

  "details": {
    "message": "All mandatory technical checks passed.",
    "attempt": 1
  },

  "created_at": "2026-11-24T12:05:00Z"
}
```

#### Example event types

- `job_created`
- `job_started`
- `stage_started`
- `stage_completed`
- `stage_failed`
- `retry_started`
- `job_completed`
- `job_failed`
- `job_cancelled`

#### Rules

- Do not use this collection as the source of current job status.
- `generation_jobs` remains the source of truth for current state.
- Use `job_events` for history, troubleshooting, and future activity displays.
- Avoid storing secrets or unnecessarily large payloads in event details.

#### Indexes

```javascript
db.job_events.createIndex({
  job_id: 1,
  created_at: 1
});

db.job_events.createIndex({
  owner_id: 1,
  created_at: -1
});
```

---

### 4.7 `topics`

Stores the shared DSA topic catalogue.

Topics are not owned by individual users.

#### Document structure

```json
{
  "_id": "ObjectId",
  "name": "Arrays",
  "slug": "arrays",
  "description": "Fundamental array concepts and operations.",
  "parent_topic_id": null,
  "difficulty": "beginner",
  "is_active": true,
  "sort_order": 1,
  "created_at": "2026-11-24T12:00:00Z",
  "updated_at": "2026-11-24T12:00:00Z"
}
```

#### Indexes

```javascript
db.topics.createIndex(
  { slug: 1 },
  { unique: true }
);

db.topics.createIndex({
  parent_topic_id: 1,
  sort_order: 1
});
```

Topic content and examples can be expanded as the DSA library grows.

---

### 4.8 `social_accounts`

Stores metadata and protected credentials for connected social accounts.

V1 supports one Instagram Professional account per user.

#### Document structure

```json
{
  "_id": "ObjectId",
  "owner_id": "ObjectId",

  "platform": "instagram",
  "platform_user_id": "instagram_user_123",
  "username": "example_creator",
  "account_type": "professional",

  "connection_status": "connected",

  "credentials": {
    "encrypted_access_token": "ENCRYPTED_VALUE",
    "expires_at": "2026-12-01T00:00:00Z"
  },

  "created_at": "2026-11-24T12:00:00Z",
  "updated_at": "2026-11-24T12:00:00Z"
}
```

#### Rules

- Never request or store the user's Instagram password.
- Use official Meta authorization flows and supported APIs.
- Encrypt access and refresh tokens before database storage.
- Keep encryption keys outside MongoDB.
- Never expose credentials through API responses.
- Handle token expiration and revocation.
- Enforce one active account per user per platform in V1.

#### Indexes

```javascript
db.social_accounts.createIndex(
  {
    owner_id: 1,
    platform: 1
  },
  { unique: true }
);

db.social_accounts.createIndex({
  platform: 1,
  platform_user_id: 1
});
```

---

### 4.9 `publishing_jobs`

Represents a publishing or scheduling operation for an existing video.

Publishing is independent of video generation.

#### Document structure

```json
{
  "_id": "ObjectId",
  "owner_id": "ObjectId",

  "video_id": "ObjectId",
  "social_account_id": "ObjectId",

  "platform": "instagram",

  "mode": "approval_required",

  "status": "pending_approval",

  "caption": "Learn Two Sum visually!",
  "hashtags": [
    "DSA",
    "Coding"
  ],

  "scheduled_at": null,
  "published_at": null,

  "external_post_id": null,

  "retry_count": 0,

  "error": null,

  "idempotency_key": "unique_operation_key",

  "created_at": "2026-11-24T12:00:00Z",
  "updated_at": "2026-11-24T12:00:00Z"
}
```

#### Publishing modes

- `automatic`
- `approval_required`

#### Publishing statuses

- `pending_approval`
- `scheduled`
- `queued`
- `publishing`
- `published`
- `failed`
- `cancelled`

#### Rules

- A publishing job must reference an existing video.
- A publishing job must reference a connected social account belonging to the same owner.
- Do not publish videos that failed mandatory validation.
- A scheduled publishing operation must persist its schedule in MongoDB.
- Prevent duplicate publishing through idempotency keys and external post identifiers.
- Record failures and retry attempts.
- Do not assume that a successful API request means the post is published; confirm the provider's final status.

#### Indexes

```javascript
db.publishing_jobs.createIndex({
  owner_id: 1,
  created_at: -1
});

db.publishing_jobs.createIndex({
  status: 1,
  scheduled_at: 1
});

db.publishing_jobs.createIndex(
  {
    owner_id: 1,
    idempotency_key: 1
  },
  { unique: true }
);

db.publishing_jobs.createIndex({
  external_post_id: 1
});
```

---

### 4.10 `notifications`

Stores user-facing application notifications.

#### Document structure

```json
{
  "_id": "ObjectId",
  "owner_id": "ObjectId",

  "type": "video_generation_completed",

  "title": "Your video is ready",
  "message": "Two Sum Explained has been generated.",

  "resource_type": "video",
  "resource_id": "ObjectId",

  "is_read": false,

  "created_at": "2026-11-24T12:30:00Z"
}
```

#### Example notification types

- `video_generation_completed`
- `video_generation_failed`
- `publishing_completed`
- `publishing_failed`
- `scheduled_post_reminder`
- `social_account_disconnected`

#### Index

```javascript
db.notifications.createIndex({
  owner_id: 1,
  is_read: 1,
  created_at: -1
});
```

---

### 4.11 `audit_logs`

Stores important security and account activity.

#### Document structure

```json
{
  "_id": "ObjectId",
  "owner_id": "ObjectId",

  "action": "social_account_connected",

  "resource_type": "social_account",
  "resource_id": "ObjectId",

  "metadata": {
    "platform": "instagram"
  },

  "created_at": "2026-11-24T12:00:00Z"
}
```

Do not store access tokens, passwords, secrets, or sensitive personal information in audit logs.

#### Index

```javascript
db.audit_logs.createIndex({
  owner_id: 1,
  created_at: -1
});
```

---

### 4.12 `library_items` — Optional

Do not implement this collection in the initial prototype.

The `videos` collection already provides the basic content library.

Introduce `library_items` only when users need additional organization features such as:

- Custom folders
- Favorites
- User-defined tags
- Collections

A future schema can reference `video_id` and `owner_id` without duplicating video metadata.

---

## 5. Database Relationships

The main logical relationship is:

```text
USER
 |
 +---- USER_PREFERENCES
 |
 +---- GENERATION_JOBS
 |        |
 |        +---- ARTIFACTS
 |        |
 |        +---- JOB_EVENTS
 |        |
 |        +---- VIDEOS
 |                  |
 |                  +---- PUBLISHING_JOBS
 |
 +---- SOCIAL_ACCOUNTS
 |
 +---- NOTIFICATIONS
 |
 +---- AUDIT_LOGS
```
