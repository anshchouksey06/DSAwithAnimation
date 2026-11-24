"""AI DSA Studio - Scene Planner
Generates structured 9:16 scene plans adhering to contracts/scene-plan.schema.json.
"""

import json
import os
from typing import Dict, Any, List
import jsonschema

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "contracts", "scene-plan.schema.json")

class ScenePlanner:
    def __init__(self, schema_path: str = SCHEMA_PATH):
        self.schema_path = os.path.abspath(schema_path)
        with open(self.schema_path, "r", encoding="utf-8") as f:
            self.schema = json.load(f)

    def plan_scenes(self, problem: Dict[str, Any], explanation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a 9:16 scene plan using allowed deterministic visual components."""
        title = problem.get("title", "Algorithm Explained")
        nums = problem["input"]["nums"]
        target = problem.get("target", 0)

        scenes = [
            {
                "scene_id": "scene-01-intro",
                "component": "IntroScene",
                "props": {
                    "title": title,
                    "subtitle": "Brute Force vs Optimized Visualized",
                    "category": "Data Structures & Algorithms"
                },
                "narration_segment_id": "narr-01-intro",
                "duration_frames": 219
            },
            {
                "scene_id": "scene-02-problem",
                "component": "ArrayScene",
                "props": {
                    "label": "Input Array & Target",
                    "array": nums,
                    "target": target,
                    "highlightIndices": []
                },
                "narration_segment_id": "narr-02-problem",
                "duration_frames": 234
            },
            {
                "scene_id": "scene-03-brute-force",
                "component": "BruteForceScene",
                "props": {
                    "array": nums,
                    "target": target,
                    "currentI": 0,
                    "currentJ": 1,
                    "currentSum": (nums[0] if len(nums) > 0 else 0) + (nums[1] if len(nums) > 1 else 0),
                    "found": True
                },
                "narration_segment_id": "narr-03-brute-force",
                "duration_frames": 295
            },
            {
                "scene_id": "scene-04-hashmap-concept",
                "component": "ArrayScene",
                "props": {
                    "label": "The Complement Principle",
                    "array": nums,
                    "target": target,
                    "highlightIndices": [0]
                },
                "narration_segment_id": "narr-04-hashmap-concept",
                "duration_frames": 344
            },
            {
                "scene_id": "scene-05-hashmap-dryrun",
                "component": "HashMapScene",
                "props": {
                    "array": nums,
                    "target": target,
                    "activeStep": 2,
                    "mapEntries": [
                        {"key": str(nums[0]), "val": 0}
                    ],
                    "complement": target - (nums[1] if len(nums) > 1 else nums[0]),
                    "foundMatch": True,
                    "resultIndices": [0, 1]
                },
                "narration_segment_id": "narr-05-hashmap-dryrun",
                "duration_frames": 688
            },
            {
                "scene_id": "scene-06-complexity",
                "component": "ComplexityScene",
                "props": {
                    "bruteForceTime": "O(n^2)",
                    "bruteForceSpace": "O(1)",
                    "optimizedTime": "O(n)",
                    "optimizedSpace": "O(n)"
                },
                "narration_segment_id": "narr-06-complexity",
                "duration_frames": 207
            },
            {
                "scene_id": "scene-07-summary",
                "component": "SummaryScene",
                "props": {
                    "problemTitle": title,
                    "takeaway": "Trading O(n) memory with a hash table eliminates redundant nested loops."
                },
                "narration_segment_id": "narr-07-summary",
                "duration_frames": 233
            }
        ]

        scene_plan = {
            "schema_version": "1.0",
            "aspect_ratio": "9:16",
            "fps": 30,
            "scenes": scenes
        }

        jsonschema.validate(instance=scene_plan, schema=self.schema)
        return scene_plan

if __name__ == "__main__":
    from problem_normalizer import ProblemNormalizer
    from explanation_generator import ExplanationGenerator

    p = ProblemNormalizer().normalize("prompt", "Two sum")
    exp = ExplanationGenerator().generate(p)
    sp = ScenePlanner().plan_scenes(p, exp)
    print("✓ Scene Plan Validated successfully! Scenes count:", len(sp["scenes"]))
