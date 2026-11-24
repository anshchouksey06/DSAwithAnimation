# AI DSA Studio — Product Requirements Document (PRD)

**Document version:** 1.0
**Product:** AI DSA Studio
**Status:** Baseline product specification
**Initial prototype:** Prototype 1 — Two Sum
**Primary goal:** Convert Data Structures and Algorithms (DSA) concepts and coding problems into accurate, animated educational videos.

---

## 1. Product Overview

AI DSA Studio is an AI-powered platform that transforms DSA topics, coding problems, and custom learning prompts into short educational videos.

The platform combines AI-generated explanations with deterministic algorithm verification and programmatic animation. Each generated video can include:

- Clear problem or concept introduction.
- Step-by-step explanation.
- Brute-force and optimized approaches where applicable.
- Code examples in a selected programming language.
- Dry runs and visual demonstrations.
- Time and space complexity analysis.
- English narration.
- Synchronized subtitles.
- Animated visual elements.

The product has two major sections within one user account:

1. **Learning Studio:** Generate and consume educational DSA videos.
2. **Creator Studio:** Organize, schedule, approve, and publish videos to Instagram.

The first prototype will focus on generating a complete Two Sum educational video locally. Social publishing and the broader SaaS workflows will be developed after the core video pipeline is validated.

## 2. Product Objectives

### Primary objectives

- Make complex DSA concepts easier to understand visually.
- Generate technically accurate explanations and demonstrations.
- Reduce the manual effort required to create educational videos.
- Support multiple programming languages.
- Provide a repeatable video-generation pipeline.
- Enable creators to publish educational content consistently.

### Success criteria

The initial prototype should:

- Generate a complete Two Sum video from structured input.
- Explain both brute-force and hash-map approaches.
- Verify the algorithm outputs against test cases.
- Generate narration using a local TTS engine.
- Generate synchronized subtitles.
- Render a vertical MP4 using Remotion.
- Pass automated technical and media-quality checks.
- Save intermediate artifacts so failed stages can be retried independently.

## 3. Target Users

- Students learning DSA and preparing for technical interviews.
- Developers revising algorithms and problem-solving techniques.
- Educators creating programming tutorials.
- Technical content creators publishing educational short videos.

## 4. Product Structure

### 4.1 Learning Studio

Users can generate videos using three input methods.

#### A. Custom prompt

The user enters a topic or learning request.

Examples:

- Explain binary search visually.
- Teach recursion using a simple example.
- Explain the sliding window technique.

#### B. Topic library

The user selects a DSA topic from a categorized library.

Possible categories:

- Arrays and Strings
- Hashing
- Searching and Sorting
- Linked Lists
- Stacks and Queues
- Trees and Graphs
- Recursion and Backtracking
- Greedy Algorithms
- Dynamic Programming
- Heaps and Tries

#### C. Coding problem

The user provides:

- A supported problem URL.
- A problem name.
- A pasted problem statement.

The system normalizes the problem before generating an explanation.

### 4.2 Creator Studio

Creator Studio manages generated videos and Instagram publishing.

Features:

- Content library.
- Video history.
- Publishing calendar.
- Approval queue.
- Scheduled publishing.
- Automatic publishing.
- Publishing status.
- Basic available analytics.
- Notifications.
- Job history.
- Retry failed operations.
- Duplicate publishing prevention.

## 5. Video Generation Requirements

### 5.1 Duration

The AI recommends a duration based on problem complexity and explanation requirements.

Users can adjust the requested duration or range.

Correctness and completeness take priority over a rigid duration limit. The system must not remove essential explanations simply to meet a target duration.

### 5.2 Video format

Initial output:

| Property | Requirement |
|---|---|
| Aspect ratio | 9:16 |
| Resolution | 1080 × 1920 |
| Frame rate | 30 FPS |
| Container | MP4 |
| Video codec | H.264 |
| Audio codec | AAC |
| Narration | English |
| Subtitles | Synchronized |

### 5.3 Programming languages

Initial supported languages:

- C++
- Java
- Python
- JavaScript

Conceptual explanations must remain language-independent. Code examples and language-specific explanations should use the user's selected language.

### 5.4 Explanation requirements

For coding problems, the system should explain:

1. Problem statement in simple language.
2. Input, output, and constraints.
3. Important assumptions.
4. Brute-force approach.
5. Brute-force complexity.
6. Optimized approach.
7. Optimized complexity.
8. Step-by-step dry run.
9. Relevant code in the selected language.
10. Final summary and key takeaway.

