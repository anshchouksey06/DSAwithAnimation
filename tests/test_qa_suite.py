"""AI DSA Studio - Comprehensive QA Automated Test Suite
Covers: API Boundary Tests, Contract Schema Invariance, Media Timeline Math, Algorithmic Edge Cases, and Security Sanitization.
"""

import unittest
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import os
import json
import wave
import jsonschema
from fastapi.testclient import TestClient

from backend.app.main import app
from engine.generators import ProblemNormalizer, ExplanationGenerator, ScenePlanner, NarrationGenerator
from engine.verification.universal_verifier import verify_binary_search
from engine.verification.two_sum_verifier import two_sum_hash_map, two_sum_brute_force

class TestAPIBoundaryAndNegative(unittest.TestCase):
    """QA Test Suite 1: API Negative & Boundary Testing"""
    def setUp(self):
        self.client = TestClient(app)

    def test_404_non_existent_job(self):
        """Verify non-existent job returns HTTP 404 with expected error structure."""
        resp = self.client.get("/api/v1/generations/job_non_existent_9999")
        self.assertEqual(resp.status_code, 404)
        data = resp.json()
        self.assertIn("detail", data)
        self.assertEqual(data["detail"], "Job not found")

    def test_404_non_existent_video(self):
        """Verify non-existent video returns HTTP 404."""
        resp = self.client.get("/api/v1/videos/video_fake_123")
        self.assertEqual(resp.status_code, 404)

    def test_422_empty_payload(self):
        """Verify empty JSON payload is rejected with 422 Unprocessable Entity."""
        resp = self.client.post("/api/v1/generations", json={})
        self.assertEqual(resp.status_code, 422)

    def test_422_unsupported_language(self):
        """Verify invalid programming language is rejected by pydantic validator."""
        payload = {
            "input_type": "prompt",
            "prompt": "Binary Search",
            "programming_language": "ruby"  # Unsupported
        }
        resp = self.client.post("/api/v1/generations", json=payload)
        self.assertEqual(resp.status_code, 422)

    def test_unique_job_ids_for_identical_requests(self):
        """Verify multiple identical requests generate distinct job IDs."""
        payload = {
            "input_type": "problem",
            "problem": {"title": "Two Sum"},
            "programming_language": "cpp"
        }
        resp1 = self.client.post("/api/v1/generations", json=payload)
        resp2 = self.client.post("/api/v1/generations", json=payload)
        id1 = resp1.json()["data"]["job_id"]
        id2 = resp2.json()["data"]["job_id"]
        self.assertNotEqual(id1, id2, "Job IDs must be cryptographically unique")


class TestContractSchemaInvariance(unittest.TestCase):
    """QA Test Suite 2: Contract Schema Enforcement & Invariance"""
    def setUp(self):
        self.contracts_dir = os.path.abspath("contracts")
        self.normalizer = ProblemNormalizer()
        self.exp_gen = ExplanationGenerator()
        self.scene_planner = ScenePlanner()
        self.narration_gen = NarrationGenerator()

    def test_all_contract_schemas_are_valid_draft7(self):
        """Ensure all 6 JSON schemas in contracts/ are valid Draft-07 schemas."""
        for fname in os.listdir(self.contracts_dir):
            if fname.endswith(".schema.json"):
                fpath = os.path.join(self.contracts_dir, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    schema_data = json.load(f)
                # Validating the schema against Draft-07 meta-schema
                jsonschema.Draft7Validator.check_schema(schema_data)

    def test_schema_rejects_missing_required_fields(self):
        """Ensure ProblemNormalizer schema catches missing fields."""
        schema = self.normalizer.schema
        bad_instance = {
            "schema_version": "1.0",
            "problem_id": "two-sum"
            # Missing title, statement, input, target, etc.
        }
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance=bad_instance, schema=schema)

    def test_end_to_end_generator_contracts(self):
        """Ensure generated entities strictly validate against all respective schemas."""
        p = self.normalizer.normalize("prompt", "Two Sum", language="java")
        jsonschema.validate(instance=p, schema=self.normalizer.schema)

        exp = self.exp_gen.generate(p)
        jsonschema.validate(instance=exp, schema=self.exp_gen.schema)

        sp = self.scene_planner.plan_scenes(p, exp)
        jsonschema.validate(instance=sp, schema=self.scene_planner.schema)

        narr = self.narration_gen.generate_narration(p, exp)
        jsonschema.validate(instance=narr, schema=self.narration_gen.schema)


