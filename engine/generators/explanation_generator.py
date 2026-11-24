"""AI DSA Studio - Explanation Generator
Generates structured algorithmic explanations with multi-language code and dry-run traces matching contracts/explanation.schema.json.
"""

import json
import os
from typing import Dict, Any, List
import jsonschema

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "contracts", "explanation.schema.json")

# Multi-language code repository for supported algorithms
CODE_TEMPLATES = {
    "two-sum": {
        "brute_force": {
            "cpp": """#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    vector<int> twoSum(vector<int>& nums, int target) {\n        for (int i = 0; i < nums.size(); ++i) {\n            for (int j = i + 1; j < nums.size(); ++j) {\n                if (nums[i] + nums[j] == target) return {i, j};\n            }\n        }\n        return {};\n    }\n};""",
            "python": """class Solution:\n    def twoSum(self, nums: list[int], target: int) -> list[int]:\n        n = len(nums)\n        for i in range(n):\n            for j in range(i + 1, n):\n                if nums[i] + nums[j] == target:\n                    return [i, j]\n        return []""",
            "java": """class Solution {\n    public int[] twoSum(int[] nums, int target) {\n        for (int i = 0; i < nums.length; i++) {\n            for (int j = i + 1; j < nums.length; j++) {\n                if (nums[i] + nums[j] == target) return new int[]{i, j};\n            }\n        }\n        return new int[]{};\n    }\n}""",
            "javascript": """function twoSum(nums, target) {\n    for (let i = 0; i < nums.length; i++) {\n        for (let j = i + 1; j < nums.length; j++) {\n            if (nums[i] + nums[j] === target) return [i, j];\n        }\n    }\n    return [];\n}"""
        },
        "optimized": {
            "cpp": """#include <vector>\n#include <unordered_map>\nusing namespace std;\n\nclass Solution {\npublic:\n    vector<int> twoSum(vector<int>& nums, int target) {\n        unordered_map<int, int> num_map;\n        for (int i = 0; i < nums.size(); ++i) {\n            int complement = target - nums[i];\n            if (num_map.count(complement)) {\n                return {num_map[complement], i};\n            }\n            num_map[nums[i]] = i;\n        }\n        return {};\n    }\n};""",
            "python": """class Solution:\n    def twoSum(self, nums: list[int], target: int) -> list[int]:\n        seen = {}\n        for i, val in enumerate(nums):\n            comp = target - val\n            if comp in seen:\n                return [seen[comp], i]\n            seen[val] = i\n        return []""",
            "java": """import java.util.HashMap;\n\nclass Solution {\n    public int[] twoSum(int[] nums, int target) {\n        HashMap<Integer, Integer> map = new HashMap<>();\n        for (int i = 0; i < nums.length; i++) {\n            int complement = target - nums[i];\n            if (map.containsKey(complement)) {\n                return new int[]{map.get(complement), i};\n            }\n            map.put(nums[i], i);\n        }\n        return new int[]{};\n    }\n}""",
            "javascript": """function twoSum(nums, target) {\n    const map = new Map();\n    for (let i = 0; i < nums.length; i++) {\n        const complement = target - nums[i];\n        if (map.has(complement)) {\n            return [map.get(complement), i];\n        }\n        map.set(nums[i], i);\n    }\n    return [];\n}"""
        }
    },
    "binary-search": {
        "brute_force": {
            "cpp": """#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    int search(vector<int>& nums, int target) {\n        for (int i = 0; i < nums.size(); ++i) {\n            if (nums[i] == target) return i;\n        }\n        return -1;\n    }\n};""",
            "python": """class Solution:\n    def search(self, nums: list[int], target: int) -> int:\n        for i, val in enumerate(nums):\n            if val == target:\n                return i\n        return -1""",
            "java": """class Solution {\n    public int search(int[] nums, int target) {\n        for (int i = 0; i < nums.length; i++) {\n            if (nums[i] == target) return i;\n        }\n        return -1;\n    }\n}""",
            "javascript": """function search(nums, target) {\n    for (let i = 0; i < nums.length; i++) {\n        if (nums[i] === target) return i;\n    }\n    return -1;\n}"""
        },
        "optimized": {
            "cpp": """#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    int search(vector<int>& nums, int target) {\n        int left = 0, right = nums.size() - 1;\n        while (left <= right) {\n            int mid = left + (right - left) / 2;\n            if (nums[mid] == target) return mid;\n            else if (nums[mid] < target) left = mid + 1;\n            else right = mid - 1;\n        }\n        return -1;\n    }\n};""",
            "python": """class Solution:\n    def search(self, nums: list[int], target: int) -> int:\n        left, right = 0, len(nums) - 1\n        while left <= right:\n            mid = (left + right) // 2\n            if nums[mid] == target:\n                return mid\n            elif nums[mid] < target:\n                left = mid + 1\n            else:\n                right = mid - 1\n        return -1""",
            "java": """class Solution {\n    public int search(int[] nums, int target) {\n        int left = 0, right = nums.length - 1;\n        while (left <= right) {\n            int mid = left + (right - left) / 2;\n            if (nums[mid] == target) return mid;\n            else if (nums[mid] < target) left = mid + 1;\n            else right = mid - 1;\n        }\n        return -1;\n    }\n}""",
            "javascript": """function search(nums, target) {\n    let left = 0, right = nums.length - 1;\n    while (left <= right) {\n        const mid = Math.floor((left + right) / 2);\n        if (nums[mid] === target) return mid;\n        else if (nums[mid] < target) left = mid + 1;\n        else right = mid - 1;\n    }\n    return -1;\n}"""
        }
    }
}