For concept-based videos, the explanation should adapt to the topic rather than forcing a coding-problem structure.

### 5.5 Complexity analysis

Explain time and space complexity.

Distinguish:

- **Auxiliary space:** additional memory used by the algorithm.
- **Total space:** memory usage including input storage, where relevant.

Complexity claims must be based on algorithm analysis and structured metadata, not solely on successful test execution.

## 6. Technical Accuracy Requirements

Technical correctness is a core product requirement.

The system must validate:

- Problem interpretation.
- Input and output assumptions.
- Algorithm behavior.
- Code compilation or execution where applicable.
- Test-case results.
- Dry-run state transitions.
- Return values and indices.
- Complexity metadata.
- Scene-plan consistency with the explanation.

For supported coding problems, use automated tests and differential testing where appropriate.

A failed mandatory validation must block automatic publishing.

The system should:

1. Record the validation failure.
2. Identify the failing stage or check.
3. Attempt a controlled correction when supported.
4. Revalidate the corrected output.
5. Request human review when validation cannot be passed reliably.

The system must never mark an unverified explanation as technically verified.

## 7. Animation Requirements

Animations must be deterministic and programmatically rendered.

The platform should use reusable visual components rather than depending entirely on generic text-to-video generation.

Examples:

- Array and pointer visualization.
- Hash-map visualization.
- Variable and memory-state visualization.
- Comparison and search animations.
- Recursion visualization.
- Tree and graph traversal.
- Dynamic programming tables.

The AI may propose scene descriptions, but the renderer must only execute approved scene components and actions.

AI-generated arbitrary React or JavaScript must never be executed directly by the rendering system.

## 8. Narration and Subtitles

- English narration is required in V1.
- Prototype 1 must use a complete local voice-generation workflow.
- TTS must be accessed through a replaceable provider interface.
- Narration segments must have stable IDs.
- Audio timing must be retained in a timeline manifest.
- Subtitles must be synchronized with narration.
- Sentence-level subtitle timing is acceptable initially.
- Word-level timing may be introduced when reliable timestamps or forced alignment are available.

The system should retain the narration script, audio file, timing manifest, and subtitle file separately.

## 9. Instagram Publishing

Instagram integration will use the official Meta publishing APIs.

Requirements:

- One Instagram Professional account per user in V1.
- Support approval-required publishing.
- Support fully automatic publishing.
- Support scheduled publishing.
- Display publishing status and errors.
- Prevent duplicate publishing.
- Respect Meta account eligibility, permissions, API requirements, and publishing limits.

Security requirements:

- Never request or store an Instagram password.
- Use authorized OAuth-based access.
- Store tokens securely on the backend.
- Do not expose access tokens to the frontend.
- Handle token expiration and permission failures.

Publishing must be blocked if mandatory technical validation has failed.

## 10. User Workflows

### Workflow A: Generate from a custom prompt

1. User opens Learning Studio.
2. User enters a topic or prompt.
3. User selects a programming language if relevant.
4. User selects or adjusts the recommended duration.
5. System generates an explanation.
6. System validates the explanation.
7. System creates a scene plan.
8. System generates narration and subtitles.
9. Remotion renders the video.
10. FFmpeg assembles the final output.
11. QA validates the video.
12. Video appears in the user's library.

### Workflow B: Generate from a coding problem

1. User enters a URL, problem name, or problem statement.
2. System normalizes the problem.
3. System identifies constraints and assumptions.
4. System generates brute-force and optimized approaches where applicable.
5. System generates code and dry runs.
6. Verification engine validates the results.
7. Scene planner creates the animation plan.
8. Narration and subtitles are generated.
9. Video is rendered and assembled.
10. QA validates the final output.

### Workflow C: Publish to Instagram

1. User connects an eligible Instagram Professional account.
2. User selects a generated video.
3. User chooses automatic publishing or approval-required publishing.
4. User selects a publishing time or publishes immediately.
5. System validates publishing requirements.
6. System submits the media through the official API.
7. System records the result and updates publishing status.
8. User can view the publishing history.

## 11. Functional Requirements