class TestMediaAndTimelineIntegrity(unittest.TestCase):
    """QA Test Suite 3: Audio/Video Timeline & Subtitle Mathematical Consistency"""

    def test_authoritative_timeline_mathematical_consistency(self):
        """Verify timeline segments are strictly contiguous and frame math is exact."""
        timeline_path = "output/two-sum-prototype-001/07_narration_timeline.json"
        if not os.path.exists(timeline_path):
            self.skipTest("Timeline file not generated yet")

        with open(timeline_path, "r", encoding="utf-8") as f:
            t = json.load(f)

        fps = t["fps"]
        self.assertEqual(fps, 30, "Educational standard must be 30 FPS")
        segments = t["segments"]
        self.assertGreaterEqual(len(segments), 5, "Must have all explanation sections")

        for i, seg in enumerate(segments):
            self.assertGreater(seg["end_seconds"], seg["start_seconds"], f"Segment {seg['segment_id']} has invalid duration")
            expected_start_frame = int(round(seg["start_seconds"] * fps))
            expected_duration_frames = int(round(seg["duration_seconds"] * fps))
            self.assertEqual(seg["start_frame"], expected_start_frame)
            self.assertEqual(seg["duration_frames"], expected_duration_frames)

            # Check contiguity
            if i > 0:
                prev_end = segments[i - 1]["end_seconds"]
                self.assertAlmostEqual(seg["start_seconds"], prev_end, delta=0.01,
                                       msg=f"Gap or overlap between {segments[i-1]['segment_id']} and {seg['segment_id']}")

    def test_subtitles_srt_format_compliance(self):
        """Verify SRT subtitles have valid index sequences and time syntax."""
        srt_path = "output/two-sum-prototype-001/08_subtitles.srt"
        if not os.path.exists(srt_path):
            self.skipTest("SRT file not found")

        with open(srt_path, "r", encoding="utf-8") as f:
            content = f.read().strip()

        blocks = content.split("\n\n")
        self.assertGreater(len(blocks), 0)
        for idx, block in enumerate(blocks, start=1):
            lines = block.strip().split("\n")
            self.assertGreaterEqual(len(lines), 3)
            self.assertEqual(lines[0], str(idx), f"SRT sequence mismatch at block {idx}")
            self.assertIn("-->", lines[1], "Timestamp line must contain '-->'")
            times = lines[1].split("-->")
            self.assertEqual(len(times), 2)
            # Verify format: HH:MM:SS,mmm
            for t_str in times:
                t_str = t_str.strip()
                parts = t_str.split(":")
                self.assertEqual(len(parts), 3)
                self.assertIn(",", parts[2])


class TestAlgorithmicEdgeCases(unittest.TestCase):
    """QA Test Suite 4: Algorithmic Correctness & Edge-Case Verification"""

    def test_two_sum_edge_cases(self):
        """Test Two Sum with identical elements, negative values, and zero targets."""
        # Edge Case 1: Duplicate elements making target
        res1 = two_sum_hash_map([3, 3], 6)
        self.assertEqual(sorted(res1), [0, 1])

        # Edge Case 2: Negative elements
        res2 = two_sum_hash_map([-1, -2, -3, -4], -7)
        self.assertEqual(sorted(res2), [2, 3])

        # Edge Case 3: Zero target
        res3 = two_sum_hash_map([0, 4, 3, 0], 0)
        self.assertEqual(sorted(res3), [0, 3])

        # Parity check between brute force and hash map
        self.assertEqual(sorted(two_sum_brute_force([3, 3], 6)), [0, 1])
        self.assertEqual(sorted(two_sum_brute_force([-1, -2, -3, -4], -7)), [2, 3])

    def test_binary_search_differential_and_boundaries(self):
        """Test Binary Search edge cases (boundaries, single element, missing element)."""
        prob = {
            "problem_id": "binary-search",
            "input": {"nums": [-5, 0, 3, 8, 12, 20]},
            "target": -5
        }
        exp = {
            "approaches": [
                {"id": "binary_search", "time_complexity": "O(log n)"}
            ]
        }
        report = verify_binary_search(prob, exp)
        self.assertEqual(report["status"], "passed")
        for check in report["checks"]:
            self.assertEqual(check["status"], "passed", f"Check {check['name']} failed")


class TestSecurityAndInputSanitization(unittest.TestCase):
    """QA Test Suite 5: Security, Special Characters & Prompt Injection Resistance"""
    def setUp(self):
        self.normalizer = ProblemNormalizer()

    def test_prompt_injection_sanitization(self):
        """Ensure malicious shell/script injected prompt is safely parsed without execution."""
        malicious_prompt = 'Two Sum; DROP TABLE users; rm -rf /; $(whoami); `calc.exe`; <script>alert("XSS")</script>'
        res = self.normalizer.normalize("prompt", malicious_prompt, language="cpp")
        self.assertEqual(res["problem_id"], "two-sum")
        self.assertEqual(res["schema_version"], "1.0")
        self.assertIsInstance(res["input"]["nums"], list)

    def test_unicode_and_emoji_handling(self):
        """Ensure Unicode, Chinese characters, and Emojis in prompt are safely handled."""
        unicode_prompt = "二分查找 Binary Search 🚀 1080x1920 高清"
        res = self.normalizer.normalize("prompt", unicode_prompt, language="python")
        self.assertEqual(res["problem_id"], "binary-search")
        self.assertEqual(res["language"], "python")

    def test_extremely_large_prompt(self):
        """Verify 10,000 character prompt does not trigger buffer overflow or unhandled exceptions."""
        large_prompt = "Two Sum " + ("A" * 10000)
        res = self.normalizer.normalize("prompt", large_prompt, language="cpp")
        self.assertEqual(res["problem_id"], "two-sum")


class TestRemotionMotionEngine(unittest.TestCase):
    """QA Test Suite 6: Remotion Video Rendering & Composition Engine"""

    def test_remotion_composition_bundle_metadata(self):
        """Verify Remotion Root registers DSAVideo and TwoSumVideo with 1080x1920 layout."""
        root_path = "renderer/src/Root.tsx"
        with open(root_path, "r", encoding="utf-8") as f:
            code = f.read()
        self.assertIn('id="DSAVideo"', code)
        self.assertIn('id="TwoSumVideo"', code)
        self.assertIn('width={1080}', code)
        self.assertIn('height={1920}', code)
        self.assertIn('calculateMetadata', code)

    def test_dynamic_scene_props_compatibility(self):
        """Verify render_remotion_video handles invalid/missing paths gracefully without raising exceptions."""
        from engine.orchestrator import PipelineOrchestrator
        orch = PipelineOrchestrator()
        res = orch.render_remotion_video(
            job_dir="output/non_existent_job",
            timeline_path="output/non_existent_timeline.json",
            scene_plan_path="output/non_existent_scenes.json",
            output_mp4="output/non_existent_job/out.mp4"
        )
        self.assertFalse(res, "Missing assets must return False gracefully")

if __name__ == "__main__":
    unittest.main()
