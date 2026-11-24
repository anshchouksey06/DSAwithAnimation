from fastapi import FastAPI, HTTPException, BackgroundTasks, Header
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Literal
import os
import uuid
import datetime
import traceback

from engine.orchestrator import PipelineOrchestrator

app = FastAPI(
    title="AI DSA Studio API",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/api/v1/openapi.json"
)

# In-memory prototype store for Prototype 1
JOBS: Dict[str, Dict[str, Any]] = {}
VIDEOS: Dict[str, Dict[str, Any]] = {}
orchestrator = PipelineOrchestrator()

class VideoPreferences(BaseModel):
    aspect_ratio: Literal["9:16"] = "9:16"
    resolution: Literal["1080x1920"] = "1080x1920"
    narration_language: Literal["en"] = "en"
    subtitles_enabled: bool = True

class DurationPreference(BaseModel):
    mode: Literal["recommended", "target", "range"] = "recommended"
    target_seconds: Optional[int] = None

class GenerationRequest(BaseModel):
    input_type: Literal["prompt", "topic", "problem"]
    prompt: Optional[str] = None
    problem: Optional[Dict[str, Any]] = None
    programming_language: Literal["cpp", "java", "python", "javascript"] = "cpp"
    duration_preference: DurationPreference = Field(default_factory=DurationPreference)
    video_preferences: VideoPreferences = Field(default_factory=VideoPreferences)

@app.get("/api/v1/health")
def health_check():
    return {
        "success": True,
        "data": {
            "status": "ok",
            "service": "ai-dsa-studio-api",
            "version": "1.0.0"
        }
    }

def run_job_background(job_id: str):
    JOBS[job_id]["status"] = "processing"
    JOBS[job_id]["current_stage"] = "technical_verification"
    job_input = JOBS[job_id].get("input", {})
    prompt = job_input.get("prompt")
    raw_problem = job_input.get("problem")
    lang = job_input.get("programming_language", "cpp")
    try:
        res = orchestrator.run_pipeline(
            job_id=job_id,
            prompt=prompt,
            raw_problem=raw_problem,
            language=lang,
            skip_render=True
        )
        JOBS[job_id]["status"] = "completed"
        JOBS[job_id]["current_stage"] = "completed"
        JOBS[job_id]["completed_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        video_id = f"video_{uuid.uuid4().hex[:8]}"
        JOBS[job_id]["result_video_id"] = video_id
        
        title = "DSA Problem"
        if raw_problem and "title" in raw_problem:
            title = raw_problem["title"]
        elif prompt:
            title = prompt

        VIDEOS[video_id] = {
            "video_id": video_id,
            "job_id": job_id,
            "title": title,
            "programming_language": lang,
            "status": "ready",
            "duration_seconds": 74,
            "validation_status": res["validation_status"],
            "qa_status": res["qa_status"],
            "artifacts_dir": res["job_dir"]
        }
    except Exception as e:
        JOBS[job_id]["status"] = "failed"
        JOBS[job_id]["error"] = str(e)
        JOBS[job_id]["traceback"] = traceback.format_exc()

@app.post("/api/v1/generations", status_code=202)
def create_generation(request: GenerationRequest, background_tasks: BackgroundTasks, idempotency_key: Optional[str] = Header(None)):
    job_id = f"job_{uuid.uuid4().hex[:8]}"
    JOBS[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "current_stage": "input_processing",
        "input": request.model_dump(),
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "error": None
    }
    background_tasks.add_task(run_job_background, job_id)
    return {
        "success": True,
        "data": {
            "job_id": job_id,
            "status": "queued",
            "message": "Video generation has been queued"
        }
    }

@app.get("/api/v1/generations/{job_id}")
def get_generation_status(job_id: str):
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "success": True,
        "data": JOBS[job_id]
    }

@app.get("/api/v1/videos/{video_id}")
def get_video(video_id: str):
    if video_id not in VIDEOS:
        raise HTTPException(status_code=404, detail="Video not found")
    return {
        "success": True,
        "data": VIDEOS[video_id]
    }

@app.get("/api/v1/videos/{video_id}/artifacts")
def list_video_artifacts(video_id: str):
    if video_id not in VIDEOS:
        raise HTTPException(status_code=404, detail="Video not found")
    v = VIDEOS[video_id]
    job_dir = v["artifacts_dir"]
    artifacts = []
    if os.path.exists(job_dir):
        for fname in sorted(os.listdir(job_dir)):
            fpath = os.path.join(job_dir, fname)
            if os.path.isfile(fpath):
                artifacts.append({
                    "name": fname,
                    "size_bytes": os.path.getsize(fpath),
                    "path": fpath.replace("\\", "/")
                })
    return {
        "success": True,
        "data": artifacts
    }

@app.get("/api/v1/artifacts/{artifact_id}/download")
def download_artifact(artifact_id: str, path: str):
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Artifact file not found")
    return FileResponse(path, filename=os.path.basename(path))
