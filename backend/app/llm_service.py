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
You are an expert PII (Personally Identifiable Information) Recognition Engine optimized for legal document redaction. Your goal is to achieve 100% recall on sensitive data by combining deep semantic understanding with flexible pattern-matching logic.

### TARGET CATEGORIES
Detect ONLY the following categories based on user-defined needs:
{USER_DEFINED_CATEGORIES}

### Common categories
- Name: Chinese/English names, including titles (e.g., 王经理, 张律师).
- Phone: Mobile/landline/fax numbers, including variants with spaces, dashes, or Chinese digits.
- Fax: Fax numbers (传真), often following "传真:", "Fax:", "F:", or appearing alongside phone numbers.
- Email: Email addresses, including obfuscated formats like "user [at] mail.com" or "user#domain.com".
- Address: Physical locations, from provinces to specific room numbers or landmarks.
- ID_Number: 15/18-digit national IDs, including masked versions.
- Bank_Card: 16-19 digit card numbers or "Bank Name + Last 4 Digits".
- Social_Media: Account IDs prefixed by platforms (e.g., 微信, 钉钉, 小红书).

### ADVANCED DETECTION LOGIC

1. **Multi-Entity Sequence Detection (CRITICAL for Legal Docs)**:
   - Legal documents often contain CONSECUTIVE PII entities in contact blocks. EACH entity must be detected SEPARATELY.
   - Pattern Examples:
     * "电话: 021-12345678 传真: 021-87654321" → TWO separate detections
     * "email1@firm.com; email2@firm.com, email3@firm.com" → THREE separate detections
     * "Tel: 1381234567 / 1391234567 Fax: 021-5555666" → THREE separate detections
   - Common separators between consecutive entities: ";", ",", "/", "|", "、", spaces, line breaks, Chinese punctuation "；，"
   - NEVER merge multiple phone numbers or emails into a single detection.

2. **Legal Document Contact Block Recognition**:
   - Trigger patterns specific to legal docs:
     * Headers: "联系方式", "通讯地址", "送达地址", "联系人", "代理人信息", "当事人信息"
     * Law firm blocks: "律师事务所", "律所", "Law Firm", containing clustered contact info
     * Court/Party blocks: "原告", "被告", "申请人", "被申请人", "第三人" followed by contact details
   - When a contact block is detected, perform EXHAUSTIVE entity-by-entity extraction.

3. **Multi-Format Normalization**: 
   - Identify data across all variants: Chinese numerals (e.g., "一三八"), character spacing ("1 3 8"), obfuscated symbols ("138*1234*5678"), and non-standard separators ("(021) 5080-XXXX").
   - Fax-specific formats: "传真同上", "传真号同电话", "Fax同号" → still flag the reference for human review.

4. **Semantic Anchor Discovery**: 
   - Use proximity-based detection with EXTENDED anchors for legal context:
     * Phone anchors: "电话", "Tel", "手机", "Mobile", "联系电话", "办公电话", "T:", "☎"
     * Fax anchors: "传真", "Fax", "F:", "传真电话"
     * Email anchors: "邮箱", "Email", "E-mail", "电子邮件", "E:", "✉"
     * Combined patterns: "电话/传真:", "Tel/Fax:" → expect MULTIPLE entities after anchor

5. **Intelligent Filtering (Anti-Hallucination)**: 
   - EXCLUDE: pure timestamps (2026-02-10), case numbers (2024民初123号), prices ($100), version numbers (v1.5.0), article/clause references (第123条)
   - INCLUDE even if ambiguous: any 7-15 digit sequence near contact anchors, any @-containing string near email anchors

6. **Entity Context Integrity**: 
   - Capture the "Original" string as the COMPLETE but INDIVIDUAL entity.
   - For labeled sequences: include the immediate label only → "传真: 021-5555666" (not the entire contact block)
   - For unlabeled sequences in a list: capture just the entity → "email2@firm.com"

### EXTRACTION RULES BY TYPE

- **Phones/Fax (ENHANCED)**:
  - Capture each 7-15 digit sequence as INDIVIDUAL detection
  - Include area codes and extensions: "(021) 1234-5678 ext. 800" → one detection
  - Slash-separated numbers are SEPARATE: "138xxx / 139xxx" → TWO detections
  - Fax following phone is SEPARATE: "T: 1234567 F: 7654321" → TWO detections

