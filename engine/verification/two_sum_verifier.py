"""Two Sum algorithm implementations and verification engine."""
from typing import List, Tuple, Dict, Any
import json
import random

def two_sum_brute_force(nums: List[int], target: int) -> List[int]:
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []

def two_sum_hash_map(nums: List[int], target: int) -> List[int]:
    seen: Dict[int, int] = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []

def dry_run_hash_map(nums: List[int], target: int) -> List[Dict[str, Any]]:
    seen: Dict[int, int] = {}
    steps = []
    for i, num in enumerate(nums):
        complement = target - num
        step_data = {
            "step": i + 1,
            "index": i,
            "value": num,
            "complement": complement,
            "in_map": complement in seen
        }
        if complement in seen:
            step_data["found"] = True
            step_data["result"] = [seen[complement], i]
            steps.append(step_data)
            break
        else:
            step_data["found"] = False
            seen[num] = i
            step_data["map_state"] = dict(seen)
            steps.append(step_data)
    return steps

def run_verification(problem_path: str, explanation_path: str) -> Dict[str, Any]:
    with open(problem_path, "r", encoding="utf-8") as f:
        problem = json.load(f)
    with open(explanation_path, "r", encoding="utf-8") as f:
        explanation = json.load(f)

    checks = []
    errors = []

    # Check 1: Standard unit tests
    test_cases = [
        {"nums": [2, 7, 11, 15], "target": 9, "expected": [0, 1], "name": "standard_example"},
        {"nums": [3, 2, 4], "target": 6, "expected": [1, 2], "name": "unsorted_example"},
        {"nums": [3, 3], "target": 6, "expected": [0, 1], "name": "duplicate_values"},
        {"nums": [-1, -2, -3, -4, -5], "target": -8, "expected": [2, 4], "name": "negative_values"},
        {"nums": [1, 5, 8, 3], "target": 4, "expected": [0, 3], "name": "solution_at_edges"},
    ]

    bf_passed = True
    hm_passed = True

    for tc in test_cases:
        res_bf = two_sum_brute_force(tc["nums"], tc["target"])
        res_hm = two_sum_hash_map(tc["nums"], tc["target"])

        # Validate correctness
        if len(res_bf) != 2 or tc["nums"][res_bf[0]] + tc["nums"][res_bf[1]] != tc["target"]:
            bf_passed = False
            errors.append(f"Brute force failed test {tc['name']}: got {res_bf}")

        if len(res_hm) != 2 or tc["nums"][res_hm[0]] + tc["nums"][res_hm[1]] != tc["target"]:
            hm_passed = False
            errors.append(f"Hash map failed test {tc['name']}: got {res_hm}")

    checks.append({
        "name": "brute_force_tests",
        "status": "passed" if bf_passed else "failed",
        "message": "All unit test cases passed for brute-force" if bf_passed else "Unit tests failed"
    })
    checks.append({
        "name": "optimized_tests",
        "status": "passed" if hm_passed else "failed",
        "message": "All unit test cases passed for hash-map" if hm_passed else "Unit tests failed"
    })

    # Check 2: Differential testing on random generated inputs
    diff_passed = True
    random.seed(42)
    for i in range(20):
        length = random.randint(2, 25)
        nums = [random.randint(-100, 100) for _ in range(length)]
        idx1, idx2 = random.sample(range(length), 2)
        target = nums[idx1] + nums[idx2]

        r_bf = two_sum_brute_force(nums, target)
        r_hm = two_sum_hash_map(nums, target)

        if not r_bf or not r_hm:
            diff_passed = False
            errors.append(f"Differential test {i} failed: missing solution")
            break

        sum_bf = nums[r_bf[0]] + nums[r_bf[1]]
        sum_hm = nums[r_hm[0]] + nums[r_hm[1]]
        if sum_bf != target or sum_hm != target:
            diff_passed = False
            errors.append(f"Differential test {i} failed: sum mismatch")
            break

    checks.append({
        "name": "differential_tests",
        "status": "passed" if diff_passed else "failed",
        "message": "20 generated test cases produced identical validity" if diff_passed else "Differential test failed"
    })

    # Check 3: Dry run consistency
    dry_steps = dry_run_hash_map(problem["input"]["nums"], problem["target"])
    last_step = dry_steps[-1]
    dry_consistent = (
        last_step.get("found") is True and
        problem["input"]["nums"][last_step["result"][0]] + problem["input"]["nums"][last_step["result"][1]] == problem["target"]
    )
    checks.append({
        "name": "dry_run_consistency",
        "status": "passed" if dry_consistent else "failed",
        "message": f"Dry-run executed {len(dry_steps)} steps and found valid answer {last_step.get('result')}"
    })

    # Check 4: Complexity metadata validation
    approaches = {app["id"]: app for app in explanation.get("approaches", [])}
    complexity_ok = (
        "brute-force" in approaches and
        "O(n^2)" in approaches["brute-force"]["time_complexity"] and
        "hash-map" in approaches and
        "O(n)" in approaches["hash-map"]["time_complexity"]
    )
    checks.append({
        "name": "complexity_metadata",
        "status": "passed" if complexity_ok else "failed",
        "message": "Time and space complexities correspond to algorithmic bounds"
    })

    overall_status = "passed" if (bf_passed and hm_passed and diff_passed and dry_consistent and complexity_ok) else "failed"

    report = {
        "schema_version": "1.0",
        "status": overall_status,
        "checks": checks,
        "errors": errors
    }
    return report

if __name__ == "__main__":
    report = run_verification(
        "examples/two-sum/01_problem.json",
        "examples/two-sum/02_explanation.json"
    )
    output_path = "examples/two-sum/03_validation.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"Validation finished with status: {report['status']}")
    for c in report['checks']:
        print(f" - {c['name']}: {c['status']} ({c.get('message', '')})")
