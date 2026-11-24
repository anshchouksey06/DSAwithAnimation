"""AI DSA Studio - Problem Normalizer
Transforms raw user input (prompt, topic name, or problem description) into a validated NormalizedProblem contract.
"""

import json
import os
import re
from typing import Dict, Any, Optional
import jsonschema

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "contracts", "problem.schema.json")

# Built-in catalog of algorithmic problems for deterministic & offline generation
CATALOG = {
    "two_sum": {
        "problem_id": "two-sum",
        "title": "Two Sum",
        "statement": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
        "input": {"nums": [2, 7, 11, 15]},
        "target": 9,
        "assumptions": [
            "Exactly one valid solution exists",
            "The same element cannot be used twice",
            "Return the answer in 0-based indices"
        ],
        "constraints": [
            "2 <= nums.length <= 10^4",
            "-10^9 <= nums[i] <= 10^9",
            "-10^9 <= target <= 10^9"
        ],
        "source_url": "https://leetcode.com/problems/two-sum/"
    },
    "binary_search": {
        "problem_id": "binary-search",
        "title": "Binary Search",
        "statement": "Given an array of integers nums sorted in ascending order and a target value, write a function to search target in nums. If target exists, return its index. Otherwise, return -1.",
        "input": {"nums": [-1, 0, 3, 5, 9, 12]},
        "target": 9,
        "assumptions": [
            "Array is strictly sorted in ascending order",
            "All elements in nums are unique",
            "Must achieve O(log n) runtime complexity"
        ],
        "constraints": [
            "1 <= nums.length <= 10^4",
            "-10^4 < nums[i], target < 10^4",
            "All elements in nums are unique and sorted"
        ],
        "source_url": "https://leetcode.com/problems/binary-search/"
    },
    "contains_duplicate": {
        "problem_id": "contains-duplicate",
        "title": "Contains Duplicate",
        "statement": "Given an integer array nums, return true if any value appears at least twice in the array, and return false if every element is distinct.",
        "input": {"nums": [1, 2, 3, 1]},
        "target": 0,
        "assumptions": [
            "Return boolean true/false",
            "Can use extra memory for fast lookup"
        ],
        "constraints": [
            "1 <= nums.length <= 10^5",
            "-10^9 <= nums[i] <= 10^9"
        ],
        "source_url": "https://leetcode.com/problems/contains-duplicate/"
    }
}

class ProblemNormalizer:
    def __init__(self, schema_path: str = SCHEMA_PATH):
        self.schema_path = os.path.abspath(schema_path)
        with open(self.schema_path, "r", encoding="utf-8") as f:
            self.schema = json.load(f)

    def normalize(
        self,
        input_type: str,
        prompt_or_title: Optional[str] = None,
        raw_problem: Optional[Dict[str, Any]] = None,
        language: str = "cpp"
    ) -> Dict[str, Any]:
        """Normalize any input into a schema-compliant NormalizedProblem dict."""
        language = language.lower()
        if language not in ["cpp", "java", "python", "javascript"]:
            language = "cpp"

        # 1. Match from prompt or title if given
        norm_key = None
        text_to_search = (prompt_or_title or "")
        if raw_problem and "title" in raw_problem:
            text_to_search += " " + raw_problem["title"]
        if raw_problem and "statement" in raw_problem:
            text_to_search += " " + raw_problem["statement"]

        clean_text = text_to_search.lower()
        if "binary search" in clean_text:
            norm_key = "binary_search"
        elif "duplicate" in clean_text:
            norm_key = "contains_duplicate"
        elif "two sum" in clean_text or "sum" in clean_text:
            norm_key = "two_sum"
        else:
            norm_key = "two_sum"

        base = CATALOG[norm_key].copy()

        # Overwrite with custom problem overrides if user provided them
        if raw_problem:
            if "title" in raw_problem and raw_problem["title"]:
                base["title"] = raw_problem["title"]
            if "statement" in raw_problem and raw_problem["statement"]:
                base["statement"] = raw_problem["statement"]
            if "input" in raw_problem and isinstance(raw_problem["input"], dict) and "nums" in raw_problem["input"]:
                base["input"] = raw_problem["input"]
            if "target" in raw_problem and raw_problem["target"] is not None:
                base["target"] = int(raw_problem["target"])

        normalized = {
            "schema_version": "1.0",
            "problem_id": base["problem_id"],
            "title": base["title"],
            "statement": base["statement"],
            "input": base["input"],
            "target": base["target"],
            "language": language,
            "assumptions": base["assumptions"],
            "constraints": base["constraints"],
            "source_url": base.get("source_url")
        }

        # Validate against schema
        jsonschema.validate(instance=normalized, schema=self.schema)
        return normalized

if __name__ == "__main__":
    normalizer = ProblemNormalizer()
    res = normalizer.normalize("prompt", "Teach me binary search in python", language="python")
    print(json.dumps(res, indent=2))
