import unittest
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from fastapi.testclient import TestClient
from backend.app.main import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health(self):
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["status"], "ok")

    def test_create_and_get_generation(self):
        payload = {
            "input_type": "problem",
            "problem": {
                "title": "Two Sum",
                "statement": "Given an array of integers nums..."
            },
            "programming_language": "cpp",
            "video_preferences": {
                "aspect_ratio": "9:16",
                "resolution": "1080x1920"
            }
        }
        response = self.client.post("/api/v1/generations", json=payload)
        self.assertEqual(response.status_code, 202)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("job_id", data["data"])
        
        job_id = data["data"]["job_id"]
        status_resp = self.client.get(f"/api/v1/generations/{job_id}")
        self.assertEqual(status_resp.status_code, 200)
        self.assertEqual(status_resp.json()["data"]["job_id"], job_id)

    def test_create_generation_from_prompt(self):
        payload = {
            "input_type": "prompt",
            "prompt": "Explain Binary Search in Python",
            "programming_language": "python",
            "video_preferences": {
                "aspect_ratio": "9:16",
                "resolution": "1080x1920"
            }
        }
        response = self.client.post("/api/v1/generations", json=payload)
        self.assertEqual(response.status_code, 202)
        data = response.json()
        self.assertTrue(data["success"])
        job_id = data["data"]["job_id"]
        
        status_resp = self.client.get(f"/api/v1/generations/{job_id}")
        self.assertEqual(status_resp.status_code, 200)
        job_data = status_resp.json()["data"]
        self.assertEqual(job_data["status"], "completed")

if __name__ == "__main__":
    unittest.main()
