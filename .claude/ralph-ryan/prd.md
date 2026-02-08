# PRD: Alta-Lex PII Masking Web Application

## 1. Introduction

Alta-Lex PII Masking is a modern, tech-themed web application that allows users to detect and mask Personally Identifiable Information (PII) from text and documents. Users can either paste text directly or upload documents (TXT, PDF, DOCX, CSV, Excel). The system supports **dual inference modes**:

1. **Local mode (Production):** Qwen3-0.6B deployed locally via vLLM, served as an OpenAI-compatible API
2. **Cloud mode (Testing):** Alibaba Cloud DashScope API (Bailian platform) for quick testing without local GPU

Users can customize which PII categories to mask (e.g., phone numbers, email addresses, names, addresses, ID numbers, etc.).

**Company:** Alta-Lex (https://www.alta-lex.ai/)

## 2. Goals

- Provide a sleek, modern, tech-feel web UI branded for Alta-Lex
- Allow users to input text directly or upload documents (TXT, PDF, DOCX, CSV, XLSX)
- Deploy Qwen3-0.6B locally via vLLM as the primary inference backend
- Support DashScope cloud API as a testing/fallback option
- Let users customize PII categories to mask
- Display masked output with PII replaced by `████` blocks
- Achieve <3s response time for typical text inputs

## 3. User Stories

### US-001: Project Scaffolding
**Description:** As a developer, I want the project scaffolded with a React+TypeScript+Vite frontend and Python FastAPI backend so that development can begin.

**Acceptance Criteria:**
- [ ] Frontend: React + TypeScript + Vite project initialized in `frontend/`
- [ ] Backend: Python FastAPI project initialized in `backend/`
- [ ] `backend/requirements.txt` includes fastapi, uvicorn, python-multipart, openai, python-docx, PyPDF2, openpyxl, pandas
- [ ] `frontend/package.json` includes react, typescript, vite, axios
- [ ] `.env.example` created in `backend/` with placeholder for API key and model config
- [ ] `.env` created in `backend/` with actual DashScope API key for testing
- [ ] `.gitignore` covers `.env`, `node_modules/`, `__pycache__/`, `dist/`
- [ ] Backend runs on port 8000, frontend on port 5173
- [ ] Typecheck passes

### US-002: Backend - Dual-Mode LLM Service (vLLM Local + DashScope Cloud)
**Description:** As a developer, I want the backend to support both local vLLM and cloud DashScope API so that we can test with cloud and deploy with local inference.

**Acceptance Criteria:**
- [ ] `backend/.env` supports configuration: `LLM_MODE=cloud|local`, `LLM_API_BASE`, `LLM_API_KEY`, `LLM_MODEL`
- [ ] Cloud mode defaults: `LLM_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1`, `LLM_MODEL=qwen3-0.6b`
- [ ] Local mode defaults: `LLM_API_BASE=http://localhost:8000/v1`, `LLM_MODEL=Qwen/Qwen3-0.6B`, `LLM_API_KEY=EMPTY`
- [ ] A unified `LLMService` class that uses OpenAI SDK to call either endpoint
- [ ] `backend/scripts/start_vllm.sh` script: `vllm serve Qwen/Qwen3-0.6B --port 8001 --enable-reasoning --reasoning-parser deepseek_r1`
- [ ] README documents both modes with setup instructions
- [ ] Typecheck passes

### US-003: Backend - Document Parsing Service
**Description:** As a user, I want to upload TXT, PDF, DOCX, CSV, and Excel files so that the system can extract text for PII detection.

**Acceptance Criteria:**
- [ ] POST `/api/upload` endpoint accepts file uploads
- [ ] Parses `.txt` files to plain text
- [ ] Parses `.pdf` files to plain text (using PyPDF2)
- [ ] Parses `.docx` files to plain text (using python-docx)
- [ ] Parses `.csv` and `.xlsx` files to plain text (using pandas)
- [ ] Returns extracted text as JSON `{ "text": "..." }`
- [ ] Returns 400 error for unsupported file types
- [ ] Typecheck passes

### US-004: Backend - PII Detection & Masking Endpoint
**Description:** As a user, I want the system to detect and mask PII in my text using Qwen3-0.6B so that sensitive information is hidden.

**Acceptance Criteria:**
- [ ] POST `/api/mask` endpoint accepts `{ "text": "...", "categories": [...] }`
- [ ] Uses `LLMService` (from US-002) to call Qwen3-0.6B
- [ ] Sends a carefully crafted prompt instructing the model to identify PII by category and return structured JSON
- [ ] Default categories: `["name", "phone", "email", "address", "id_number", "bank_card", "social_media"]`
- [ ] Returns `{ "masked_text": "...", "detections": [{"type": "phone", "original": "138xxxx", "position": [start, end]}] }`
- [ ] PII is replaced with `████` in the masked text
- [ ] Handles API errors gracefully with proper error responses
- [ ] Typecheck passes

### US-005: Frontend - Layout & Alta-Lex Branding
**Description:** As a user, I want a modern, tech-themed UI with Alta-Lex branding so that the app feels professional and futuristic.

**Acceptance Criteria:**
- [ ] Dark theme with gradient accents (deep blue/purple/cyan palette)
- [ ] Top navbar with Alta-Lex logo area, company name "Alta-Lex", and tagline "PII Shield"
- [ ] Main content area split into input panel (left) and output panel (right)
- [ ] Subtle grid/circuit-board background pattern or animated particles for tech feel
- [ ] Responsive layout that works on desktop (min 1024px width)
- [ ] Footer with "Powered by Alta-Lex AI" and link to https://www.alta-lex.ai/
- [ ] CSS uses modern approach (CSS modules or Tailwind-style utility classes)
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill

### US-006: Frontend - Text Input & File Upload Panel
**Description:** As a user, I want to type or paste text and upload documents so that I can submit content for PII masking.

**Acceptance Criteria:**
- [ ] Large textarea for direct text input with placeholder text
- [ ] File upload area with drag-and-drop support
- [ ] Shows accepted file types: TXT, PDF, DOCX, CSV, XLSX
- [ ] When a file is uploaded, extracts text via `/api/upload` and populates textarea
- [ ] Upload shows file name and a remove button after upload
- [ ] "Mask PII" button to trigger masking
- [ ] Loading spinner/animation while processing
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill

### US-007: Frontend - PII Category Configuration
**Description:** As a user, I want to select which PII categories to mask so that I have control over what gets masked.

**Acceptance Criteria:**
- [ ] Collapsible/expandable panel showing PII categories as toggle switches
- [ ] Default categories (all ON): Name, Phone, Email, Address, ID Number, Bank Card, Social Media
- [ ] Each toggle has an icon and label
- [ ] Users can add custom category via text input + add button
- [ ] Selected categories are sent to `/api/mask` endpoint
- [ ] Settings persist during session (React state)
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill

### US-008: Frontend - Masked Output Display
**Description:** As a user, I want to see the masked output clearly so that I can verify which PII was detected and masked.

**Acceptance Criteria:**
- [ ] Output panel displays masked text with `████` blocks styled with a highlight color (e.g., red/orange background)
- [ ] Masked blocks are visually distinct from normal text
- [ ] A summary section below output shows count of detections per PII type
- [ ] "Copy to Clipboard" button copies masked text
- [ ] Empty state shows a placeholder message when no output yet
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill

### US-009: Integration & End-to-End Flow
**Description:** As a user, I want the full flow to work end-to-end: input text -> configure categories -> mask -> see output.

**Acceptance Criteria:**
- [ ] Frontend calls backend API correctly with CORS enabled
- [ ] Text input -> click "Mask PII" -> masked output displays
- [ ] File upload -> text extracted -> click "Mask PII" -> masked output displays
- [ ] Category toggles affect masking results
- [ ] Error states displayed to user (API failure, empty input, etc.)
- [ ] Backend CORS allows frontend origin
- [ ] Test with DashScope cloud API to verify end-to-end
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill

### US-010: Backend Unit & Integration Tests
**Description:** As a developer, I want comprehensive backend tests so that all API endpoints and services are verified.

**Acceptance Criteria:**
- [ ] `backend/tests/` directory with pytest test files
- [ ] Unit tests for document parsing: test each file type (TXT, PDF, DOCX, CSV, XLSX)
- [ ] Unit tests for LLMService: mock API calls, test cloud and local mode config
- [ ] Unit tests for PII masking logic: test prompt construction, response parsing, masking replacement
- [ ] Integration tests for `/api/upload` endpoint with sample files
- [ ] Integration tests for `/api/mask` endpoint with DashScope cloud API (real API call)
- [ ] Test edge cases: empty input, unsupported file type, API timeout, malformed LLM response
- [ ] All tests pass with `pytest backend/tests/ -v`
- [ ] Test results output to `backend/tests/test_report.txt`
- [ ] Typecheck passes

### US-011: Frontend Tests
**Description:** As a developer, I want frontend component tests so that UI behavior is verified.

**Acceptance Criteria:**
- [ ] Vitest configured in `frontend/` for React component testing
- [ ] Tests for text input component: typing, clearing, placeholder
- [ ] Tests for file upload component: drag-and-drop simulation, file type validation
- [ ] Tests for PII category toggles: enable/disable, custom category add
- [ ] Tests for output display: masked text rendering, copy-to-clipboard
- [ ] Tests for API integration: mock axios calls, loading states, error states
- [ ] All tests pass with `npm run test` in `frontend/`
- [ ] Typecheck passes

### US-012: Test Report & Quality Summary
**Description:** As a stakeholder, I want a comprehensive test report documenting test coverage, results, and PII detection accuracy.

**Acceptance Criteria:**
- [ ] `docs/test-report.md` created with structured test results
- [ ] Section 1: Backend test results summary (pass/fail counts, coverage)
- [ ] Section 2: Frontend test results summary (pass/fail counts)
- [ ] Section 3: PII detection accuracy test - run 10+ diverse test cases through DashScope API, document input/output/correctness
- [ ] Section 4: Test cases table with columns: ID, Description, Input, Expected Output, Actual Output, Pass/Fail
- [ ] Section 5: Performance metrics (API response times for sample inputs)
- [ ] Section 6: Known limitations and edge cases
- [ ] All sample PII test cases cover: names, phone numbers, emails, addresses, ID numbers, bank cards, social media handles
- [ ] Include both English and Chinese PII test cases
- [ ] Typecheck passes

### US-013: Deployment & User Documentation
**Description:** As a developer/operator, I want comprehensive documentation for deploying, configuring, and using the application.

**Acceptance Criteria:**
- [ ] `README.md` at project root with: project overview, architecture diagram, quick start guide
- [ ] `docs/deployment.md` with: system requirements, vLLM local setup (GPU requirements, model download, startup), DashScope cloud setup, Docker deployment option (Dockerfile for backend), environment variables reference, port configuration
- [ ] `docs/user-guide.md` with: feature walkthrough, how to input text, how to upload documents, how to configure PII categories, how to read masked output, screenshots/examples
- [ ] `docs/api-reference.md` with: all API endpoints documented (method, URL, request body, response body, error codes), example curl commands
- [ ] `backend/Dockerfile` for containerized backend deployment
- [ ] `docker-compose.yml` at project root for full-stack deployment (backend + frontend + optional vLLM)
- [ ] Typecheck passes

## 4. Functional Requirements

- FR-1: The system must accept text input directly via a textarea
- FR-2: The system must accept document uploads in TXT, PDF, DOCX, CSV, and XLSX formats
- FR-3: The system must extract plain text from uploaded documents
- FR-4: The system must support dual inference: local vLLM and cloud DashScope API
- FR-5: The system must call Qwen3-0.6B to detect PII
- FR-6: The system must allow users to configure which PII categories to detect
- FR-7: The system must replace detected PII with `████` blocks
- FR-8: The system must display masked output with visual highlighting
- FR-9: The system must provide a copy-to-clipboard function for masked output
- FR-10: The system must handle errors gracefully with user-friendly messages
- FR-11: The system must support CORS for frontend-backend communication

## 5. Non-Goals

- User authentication / login system
- Persistent storage of documents or results
- Batch processing of multiple documents
- Model fine-tuning or training
- Mobile-optimized responsive design (desktop-first)
- Download masked documents in original format

## 6. Technical Considerations

### Backend
- **Framework:** FastAPI (Python)
- **Dual Inference Mode:**
  - **Local (Production):** vLLM serving Qwen3-0.6B on port 8001
    - Command: `vllm serve Qwen/Qwen3-0.6B --port 8001 --enable-reasoning --reasoning-parser deepseek_r1`
    - Endpoint: `http://localhost:8001/v1`
  - **Cloud (Testing):** Alibaba Cloud DashScope (Bailian platform)
    - Endpoint: `https://dashscope.aliyuncs.com/compatible-mode/v1`
    - Model: `qwen3-0.6b`
    - API Key: `sk-76b89a81018e490c973de7251f899422` (stored in `.env`, never committed)
- **Both modes use OpenAI-compatible API**, so a single `LLMService` class handles both
- **Document Parsing:** PyPDF2, python-docx, pandas, openpyxl
- **CORS:** Allow frontend origin (localhost:5173 in dev)
- **Backend API port:** 8000 (vLLM runs on 8001 to avoid conflict)

### Frontend
- **Framework:** React 18+ with TypeScript
- **Build Tool:** Vite
- **HTTP Client:** Axios
- **Styling:** CSS with modern dark theme, gradients, animations
- **Color Palette:** Dark backgrounds (#0a0a1a, #1a1a2e), cyan/blue accents (#00d4ff, #7b2ff7), text (#e0e0e0)

### Prompt Engineering Strategy
The Qwen3-0.6B model will be prompted with a structured instruction to:
1. Analyze the input text for specified PII categories
2. Return a JSON response listing each detected PII item with type, value, and position
3. Use non-thinking mode for faster responses (cloud: extra_body parameter; local: handled by vLLM parser)
4. The prompt will instruct the model to act as a PII detection specialist

### Architecture
```
                                  ┌─────────────────────────────┐
                                  │  Qwen3-0.6B Inference       │
                                  │                             │
                                  │  [Local] vLLM :8001         │
[React Frontend] ──HTTP──▶ [FastAPI Backend :8000] ──API──▶     │
      │                          │                │  [Cloud] DashScope API  │
      │                    [Document Parser]       └─────────────────────────────┘
      │                    (PyPDF2, docx, pandas)
      │
  [User Browser :5173]
```
