import io
import json
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


class TestHealthEndpoint:
    def test_health_check(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "Alta-Lex" in data["service"]


class TestUploadEndpoint:
    def test_upload_txt(self):
        content = b"Hello world, my name is John Smith."
        response = client.post(
            "/api/upload",
            files={"file": ("test.txt", io.BytesIO(content), "text/plain")},
        )
        assert response.status_code == 200
        assert response.json()["text"] == "Hello world, my name is John Smith."

    def test_upload_csv(self):
        content = b"name,email\nAlice,alice@test.com\n"
        response = client.post(
            "/api/upload",
            files={"file": ("data.csv", io.BytesIO(content), "text/csv")},
        )
        assert response.status_code == 200
        assert "Alice" in response.json()["text"]

    def test_upload_unsupported_type(self):
        content = b"binary data"
        response = client.post(
            "/api/upload",
            files={"file": ("test.exe", io.BytesIO(content), "application/octet-stream")},
        )
        assert response.status_code == 400
        assert "Unsupported" in response.json()["detail"]


class TestMaskEndpoint:
    @patch("backend.app.llm_service.llm_service")
    def test_mask_pii_success(self, mock_llm):
        mock_llm.detect_pii = AsyncMock(return_value={
            "detections": [
                {"type": "name", "original": "John Smith", "start": 11, "end": 21}
            ]
        })
        response = client.post(
            "/api/mask",
            json={"text": "My name is John Smith.", "categories": ["name"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert "████" in data["masked_text"]
        assert len(data["detections"]) == 1

    def test_mask_empty_text(self):
        response = client.post(
            "/api/mask",
            json={"text": "   ", "categories": ["name"]},
        )
        assert response.status_code == 400

    @patch("backend.app.llm_service.llm_service")
    def test_mask_llm_error(self, mock_llm):
        mock_llm.detect_pii = AsyncMock(return_value={
            "detections": [],
            "error": "API timeout"
        })
        response = client.post(
            "/api/mask",
            json={"text": "Some text", "categories": ["name"]},
        )
        assert response.status_code == 502

    @patch("backend.app.llm_service.llm_service")
    def test_mask_no_pii_found(self, mock_llm):
        mock_llm.detect_pii = AsyncMock(return_value={
            "detections": []
        })
        response = client.post(
            "/api/mask",
            json={"text": "Hello world", "categories": ["name"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["masked_text"] == "Hello world"
        assert data["detections"] == []

    @patch("backend.app.llm_service.llm_service")
    def test_mask_multiple_detections(self, mock_llm):
        mock_llm.detect_pii = AsyncMock(return_value={
            "detections": [
                {"type": "name", "original": "Alice", "start": 0, "end": 5},
                {"type": "phone", "original": "123456", "start": 13, "end": 19},
            ]
        })
        response = client.post(
            "/api/mask",
            json={"text": "Alice called 123456", "categories": ["name", "phone"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["masked_text"] == "████ called ████"
        assert len(data["detections"]) == 2

    @patch("backend.app.llm_service.llm_service")
    def test_mask_default_categories(self, mock_llm):
        mock_llm.detect_pii = AsyncMock(return_value={"detections": []})
        response = client.post(
            "/api/mask",
            json={"text": "Hello world"},
        )
        assert response.status_code == 200