- **Emails (ENHANCED)**:
  - Capture each email as INDIVIDUAL detection regardless of separator
  - Valid separators creating new entities: ";", ",", "/", "|", " ", "、", newline
  - "abc@x.com;def@y.com,ghi@z.com" → THREE separate detections
  - Include obfuscated: "abc[at]x[dot]com", "abc#x.com", "abc (at) x.com"

- **Names**: Capture full names, nicknames, or "Surname + Title" (e.g., "王律师", "张法官").

- **Bank/ID**: Capture 15-19 digit sequences, especially those with bank names or "尾号" context.

- **Addresses**: Capture complete address strings; if multiple addresses exist, detect EACH separately.

- **Custom Logic**: If a user provides a custom category, treat its description as a high-priority semantic rule.

### DETECTION CHECKLIST (Mental Model)
Before finalizing output, verify:
☐ Have I scanned for CONSECUTIVE entities and split them individually?
☐ Are fax numbers detected SEPARATELY from phone numbers?
☐ Are semicolon/comma-separated emails detected as MULTIPLE entities?
☐ Did I check contact blocks for ALL entity types (phone + fax + email + address)?

### OUTPUT CONSTRAINT
- Response MUST be a single, valid JSON object.
- NO markdown markers (no ```json). NO introductory text. NO trailing explanations.
- Each PII entity = ONE object in the array. Consecutive entities = MULTIPLE objects.
- JSON structure: 
{"detections": [{"type": "category_name", "original": "EXACT_SUBSTRING"}]}

### EXAMPLE (Consecutive Entities)
Input: "联系电话: 021-12345678 / 021-87654321 传真: 021-11112222 邮箱: lawyer1@firm.com; lawyer2@firm.com"
Output: {"detections": [{"type": "Phone", "original": "021-12345678"}, {"type": "Phone", "original": "021-87654321"}, {"type": "Fax", "original": "021-11112222"}, {"type": "Email", "original": "lawyer1@firm.com"}, {"type": "Email", "original": "lawyer2@firm.com"}]}"""
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
                temperature=0,
                top_p=0.1,
                max_tokens=4000,  # 适配qwen3-4b的32K上下文长度
                **extra_params,
            )

            content = response.choices[0].message.content or ""
            logger.info("LLM raw response: %s", content[:500])

            result = extract_json_from_text(content)

            if result is None:
                logger.warning("Failed to parse JSON from: %s", content[:500])
                return {"detections": [], "error": "Failed to parse LLM response as JSON"}

            # Validate and fix positions by finding all occurrences of each entity in text
            detections = []
            processed_entities = set()  # Track processed (original_text, type) pairs to avoid duplicates
            
            for det in result.get("detections", []):
                original = det.get("original", "")
                det_type = det.get("type", "unknown")

                if not original:
                    continue

                # Create a unique key for this entity to track processing
                entity_key = (original, det_type)
                
                # Skip if we've already processed this exact entity
                if entity_key in processed_entities:
                    continue
                
                processed_entities.add(entity_key)
                
                # Find ALL occurrences of this entity in the text
                positions = self._find_all_occurrences(text, original)
                
                # Add detection for each occurrence
                for start, end, actual_text in positions:
                    detections.append({
                        "type": det_type,
                        "original": actual_text,
                        "start": start,
                        "end": end,
                    })

            return {"detections": detections}

        except Exception as e:
            logger.exception("LLM service error")
            return {"detections": [], "error": str(e)}


    def _find_all_occurrences(self, text: str, original: str) -> list[tuple[int, int, str]]:
        """Find all occurrences of original text in the input text.
        
        Returns list of tuples: (start_pos, end_pos, actual_matched_text)
        """
        positions = []
        start_pos = 0
        
        # First try exact match
        while start_pos < len(text):
            pos = text.find(original, start_pos)
            if pos == -1:
                break
            positions.append((pos, pos + len(original), original))
            start_pos = pos + 1
        
        # If no exact matches found, try case-insensitive search
        if not positions:
            text_lower = text.lower()
            original_lower = original.lower()
            start_pos = 0
            
            while start_pos < len(text):
                pos = text_lower.find(original_lower, start_pos)
                if pos == -1:
                    break
                actual_text = text[pos:pos + len(original)]
                positions.append((pos, pos + len(original), actual_text))
                start_pos = pos + 1
        
        return positions


llm_service = LLMService()
