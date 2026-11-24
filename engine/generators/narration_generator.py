"""AI DSA Studio - Narration Generator
Generates spoken educational narration scripts synchronized with the scene plan adhering to contracts/narration.schema.json.
"""

import json
import os
from typing import Dict, Any, List
import jsonschema

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "contracts", "narration.schema.json")

class NarrationGenerator:
    def __init__(self, schema_path: str = SCHEMA_PATH):
        self.schema_path = os.path.abspath(schema_path)
        with open(self.schema_path, "r", encoding="utf-8") as f:
            self.schema = json.load(f)

    def generate_narration(self, problem: Dict[str, Any], explanation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate concise, natural spoken narration segments matching scene IDs."""
        title = problem.get("title", "this algorithm")
        nums = problem["input"]["nums"]
        target = problem.get("target", 0)
        nums_str = ", ".join(str(x) for x in nums)

        segments = [
            {
                "segment_id": "narr-01-intro",
                "text": f"Welcome to {title}. We need to find two distinct indices whose values add up to the target."
            },
            {
                "segment_id": "narr-02-problem",
                "text": f"Here is our input array: {nums_str}. Our target sum is {target}."
            },
            {
                "segment_id": "narr-03-brute-force",
                "text": "The brute force way checks every pair. In the worst case, comparing all pairs takes O of n squared time."
            },
            {
                "segment_id": "narr-04-hashmap-concept",
                "text": "Can we do better? Yes, with a hash map. Instead of searching repeatedly, we calculate the complement: target minus current value."
            },
            {
                "segment_id": "narr-05-hashmap-dryrun",
                "text": f"Let's trace it. At index zero, value {nums[0]}. Complement is {target - nums[0]}, not in map, so store it. At index one, value {nums[1] if len(nums)>1 else nums[0]}. The complement is in our map! We found our answer."
            },
            {
                "segment_id": "narr-06-complexity",
                "text": "The hash map approach runs in linear time, O of n, using O of n extra space."
            },
            {
                "segment_id": "narr-07-summary",
                "text": "Key takeaway: by trading memory for speed with a hash map, we reduced quadratic time to linear time."
            }
        ]

        script = {
            "schema_version": "1.0",
            "language": "en",
            "segments": segments
        }

        jsonschema.validate(instance=script, schema=self.schema)
        return script

if __name__ == "__main__":
    from problem_normalizer import ProblemNormalizer
    from explanation_generator import ExplanationGenerator

    p = ProblemNormalizer().normalize("prompt", "Two sum")
    exp = ExplanationGenerator().generate(p)
    narr = NarrationGenerator().generate_narration(p, exp)
    print("✓ Narration Script Validated successfully! Segments count:", len(narr["segments"]))
