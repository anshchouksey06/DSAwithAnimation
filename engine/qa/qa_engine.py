import os
import json
from typing import Dict, Any, List

def run_qa_checks(
    job_dir: str,
    final_video_path: str,
    validation_report_path: str,
    timeline_path: str,
    scene_plan_path: str
) -> Dict[str, Any]:
    errors: List[str] = []
    media_checks: List[Dict[str, Any]] = []
    content_checks: List[Dict[str, Any]] = []

    # Media Check 1: File existence and size
    video_exists = os.path.exists(final_video_path)
    video_size = os.path.getsize(final_video_path) if video_exists else 0
    if not video_exists or video_size < 1000:
        errors.append("Final MP4 is missing or suspiciously small.")
        media_checks.append({"name": "video_file_integrity", "status": "failed", "details": f"Size: {video_size} bytes"})
    else:
        media_checks.append({"name": "video_file_integrity", "status": "passed", "details": f"File size: {video_size} bytes"})

    # Content Check 1: Technical validation passed
    val_status = "unknown"
    if os.path.exists(validation_report_path):
        with open(validation_report_path, "r", encoding="utf-8") as f:
            val_data = json.load(f)
            val_status = val_data.get("status", "failed")
    if val_status == "passed":
        content_checks.append({"name": "technical_verification_passed", "status": "passed", "details": "Algorithm & tests verified"})
    else:
        errors.append("Technical verification failed or report missing.")
        content_checks.append({"name": "technical_verification_passed", "status": "failed", "details": f"Status: {val_status}"})

    # Content Check 2: Scene & Narration consistency
    if os.path.exists(timeline_path) and os.path.exists(scene_plan_path):
        with open(timeline_path, "r", encoding="utf-8") as f:
            timeline_data = json.load(f)
        with open(scene_plan_path, "r", encoding="utf-8") as f:
            scene_data = json.load(f)

        timeline_seg_ids = {s["segment_id"] for s in timeline_data.get("segments", [])}
        missing_segs = [sc["scene_id"] for sc in scene_data.get("scenes", []) if sc.get("narration_segment_id") not in timeline_seg_ids]

        if not missing_segs:
            content_checks.append({"name": "scene_narration_alignment", "status": "passed", "details": f"All {len(scene_data.get('scenes', []))} scenes aligned with audio"})
        else:
            errors.append(f"Scenes missing narration mapping: {missing_segs}")
            content_checks.append({"name": "scene_narration_alignment", "status": "failed", "details": f"Missing: {missing_segs}"})
    else:
        errors.append("Scene plan or timeline missing.")
        content_checks.append({"name": "scene_narration_alignment", "status": "failed", "details": "Metadata missing"})

    overall_status = "passed" if not errors else "failed"

    report = {
        "schema_version": "1.0",
        "status": overall_status,
        "media_checks": media_checks,
        "content_checks": content_checks,
        "errors": errors
    }

    qa_output_path = os.path.join(job_dir, "11_qa_report.json")
    with open(qa_output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return report
