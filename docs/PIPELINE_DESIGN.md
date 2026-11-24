# AI DSA Studio — Video Generation Pipeline Design

**Document version:** 1.0
**Applies to:** Prototype 1 and future V1 pipeline
**Prototype problem:** Two Sum
**Renderer:** Remotion
**Narration:** Local TTS
**Generation strategy:** Hybrid AI + deterministic verification and rendering

---

## 1. Purpose

This document defines how AI DSA Studio transforms a DSA topic or coding problem into a technically validated educational video.

The pipeline must be modular. Each stage receives a structured input, performs one responsibility, and produces a structured output or artifact.

A failed stage must be retryable without unnecessarily regenerating successful earlier stages.

## 2. Core Design Principle

**AI proposes explanations and scenes. Deterministic systems validate the content and render the video.**

The AI must not directly produce executable animation code.

Instead:

1. AI generates structured explanation data.
2. Verification checks the algorithm and explanation.
3. AI or deterministic logic proposes a scene plan.
4. Schema validation and an allowlist restrict the scene plan.
5. Remotion renders approved visual components.
6. FFmpeg assembles video, audio, and subtitles.

This provides flexibility without allowing uncontrolled generated code to run inside the renderer.

## 3. Pipeline Overview

```text
User Input
    |
    v
Input Ingestion
    |
    v
Problem Normalization
    |
    v
Explanation Generation
    |
    v
Technical Verification
    |
    v
Scene Planning
    |
    v
Scene Plan Validation
    |
    v
Narration Script Generation
    |
    v
Local TTS Generation
    |
    v
Audio Timing + Subtitle Generation
    |
    v
Remotion Rendering
    |
    v
FFmpeg Assembly
    |
    v
Final Video QA
    |
    v
Video Artifact + Metadata
```

Each stage should have an independent status and output artifact.

## 4. Pipeline Layers

### Layer A — Intelligence

Responsible for:

- Understanding the user's input.
- Normalizing coding problems.
- Generating explanations.
- Producing code examples.
- Producing dry-run states.
- Proposing visual scenes.
- Generating narration scripts.

AI output must follow versioned JSON contracts.

### Layer B — Verification

Responsible for:

- Validating problem assumptions.
- Testing algorithm implementations.
- Checking dry-run state transitions.
- Comparing brute-force and optimized outputs.
- Checking complexity metadata against algorithm analysis.
- Validating scene references and narration references.

Mandatory validation failures must stop automatic progression to publishing.

### Layer C — Visual Production

Responsible for:

- Local voice generation.
- Audio timing.
- Subtitle generation.
- Deterministic animation.
- Video rendering.
- Audio and video assembly.

### Layer D — Delivery

Responsible for:

- Final media QA.
- Artifact storage.
- Job completion status.
- Preview and download availability.
- Later: publishing and scheduling.

## 5. Component Contracts

| Component | Input | Output |
|---|---|---|
| Problem Processor | User input | Normalized problem JSON |
| Explanation Engine | Normalized problem | Explanation JSON |
| Verification Engine | Explanation, code, test cases | Validation report |
| Scene Planner | Validated explanation | Scene plan JSON |
| Narration Generator | Explanation and scene plan | Narration script JSON |
| TTS Service | Narration segments | Audio files and timing manifest |
| Subtitle Generator | Narration timing | SRT subtitle file |
| Remotion Renderer | Scene plan and assets | Silent video |
| FFmpeg Assembler | Silent video, audio, subtitles | Final MP4 |
| QA Engine | Final MP4 and validation report | QA report |

Each component should expose a clear interface and avoid hidden dependencies on other components' internal implementation.

## 6. Stage 1 — Input Ingestion

Supported input types:

- Custom prompt.
- Topic library selection.
- Coding problem URL.
- Coding problem name.
- Pasted problem statement.

The input layer should capture:

- Input type.
- Raw input.
- Selected programming language.
- Requested duration or range, if supplied.
- User preferences relevant to the video.
- Input source metadata.

Do not assume that every URL is accessible. If extraction fails, ask for or accept a pasted problem statement.

## 7. Stage 2 — Problem Normalization

Convert raw input into a canonical problem representation.

Example:

```json
{
  "schema_version": "1.0",
  "problem_id": "two-sum",
  "title": "Two Sum",
  "input": {
    "nums": [2, 7, 11, 15],
    "target": 9
  },
  "language": "cpp",
  "assumptions": [
    "Exactly one valid solution exists",
    "The same element cannot be used twice"
  ]
}
```

The normalized problem must include:

- Stable problem ID.
- Title.
- Problem statement.
- Input structure.
- Output structure.
- Constraints.
- Assumptions.
- Selected programming language.
- Source metadata where available.

If important information is missing or ambiguous, the system must not silently invent it.

## 8. Stage 3 — Explanation Generation

Generate structured explanations rather than a single unstructured block of text.

For coding problems, include:

- Problem summary.
- Key observations.
- Brute-force approach.
- Optimized approach.
- Pseudocode.
- Language-specific code.
- Complexity analysis.
- Dry-run steps.
- Narration content.

