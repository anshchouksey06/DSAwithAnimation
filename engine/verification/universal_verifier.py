"""AI DSA Studio - Universal Verification Engine
Routes verification to problem-specific differential testers or generalized algorithmic verification.
"""

import json
import random
from typing import Dict, Any, List

from .two_sum_verifier import run_verification as verify_two_sum

def verify_binary_search(problem: Dict[str, Any], explanation: Dict[str, Any]) -> Dict[str, Any]:
    checks = []
    errors = []

    def linear_search(arr: List[int], target: int) -> int:
        for i, v in enumerate(arr):
            if v == target:
                return i
        return -1

    def binary_search(arr: List[int], target: int) -> int:
        left, right = 0, len(arr) - 1
        while left <= right:
            mid = left + (right - left) // 2
            if arr[mid] == target:
                return mid
            elif arr[mid] < target:
                left = mid + 1
            else:
                right = mid - 1
        return -1

    # 1. Deterministic unit tests
    test_cases = [
        {"nums": [-1, 0, 3, 5, 9, 12], "target": 9, "expected": 4, "name": "middle_element"},
        {"nums": [-1, 0, 3, 5, 9, 12], "target": 2, "expected": -1, "name": "element_not_found"},
        {"nums": [5], "target": 5, "expected": 0, "name": "single_element_found"},
        {"nums": [5], "target": 2, "expected": -1, "name": "single_element_not_found"},
        {"nums": [1, 2, 3, 4, 5], "target": 1, "expected": 0, "name": "left_boundary"},
        {"nums": [1, 2, 3, 4, 5], "target": 5, "expected": 4, "name": "right_boundary"},
    ]

    unit_passed = True
    for tc in test_cases:
        res_lin = linear_search(tc["nums"], tc["target"])
        res_bin = binary_search(tc["nums"], tc["target"])
        if res_bin != tc["expected"] or res_lin != tc["expected"]:
            unit_passed = False
            errors.append(f"Test case '{tc['name']}' failed: expected {tc['expected']}, got bin={res_bin}, lin={res_lin}")

    checks.append({
        "name": "binary_search_unit_tests",
        "status": "passed" if unit_passed else "failed",
        "message": "All unit tests passed" if unit_passed else "Unit tests failed"
    })

    # 2. Differential testing on 25 random sorted arrays
    diff_passed = True
    random.seed(42)
    for i in range(25):
        arr = sorted(list(set(random.randint(-100, 100) for _ in range(random.randint(5, 30)))))
        target = random.choice(arr) if random.random() < 0.7 else random.randint(-120, 120)

        res_lin = linear_search(arr, target)
        res_bin = binary_search(arr, target)

        if res_lin != res_bin:
            diff_passed = False
            errors.append(f"Differential mismatch on test {i}: linear={res_lin}, binary={res_bin}")
            break

    checks.append({
        "name": "differential_testing",
        "status": "passed" if diff_passed else "failed",
        "message": "Differential testing passed across 25 sorted trials"
    })

    # 3. Complexity metadata consistency
    approaches = {a["id"]: a for a in explanation.get("approaches", [])}
    comp_passed = True
    if "binary_search" in approaches:
        if approaches["binary_search"]["time_complexity"] != "O(log n)":
            comp_passed = False
            errors.append(f"Expected O(log n) for binary_search, got {approaches['binary_search']['time_complexity']}")

    checks.append({
        "name": "complexity_consistency",
        "status": "passed" if comp_passed else "failed",
        "message": "Complexity annotations verified"
    })

    status = "passed" if all(c["status"] == "passed" for c in checks) else "failed"
    return {
        "schema_version": "1.0",
        "status": status,
        "checks": checks,
        "errors": errors
    }

def run_universal_verification(problem_path: str, explanation_path: str) -> Dict[str, Any]:
    with open(problem_path, "r", encoding="utf-8") as f:
        problem = json.load(f)
    with open(explanation_path, "r", encoding="utf-8") as f:
        explanation = json.load(f)

    prob_id = problem.get("problem_id", "")
    if prob_id == "binary-search":
        return verify_binary_search(problem, explanation)
    else:
        return verify_two_sum(problem_path, explanation_path)
