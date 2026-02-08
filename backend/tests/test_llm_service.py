import json
import pytest
from unittest.mock import patch, MagicMock
from backend.app.llm_service import extract_json_from_text, LLMService


class TestExtractJsonFromText:
    def test_direct_json(self):
        text = '{"detections": [{"type": "name", "original": "John"}]}'
        result = extract_json_from_text(text)
        assert result is not None
        assert len(result["detections"]) == 1

    def test_json_with_thinking_block(self):
        text = '<think>Let me analyze...</think>{"detections": [{"type": "phone", "original": "123"}]}'
        result = extract_json_from_text(text)
        assert result is not None
        assert result["detections"][0]["type"] == "phone"

    def test_json_in_code_block(self):
        text = '```json\n{"detections": [{"type": "email", "original": "a@b.com"}]}\n```'
        result = extract_json_from_text(text)
        assert result is not None
        assert result["detections"][0]["original"] == "a@b.com"

    def test_empty_detections(self):
        text = '{"detections": []}'
        result = extract_json_from_text(text)
        assert result is not None
        assert result["detections"] == []

    def test_invalid_json(self):
        text = "This is not JSON at all"
        result = extract_json_from_text(text)
        assert result is None

    def test_json_with_surrounding_text(self):
        text = 'Here is the result: {"detections": [{"type": "name", "original": "Bob"}]} end'
        result = extract_json_from_text(text)
        assert result is not None
        assert result["detections"][0]["original"] == "Bob"

    def test_whitespace_handling(self):
        text = '  \n  {"detections": []}  \n  '
        result = extract_json_from_text(text)
        assert result is not None


class TestLLMServiceConfig:
    @patch("backend.app.llm_service.settings")
    def test_cloud_mode_init(self, mock_settings):
        mock_settings.LLM_API_KEY = "test-key"
        mock_settings.LLM_API_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        mock_settings.LLM_MODEL = "qwen3-0.6b"
        mock_settings.LLM_MODE = "cloud"
        service = LLMService()
        assert service.mode == "cloud"
        assert service.model == "qwen3-0.6b"

    @patch("backend.app.llm_service.settings")
    def test_local_mode_init(self, mock_settings):
        mock_settings.LLM_API_KEY = "EMPTY"
        mock_settings.LLM_API_BASE = "http://localhost:8001/v1"
        mock_settings.LLM_MODEL = "Qwen/Qwen3-0.6B"
        mock_settings.LLM_MODE = "local"
        service = LLMService()
        assert service.mode == "local"
        assert service.model == "Qwen/Qwen3-0.6B"


class TestLLMServiceDetectPII:
    @pytest.mark.asyncio
    async def test_detect_pii_mock(self):
        service = LLMService.__new__(LLMService)
        service.mode = "cloud"
        service.model = "qwen3-0.6b"
        service.client = MagicMock()

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "detections": [
                {"type": "name", "original": "John Smith"},
                {"type": "phone", "original": "138-1234-5678"}
            ]
        })
        service.client.chat.completions.create.return_value = mock_response

        text = "My name is John Smith, phone 138-1234-5678"
        result = await service.detect_pii(text, ["name", "phone"])
        assert len(result["detections"]) == 2
        assert result["detections"][0]["type"] == "name"
        assert result["detections"][0]["start"] == 11
        assert result["detections"][0]["end"] == 21

    @pytest.mark.asyncio
    async def test_detect_pii_api_error(self):
        service = LLMService.__new__(LLMService)
        service.mode = "cloud"
        service.model = "qwen3-0.6b"
        service.client = MagicMock()
        service.client.chat.completions.create.side_effect = Exception("API error")

        result = await service.detect_pii("test text", ["name"])
        assert "error" in result
        assert result["detections"] == []

    @pytest.mark.asyncio
    async def test_detect_pii_malformed_response(self):
        service = LLMService.__new__(LLMService)
        service.mode = "cloud"
        service.model = "qwen3-0.6b"
        service.client = MagicMock()

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Not valid JSON at all"
        service.client.chat.completions.create.return_value = mock_response

        result = await service.detect_pii("test", ["name"])
        assert "error" in result