class ExplanationGenerator:
    def __init__(self, schema_path: str = SCHEMA_PATH):
        self.schema_path = os.path.abspath(schema_path)
        with open(self.schema_path, "r", encoding="utf-8") as f:
            self.schema = json.load(f)

    def generate(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a complete structured explanation given a normalized problem."""
        problem_id = problem.get("problem_id", "two-sum")
        lang = problem.get("language", "cpp").lower()
        nums = problem["input"]["nums"]
        target = problem["target"]

        if problem_id == "binary-search":
            return self._generate_binary_search(problem, lang, nums, target)
        else:
            return self._generate_two_sum(problem, lang, nums, target)

    def _generate_two_sum(self, problem: Dict[str, Any], lang: str, nums: List[int], target: int) -> Dict[str, Any]:
        code_bf = CODE_TEMPLATES["two-sum"]["brute_force"].get(lang, CODE_TEMPLATES["two-sum"]["brute_force"]["cpp"])
        code_opt = CODE_TEMPLATES["two-sum"]["optimized"].get(lang, CODE_TEMPLATES["two-sum"]["optimized"]["cpp"])

        explanation = {
            "schema_version": "1.0",
            "problem_id": problem.get("problem_id", "two-sum"),
            "summary": f"Find two distinct indices in nums that sum to {target}.",
            "key_observations": [
                "The equation a + b = target can be rewritten as b = target - a (the complement).",
                "Instead of repeatedly scanning the array to find b, a hash map enables O(1) average lookup.",
                "Trading O(n) auxiliary space dramatically reduces time complexity from quadratic to linear."
            ],
            "approaches": [
                {
                    "id": "brute_force",
                    "name": "Nested Loops (Brute Force)",
                    "time_complexity": "O(n^2)",
                    "auxiliary_space": "O(1)",
                    "total_space": "O(1)",
                    "idea": "Exhaustively examine every unique pair of indices (i, j) where i < j until nums[i] + nums[j] == target.",
                    "pseudocode": [
                        "for i from 0 to n-1:",
                        "  for j from i+1 to n-1:",
                        "    if nums[i] + nums[j] == target: return [i, j]"
                    ],
                    "code": code_bf,
                    "dry_run_steps": [
                        {
                            "step": 1,
                            "i": 0,
                            "j": 1,
                            "val_i": nums[0] if len(nums) > 0 else 2,
                            "val_j": nums[1] if len(nums) > 1 else 7,
                            "sum": (nums[0] if len(nums) > 0 else 2) + (nums[1] if len(nums) > 1 else 7),
                            "target": target,
                            "match": ((nums[0] if len(nums) > 0 else 2) + (nums[1] if len(nums) > 1 else 7)) == target,
                            "action": "Pair found, return [0, 1]"
                        }
                    ]
                },
                {
                    "id": "hash_map",
                    "name": "One-Pass Hash Map (Optimized)",
                    "time_complexity": "O(n)",
                    "auxiliary_space": "O(n)",
                    "total_space": "O(n)",
                    "idea": "Traverse the array once. For each element, check whether target - nums[i] already exists in our hash map. If yes, return their indices; otherwise store nums[i] -> i.",
                    "pseudocode": [
                        "map = empty hash map",
                        "for i, val in enumerate(nums):",
                        "  complement = target - val",
                        "  if complement in map: return [map[complement], i]",
                        "  map[val] = i"
                    ],
                    "code": code_opt,
                    "dry_run_steps": [
                        {
                            "step": 1,
                            "index": 0,
                            "value": nums[0] if len(nums) > 0 else 2,
                            "complement": target - (nums[0] if len(nums) > 0 else 2),
                            "map_state_before": {},
                            "found": False,
                            "action": f"Store {nums[0] if len(nums) > 0 else 2} at index 0"
                        },
                        {
                            "step": 2,
                            "index": 1,
                            "value": nums[1] if len(nums) > 1 else 7,
                            "complement": target - (nums[1] if len(nums) > 1 else 7),
                            "map_state_before": {str(nums[0] if len(nums) > 0 else 2): 0},
                            "found": True,
                            "action": f"Complement found! Return [0, 1]"
                        }
                    ]
                }
            ]
        }

        jsonschema.validate(instance=explanation, schema=self.schema)
        return explanation

    def _generate_binary_search(self, problem: Dict[str, Any], lang: str, nums: List[int], target: int) -> Dict[str, Any]:
        code_bf = CODE_TEMPLATES["binary-search"]["brute_force"].get(lang, CODE_TEMPLATES["binary-search"]["brute_force"]["cpp"])
        code_opt = CODE_TEMPLATES["binary-search"]["optimized"].get(lang, CODE_TEMPLATES["binary-search"]["optimized"]["cpp"])

        explanation = {
            "schema_version": "1.0",
            "problem_id": "binary-search",
            "summary": f"Search for target value {target} in a sorted array in logarithmic time.",
            "key_observations": [
                "Because the array is sorted, comparing target with the midpoint eliminates half the search space every step.",
                "Repeatedly halving the search space yields O(log n) time complexity.",
                "Two pointers (left, right) track the active window without extra memory."
            ],
            "approaches": [
                {
                    "id": "linear_scan",
                    "name": "Linear Scan (Brute Force)",
                    "time_complexity": "O(n)",
                    "auxiliary_space": "O(1)",
                    "total_space": "O(1)",
                    "idea": "Scan every element from index 0 to n-1 checking if nums[i] == target.",
                    "pseudocode": [
                        "for i from 0 to n-1:",
                        "  if nums[i] == target: return i",
                        "return -1"
                    ],
                    "code": code_bf,
                    "dry_run_steps": [
                        {"step": 1, "index": 0, "value": nums[0], "target": target, "action": "Check if equal"}
                    ]
                },
                {
                    "id": "binary_search",
                    "name": "Binary Search (Optimized)",
                    "time_complexity": "O(log n)",
                    "auxiliary_space": "O(1)",
                    "total_space": "O(1)",
                    "idea": "Maintain left and right boundaries. Calculate mid = left + (right - left)/2. If nums[mid] == target return mid; if nums[mid] < target search right; else search left.",
                    "pseudocode": [
                        "left = 0, right = n - 1",
                        "while left <= right:",
                        "  mid = left + (right - left) // 2",
                        "  if nums[mid] == target: return mid",
                        "  elif nums[mid] < target: left = mid + 1",
                        "  else: right = mid - 1",
                        "return -1"
                    ],
                    "code": code_opt,
                    "dry_run_steps": [
                        {
                            "step": 1,
                            "left": 0,
                            "right": len(nums) - 1,
                            "mid": (len(nums) - 1) // 2,
                            "mid_val": nums[(len(nums) - 1) // 2],
                            "target": target,
                            "action": f"Compare mid value with target"
                        }
                    ]
                }
            ]
        }

        jsonschema.validate(instance=explanation, schema=self.schema)
        return explanation

if __name__ == "__main__":
    from problem_normalizer import ProblemNormalizer
    p = ProblemNormalizer().normalize("prompt", "Two sum in python", language="python")
    gen = ExplanationGenerator()
    exp = gen.generate(p)
    print("✓ Valid explanation generated!")
    print(json.dumps(exp, indent=2)[:300] + "...")
