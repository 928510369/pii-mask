# API Reference

**Base URL:** `http://localhost:8000`

---

## Endpoints

### GET /api/health

Health check endpoint.

**Response:**

```json
{
  "status": "ok",
  "service": "Alta-Lex PII Shield"
}
```

**Example:**

```bash
curl http://localhost:8000/api/health
```

---

### POST /api/upload

Upload a document and extract text content.

**Content-Type:** `multipart/form-data`

**Request:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | File | Yes | Document file to parse |

**Supported file types:** `.txt`, `.pdf`, `.docx`, `.csv`, `.xlsx`

**Success Response (200):**

```json
{
  "text": "Extracted text content from the document..."
}
```

**Error Response (400):**

```json
{
  "detail": "Unsupported file type: .xyz. Supported types: .txt, .pdf, .docx, .csv, .xlsx"
}
```

**Examples:**

```bash
# Upload a text file
curl -F "file=@document.txt" http://localhost:8000/api/upload

# Upload a PDF
curl -F "file=@report.pdf" http://localhost:8000/api/upload

# Upload a Word document
curl -F "file=@contract.docx" http://localhost:8000/api/upload

# Upload a CSV
curl -F "file=@data.csv" http://localhost:8000/api/upload

# Upload an Excel file
curl -F "file=@spreadsheet.xlsx" http://localhost:8000/api/upload
```

---

### POST /api/mask

Detect and mask PII in text.

**Content-Type:** `application/json`

**Request Body:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `text` | string | Yes | - | Text to analyze for PII |
| `categories` | string[] | No | All 7 defaults | PII categories to detect |

**Default categories:** `["name", "phone", "email", "address", "id_number", "bank_card", "social_media"]`

**Success Response (200):**

```json
{
  "masked_text": "Contact ████ at ████ or ████.",
  "detections": [
    {
      "type": "name",
      "original": "John Smith",
      "start": 8,
      "end": 18
    },
    {
      "type": "email",
      "original": "john@test.com",
      "start": 22,
      "end": 35
    },
    {
      "type": "phone",
      "original": "555-123-4567",
      "start": 39,
      "end": 51
    }
  ]
}
```

**Detection Object:**

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | PII category (e.g., "name", "phone") |
| `original` | string | The original PII text |
| `start` | integer | Start position in original text |
| `end` | integer | End position in original text |

**Error Responses:**

| Code | Detail | Cause |
|------|--------|-------|
| 400 | "Text cannot be empty" | Empty or whitespace-only text |
| 502 | "LLM service error: ..." | LLM API call failed |

**Examples:**

```bash
# Basic masking with all categories
curl -X POST http://localhost:8000/api/mask \
  -H "Content-Type: application/json" \
  -d '{
    "text": "My name is John Smith, email john@test.com",
    "categories": ["name", "phone", "email", "address"]
  }'

# Chinese text
curl -X POST http://localhost:8000/api/mask \
  -H "Content-Type: application/json" \
  -d '{
    "text": "张三的电话是13812345678",
    "categories": ["name", "phone"]
  }'

# Default categories (all 7)
curl -X POST http://localhost:8000/api/mask \
  -H "Content-Type: application/json" \
  -d '{"text": "Contact alice@company.com for details."}'

# Custom categories
curl -X POST http://localhost:8000/api/mask \
  -H "Content-Type: application/json" \
  -d '{
    "text": "SSN: 123-45-6789, passport: AB1234567",
    "categories": ["ssn", "passport"]
  }'
```

---

## Error Handling

All error responses follow the format:

```json
{
  "detail": "Human-readable error message"
}
```

| HTTP Code | Meaning |
|-----------|---------|
| 200 | Success |
| 400 | Bad request (invalid input) |
| 422 | Validation error (malformed JSON) |
| 502 | LLM service error |

---

## Rate Limits

- **Cloud mode (DashScope):** Subject to DashScope API rate limits
- **Local mode (vLLM):** Limited by GPU throughput
- **Request timeout:** 60 seconds (configurable in frontend)

---

## CORS

The backend allows requests from:
- `http://localhost:5173`
- `http://localhost:5174`
- `http://localhost:5175`

To add additional origins, modify the `allow_origins` list in `backend/app/main.py`.