Example explanation structure:

```json
{
  "schema_version": "1.0",
  "problem_id": "two-sum",
  "approaches": [
    {
      "id": "brute-force",
      "name": "Brute Force",
      "time_complexity": "O(n^2)",
      "auxiliary_space": "O(1)"
    },
    {
      "id": "hash-map",
      "name": "Hash Map",
      "time_complexity": "O(n) average",
      "auxiliary_space": "O(n)"
    }
  ]
}
```

This is an illustrative minimum. The production schema must also define pseudocode, code, dry-run states, assumptions, and narration references.

## 9. Stage 4 — Technical Verification

Verification must be independent of the AI explanation generator.

### 9.1 Algorithm tests

For Two Sum:

- Test the standard example.
- Test duplicate values.
- Test negative values.
- Test a solution at the beginning or end of the array.
- Test boundary cases permitted by the problem constraints.

### 9.2 Differential testing

Run the brute-force and optimized implementations on the same valid generated inputs.

Compare whether:

- Both find a valid solution.
- Both return valid indices.
- The returned indices are distinct.
- The selected values sum to the target.

Do not require the two implementations to return the exact same pair if multiple valid answers are allowed.

For the initial Two Sum contract, exactly one solution is assumed.

### 9.3 Dry-run validation

A dry run is represented as a sequence of state transitions.

For the hash-map approach:

```text
Initial:
nums = [2, 7, 11, 15]
target = 9
seen = {}

Step 1:
value = 2
complement = 7
7 is not in seen
seen = {2: 0}

Step 2:
value = 7
complement = 2
2 is in seen
return [0, 1]
```

The verifier should check that each transition follows the algorithm's rules.

### 9.4 Complexity validation

Complexity is not proven by a collection of test runs.

Use:

- Algorithm metadata.
- Known algorithmic rules.
- Structured complexity declarations.
- Static review or explicit validation rules.

For Two Sum:

- Brute force: O(n²) time, O(1) auxiliary space.
- Hash map: O(n) average time, O(n) auxiliary space.

### 9.5 Validation report

Every validation stage should produce a structured report.

Example:

```json
{
  "schema_version": "1.0",
  "status": "passed",
  "checks": [
    {
      "name": "brute_force_tests",
      "status": "passed"
    },
    {
      "name": "optimized_tests",
      "status": "passed"
    },
    {
      "name": "dry_run_consistency",
      "status": "passed"
    },
    {
      "name": "complexity_metadata",
      "status": "passed"
    }
  ],
  "errors": []
}
```

A failed mandatory check must block the next mandatory production stage.

## 10. Stage 5 — Scene Planning

Convert the validated explanation into a structured scene plan.

The scene plan must describe:

- Scene ID.
- Component type.
- Scene properties.
- Visual state.
- Timeline or duration information.
- Narration segment references.
- Approved animation actions.

### Initial scene allowlist

Prototype 1 supports:

- `IntroScene`
- `ArrayScene`
- `BruteForceScene`
- `ComplexityScene`
- `HashMapScene`
- `SummaryScene`

The renderer must reject:

- Unknown component types.
- Unknown actions.
- Invalid properties.
- Invalid narration references.
- Invalid timing data.

The AI cannot add arbitrary components or execute generated code.

### Example scene-plan fragment

```json
{
  "schema_version": "1.0",
  "scenes": [
    {
      "scene_id": "intro",
      "component": "IntroScene",
      "props": {
        "title": "Two Sum",
        "subtitle": "Find two numbers that add up to a target"
      },
      "narration_segment_id": "narration-001"
    },
    {
      "scene_id": "array-example",
      "component": "ArrayScene",
      "props": {
        "values": [2, 7, 11, 15],
        "target": 9
      },
      "narration_segment_id": "narration-002"
    }
  ]
}
```

The final schema must define exact property types, timing semantics, and permitted actions.

## 11. Stage 6 — Narration Script Generation

Narration should be split into stable segments.

Example:

```json
{
  "schema_version": "1.0",
  "segments": [
    {
      "segment_id": "narration-001",
      "text": "Let's understand the Two Sum problem."
    },
    {
      "segment_id": "narration-002",
      "text": "We need to find two different indices whose values add up to the target."
    }
  ]
}
```

Requirements:

- Clear spoken English.
- Short, understandable sentences.
- Correct technical terminology.
- No unsupported claims.
- Narration aligned with the corresponding visual scene.
- Stable segment IDs.

## 12. Stage 7 — Local TTS Generation

Prototype 1 must use a complete local voice-generation workflow.

Piper is the initial candidate for local TTS.

Before selecting a specific voice model, verify:

- Installation compatibility.
- Voice quality.
- Supported operating system.
- Model availability.
- Model and voice licensing.
- Commercial-use restrictions, if applicable.

Use a provider interface so the TTS engine can be replaced without changing the rest of the pipeline.

Suggested interface:

```python
from abc import ABC, abstractmethod

class TTSProvider(ABC):
    @abstractmethod
    def generate(self, text: str, output_path: str):
        """Generate speech audio from text."""
        raise NotImplementedError
```

The TTS adapter should:

- Accept a narration segment.
- Generate audio locally.
- Return the output path and available timing metadata.
- Report errors explicitly.

Store audio per segment or in a combined file with a segment timing manifest.

## 13. Stage 8 — Audio Timing and Subtitles

Audio timing is authoritative for the final narration.

Do not force narration into arbitrary fixed scene durations.

The system should:

1. Generate audio.
2. Determine segment durations.
3. Build a timeline manifest.
4. Assign scenes to corresponding narration segments.
5. Generate subtitles from the same narration text and timing data.

Initial subtitle timing can be sentence-level.

Word-level timing should be introduced only when reliable timestamps or forced alignment are available.

Outputs:

- Narration audio.
- Narration timeline JSON.
- SRT subtitles.

## 14. Stage 9 — Remotion Rendering

Remotion renders approved scene components using the validated scene plan.

Rendering requirements:

- Vertical 9:16.
- 1080 × 1920.
- 30 FPS.
- Deterministic visual output.
- Reusable React scene components.
- No execution of AI-generated arbitrary code.

For Prototype 1, build reusable components for:

- Titles and text.
- Arrays and indexes.
- Pointer movement.
- Pair comparisons.
- Hash-map entries.
- Complexity cards.
- Summary screens.

The renderer initially produces a silent video.

## 15. Stage 10 — FFmpeg Assembly

FFmpeg combines:

- Silent rendered video.
- Narration audio.
- Subtitle track or burned-in subtitles.

The assembly stage must:

- Preserve the required resolution.
- Preserve the intended aspect ratio.
- Use H.264 video.
- Use AAC audio.
- Handle audio/video duration differences.
- Avoid unintended clipping or silence.
- Produce a playable MP4.

Keep subtitle output separately even if subtitles are burned into the final video.

## 16. Stage 11 — Final QA

The QA engine should check:

### Media checks

- MP4 exists and can be decoded.
- Resolution is 1080 × 1920.
- Frame rate is 30 FPS.
- Audio is present.
- Duration is valid.
- No unexpected blank or corrupted output.

### Content checks

- Required scenes are present.
- Narration references resolve.
- Subtitles reference valid narration segments.
- Final video corresponds to the validated scene plan.
- Mandatory technical validation passed.

### QA report

```json
{
  "schema_version": "1.0",
  "status": "passed",
  "media_checks": [],
  "content_checks": [],
  "errors": []
}
```

Do not automatically publish a video if mandatory QA or technical validation fails.

## 17. Artifact Management

Each stage should save its output independently.

Suggested structure:

```text
output/
└── two-sum-job-001/
    ├── 01_problem.json
    ├── 02_explanation.json
    ├── 03_validation.json
    ├── 04_scene_plan.json
    ├── 05_narration_script.json
    ├── 06_narration.wav
    ├── 07_narration_timeline.json
    ├── 08_subtitles.srt
    ├── 09_silent_video.mp4
    ├── 10_final_video.mp4
    └── 11_qa_report.json
```

Keep intermediate files so:

- TTS can be retried without regenerating the explanation.
- Rendering can be retried without regenerating audio.
- QA can be rerun without repeating the entire pipeline.

Use hashes or equivalent artifact fingerprints to identify reusable outputs.

## 18. Job States

Suggested job states:

```text
CREATED
  |
  v
PROCESSING_INPUT
  |
  v
GENERATING_EXPLANATION
  |
  v
VERIFYING
  |
  v
PLANNING_SCENES
  |
  v
GENERATING_NARRATION
  |
  v
GENERATING_AUDIO
  |
  v
RENDERING
  |
  v
ASSEMBLING
  |
  v
QUALITY_CHECK
  |
  v
COMPLETED
```

Any stage may transition to a failure state.

A retry should restart from the failed stage when its required upstream artifacts remain valid.

## 19. Prototype 1 Implementation Strategy

Build in controlled steps:

1. Create the Two Sum problem fixture.
2. Implement brute-force and hash-map algorithms.
3. Add deterministic tests and differential testing.
4. Create a verified explanation fixture.
5. Validate the explanation against its schema.
6. Create the first scene-plan fixture.
7. Implement the local TTS adapter.
8. Generate narration audio and subtitle timing.
9. Implement the Remotion scene components.
10. Render the silent video.
11. Assemble the final MP4 with FFmpeg.
12. Run media and content QA.

Only after the deterministic end-to-end pipeline works should AI-generated explanations and scene plans replace the initial fixtures.

This is a sequencing strategy for reliability, not a decision to remove AI from the product.

## 20. Pipeline Definition of Done

Prototype 1 is complete when:

- Every stage has a defined input and output.
- JSON contracts validate successfully.
- Algorithm tests pass.
- The explanation and dry run are consistent.
- Local TTS produces usable narration.
- Subtitle timing is generated.
- Remotion renders the scenes.
- FFmpeg produces a valid MP4.
- Final QA passes.
- Intermediate artifacts are retained.
- Failed stages can be retried independently.

---

> **Pipeline principle:** Generate structured content, verify it independently, render it deterministically, and preserve every important intermediate artifact.
