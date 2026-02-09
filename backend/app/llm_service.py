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

        system_prompt = """### ROLE
You are an expert PII (Personally Identifiable Information) Recognition Engine. Your goal is to achieve 100% recall on sensitive data by combining deep semantic understanding with flexible pattern-matching logic.

### TARGET CATEGORIES
Detect ONLY the following categories based on user-defined needs:
{USER_DEFINED_CATEGORIES}

### Common categories
- Name: Chinese/English names, including titles (e.g., 王经理).
- Phone: Mobile/landline numbers, including variants with spaces, dashes, or Chinese digits.
- Email: Email addresses, including obfuscated formats like "user [at] mail.com".
- Address: Physical locations, from provinces to specific room numbers or landmarks.
- ID_Number: 15/18-digit national IDs, including masked versions.
- Bank_Card: 16-19 digit card numbers or "Bank Name + Last 4 Digits".
- Social_Media: Account IDs prefixed by platforms (e.g., 微信, 钉钉, 小红书).

### ADVANCED DETECTION LOGIC
1. Multi-Format Normalization: 
   - Identify data across all variants: Chinese numerals (e.g., "一三八"), character spacing ("1 3 8"), obfuscated symbols ("138*1234*5678"), and non-standard separators ("(021) 5080-XXXX").
2. Semantic Anchor Discovery: 
   - Use proximity-based detection. If a substring follows a "Trigger Keyword" (e.g., "Contact:", "Addr:", "Lives in", "账号", "联系方式", "微信搜"), prioritize it as PII even if the format is non-standard or masked.
3. Intelligent Filtering (Anti-Hallucination): 
   - Distinguish PII from noise: EXCLUDE pure timestamps (2026-02-10), generic prices ($100), or version numbers (v1.5.0) UNLESS they explicitly match a target category logic.
4. Entity Context Integrity: 
   - Capture the "Original" string as the COMPLETE contextually relevant substring. For Social Media, include the platform (e.g., "WeChat: user123"). For masked data, keep the mask intact (e.g., "310...XXXX").

### EXTRACTION RULES BY TYPE
- Names: Capture full names, nicknames, or "Surname + Title" (e.g., "Manager Wang").
- Phones: Capture 7-15 digit sequences regardless of separators/symbols.
- Bank/ID: Capture 15-19 digit sequences, especially those with bank names or "尾号" context.
- Custom Logic: If a user provides a custom category, treat its description as a high-priority semantic rule.

### Requirement
Perform a comprehensive scan, outputting as many identified or suspected entities as possible, without missing any.

### OUTPUT CONSTRAINT
- Response MUST be a single, valid JSON object.
- NO markdown markers (no ```json). NO introductory text. NO trailing explanations.
- JSON structure: 
{"detections": [{"type": "category_name", "original": "EXACT_SUBSTRING"}]}"""
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
                max_tokens=16000,  # 适配qwen3-4b的32K上下文长度
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
