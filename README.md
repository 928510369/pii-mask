# Alta-Lex PII Shield

A modern web application for detecting and masking Personally Identifiable Information (PII) from text and documents, powered by Qwen3-0.6B.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Frontend (React)                   │
│          Vite + TypeScript + Axios                   │
│              HTTPS:443                                │
└───────────────────────┬─────────────────────────────┘
                        │ HTTPS (REST API)
┌───────────────────────▼─────────────────────────────┐
│                Backend (FastAPI)                      │
│          Document Parser + PII Masking               │
│              Internal Port: 8000                     │
└───────────────────────┬─────────────────────────────┘
                        │ OpenAI-compatible API
┌───────────────────────▼─────────────────────────────┐
│              LLM Service (Qwen3-0.6B)                │
│    Cloud: DashScope API  |  Local: vLLM (port 8001)  │
└─────────────────────────────────────────────────────┘
```

## Features

- **Text Input:** Paste or type text containing PII
- **Document Upload:** Drag-and-drop support for TXT, PDF, DOCX, CSV, XLSX
- **Configurable Categories:** Toggle PII types (name, phone, email, address, ID, bank card, social media) + custom categories
- **Visual Masking:** PII replaced with highlighted ████ blocks
- **Detection Summary:** Badge counts per PII type
- **Copy to Clipboard:** One-click copy of masked output
- **Dual LLM Mode:** Cloud (DashScope) or local (vLLM) inference

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn

### 1. Clone and Setup

```bash
git clone <repository-url>
cd pii-mask
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API key and configuration
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

### 4. Start Services

```bash
# Terminal 1: Backend
cd backend
PYTHONPATH=.. uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 5. Open in Browser

Navigate to http://localhost:5173

## Configuration

Edit `backend/.env`:

```env
# Cloud mode (DashScope)
LLM_MODE=cloud
LLM_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_API_KEY=your-api-key
LLM_MODEL=qwen3-0.6b

# Local mode (vLLM)
LLM_MODE=local
LLM_API_BASE=http://localhost:8001/v1
LLM_API_KEY=EMPTY
LLM_MODEL=Qwen/Qwen3-0.6B
```

## Documentation

- [Deployment Guide](docs/deployment.md)
- [User Guide](docs/user-guide.md)
- [API Reference](docs/api-reference.md)
- [Test Report](docs/test-report.md)

## Testing

```bash
# Backend tests
cd pii-mask
PYTHONPATH=. python3 -m pytest backend/tests/ -v

# Frontend tests
cd frontend
npm run test
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, TypeScript, Vite 7, Axios |
| Backend | Python, FastAPI, Pydantic |
| LLM | Qwen3-0.6B via OpenAI SDK |
| Inference | DashScope (cloud) / vLLM (local) |
| Testing | pytest, Vitest, @testing-library/react |

## License

Proprietary - Alta-Lex AI