| ID | Requirement |
|---|---|
| FR-01 | Users can access Learning Studio and Creator Studio from one account. |
| FR-02 | Users can generate videos using prompts, topics, or coding problems. |
| FR-03 | Users can select C++, Java, Python, or JavaScript for code examples. |
| FR-04 | The system generates structured explanations and approaches. |
| FR-05 | The system validates algorithm behavior and mandatory technical requirements. |
| FR-06 | The system generates a structured, validated scene plan. |
| FR-07 | The system generates English narration and synchronized subtitles. |
| FR-08 | The system renders vertical MP4 videos. |
| FR-09 | Users can view and manage generated videos. |
| FR-10 | Users can connect one eligible Instagram Professional account. |
| FR-11 | Users can approve, schedule, or automatically publish eligible videos. |
| FR-12 | The system records job status, failures, retries, and publishing history. |

## 12. Non-Functional Requirements

### Reliability

- Each generation stage must have explicit status.
- Failed stages must be identifiable.
- Retries must not create duplicate outputs or publishing operations.
- Intermediate artifacts should be reusable.

### Security

- Enforce user ownership checks on all user-owned records.
- Keep credentials and API tokens out of frontend code.
- Encrypt sensitive tokens at rest.
- Use isolated execution for user-supplied code.
- Apply resource limits and timeouts to code execution.

### Performance

- Video rendering must run in background workers, not in normal API request handlers.
- The API should return job identifiers for long-running operations.
- Users should be able to inspect generation progress.

### Maintainability

- Keep frontend, backend, and renderer independently deployable.
- Use versioned JSON contracts.
- Keep AI, TTS, rendering, storage, and publishing providers replaceable.

## 13. V1 Scope

### Included

- Learning Studio.
- Creator Studio foundations.
- Three video input methods.
- Four programming languages.
- Brute-force and optimized explanations where applicable.
- Dry runs.
- Complexity explanations.
- Deterministic animations.
- English narration.
- Subtitles.
- Vertical MP4 output.
- Content library and job history.
- Instagram integration for one Professional account.
- Automatic and approval-required publishing.
- Basic available analytics and notifications.

### Excluded from V1

- YouTube and TikTok publishing.
- Multiple social accounts per user.
- Subscription and payment systems.
- Team collaboration.
- Dedicated video editor.
- Advanced thumbnail editor.
- Multilingual narration.
- Advanced marketing analytics.

## 14. Prototype 1 Scope — Two Sum

Prototype 1 validates the end-to-end technical video pipeline.

### Input

- Problem: Two Sum.
- Example array: `[2, 7, 11, 15]`.
- Target: `9`.
- Language: C++ initially for the code example.

### Assumptions

- Exactly one valid solution exists.
- The same array element cannot be used twice.
- Return the two valid indices.

### Required approaches

**Brute force**

- Compare every valid pair.
- Return indices when their sum equals the target.
- Time: O(n²).
- Auxiliary space: O(1).

**Hash map**

- Iterate through the array.
- Calculate the complement.
- Check whether the complement has already been seen.
- Store the current value and index when no match is found.
- Return the matching indices.
- Average time: O(n).
- Auxiliary space: O(n).

### Required video sections

1. Intro.
2. Problem explanation.
3. Brute-force visualization.
4. Brute-force complexity.
5. Hash-map explanation.
6. Hash-map dry run.
7. Optimized complexity.
8. Code and summary.

The actual duration must follow the narration and completeness of the explanation. A target of approximately 90–120 seconds is a planning estimate, not a hard limit.

Prototype 1 does not require Instagram publishing. Its primary deliverable is a validated final MP4 and all intermediate artifacts.

## 15. Acceptance Criteria

Prototype 1 is complete when:

- The Two Sum input is normalized correctly.
- Both implementations return correct results for the defined test cases.
- Duplicate values and negative values are tested.
- Differential tests pass for generated valid inputs.
- Explanation and complexity metadata are consistent.
- The scene plan passes schema validation.
- Unsupported scene components are rejected.
- Local TTS produces narration audio.
- Subtitle timing is generated and checked.
- Remotion renders the silent video.
- FFmpeg creates the final MP4.
- The final video has the required format and dimensions.
- Automated QA reports pass or clearly identifies failures.
- All intermediate artifacts are saved independently.

## 16. Product Development Order

1. Finalize product requirements and documentation.
2. Finalize pipeline and contracts.
3. Implement Prototype 1 with deterministic Two Sum content.
4. Validate local TTS and Remotion rendering.
5. Add AI explanation and scene generation.
6. Add backend job orchestration and persistent job records.
7. Build the Learning Studio interface.
8. Add content library and history.
9. Build Creator Studio.
10. Integrate Instagram publishing.
11. Add scheduling, notifications, and analytics.

---

> **Product principle:** Technical accuracy and educational clarity take priority over generation speed and video duration.
