import json
import re
import logging
from openai import OpenAI
from .config import settings

logger = logging.getLogger(__name__)


def extract_json_from_text(text: str) -> dict | None:
    """Try multiple strategies to extract JSON from LLM response text."""
    text = text.strip()

    # Strategy 1: Remove <think>...</think> blocks
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

    # Strategy 2: Direct JSON parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Strategy 3: Extract from markdown code blocks
    code_block_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if code_block_match:
        try:
            return json.loads(code_block_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Strategy 4: Find JSON object pattern in text
    json_match = re.search(r'\{[^{}]*"detections"\s*:\s*\[.*?\]\s*\}', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass

    # Strategy 5: Find any JSON object
    for match in re.finditer(r"\{[^{}]+\}", text):
        try:
            parsed = json.loads(match.group(0))
            if "detections" in parsed:
                return parsed
        except json.JSONDecodeError:
            continue

    return None


class LLMService:
    """Unified LLM service supporting both local vLLM and cloud DashScope API."""

    def __init__(self):
        # For local vLLM, use dummy API key to avoid Bearer header issues
        api_key = settings.LLM_API_KEY if settings.LLM_API_KEY else "sk-dummy-key-for-local"
        self.client = OpenAI(
            api_key=api_key,
            base_url=settings.LLM_API_BASE,
        )
        self.model = settings.LLM_MODEL
        self.mode = settings.LLM_MODE

    async def detect_pii(self, text: str, categories: list[str]) -> dict:
        """Detect PII in text using Qwen3-0.6B.

        Returns a dict with 'detections' list of {type, original, start, end}.
        """
        categories_str = ", ".join(categories)

        system_prompt = """You are an expert PII Recognition Engine. Your goal is to achieve 100% recall on sensitive data, including standard PII and custom categories provided by the user.



[Target Categories]

Your detection task is STRICTLY limited to the following categories:

{USER_DEFINED_CATEGORIES}



[Scanning Strategy]

1. Pattern Robustness: Treat "1三8" as "138", "zero" as "0", and ignore separators like "-", " ", or ".". 

2. Semantic Extension: If a user provides a custom category, analyze its definition and identify related substrings even if the format is irregular.

3. Context Clues: Use surrounding keywords (e.g., "Account:", "Located at", "Contact") to confirm entity boundaries.

4. NO Hallucination: Exclude common non-PII numbers like dates, prices, or version numbers unless they explicitly match a category.



[Entity Integrity]

- Capture the FULL substring. For example, if "WeChat: user123" is found, the original should be the entire phrase if it provides necessary context for that category.



[Output Constraint]

- Response MUST be a single, valid JSON object.

- NO markdown markers, NO prose, NO explanations.

- Format: {"detections": [{"type": "category_name", "original": "EXACT_SUBSTRING"}]}"""
        user_prompt = (
            f"Categories to detect: {categories_str}\n\n"
            f"Text to analyze:\n{text}"
        )

        try:
            extra_params: dict = {}
            if self.mode == "cloud":
                extra_params["extra_body"] = {
                    "enable_thinking": False,
                }

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                top_p=0.8,
                max_tokens=8000,  # 适配Phi-3.5的16K上下文长度
                **extra_params,
            )

            content = response.choices[0].message.content or ""
            logger.info("LLM raw response: %s", content[:500])

            result = extract_json_from_text(content)

            if result is None:
                logger.warning("Failed to parse JSON from: %s", content[:500])
                return {"detections": [], "error": "Failed to parse LLM response as JSON"}

            # Validate and fix positions by finding actual text in input
            detections = []
            for det in result.get("detections", []):
                original = det.get("original", "")
                det_type = det.get("type", "unknown")

                if not original:
                    continue

                # Find the actual position in text
                start = text.find(original)
                if start != -1:
                    detections.append({
                        "type": det_type,
                        "original": original,
                        "start": start,
                        "end": start + len(original),
                    })
                else:
                    # Try case-insensitive search
                    lower_start = text.lower().find(original.lower())
                    if lower_start != -1:
                        actual = text[lower_start:lower_start + len(original)]
                        detections.append({
                            "type": det_type,
                            "original": actual,
                            "start": lower_start,
                            "end": lower_start + len(actual),
                        })

            return {"detections": detections}

        except Exception as e:
            logger.exception("LLM service error")
            return {"detections": [], "error": str(e)}


llm_service = LLMService()
