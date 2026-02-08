# Deployment Guide

## System Requirements

### Minimum (Cloud Mode)
- CPU: 2 cores
- RAM: 4 GB
- Disk: 1 GB
- Python 3.10+
- Node.js 18+
- Internet connection (for DashScope API)

### Recommended (Local vLLM Mode)
- CPU: 8 cores
- RAM: 16 GB
- GPU: NVIDIA GPU with 4+ GB VRAM (for vLLM)
- Disk: 10 GB (model weights ~1.2 GB)
- Python 3.10+
- Node.js 18+
- CUDA 12.0+

---

## Option 1: Manual Deployment

### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
```

Edit `.env` with your configuration:

```env
LLM_MODE=cloud
LLM_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_API_KEY=sk-your-dashscope-api-key
LLM_MODEL=qwen3-0.6b
```

Start the backend:

```bash
cd ..  # Return to project root
PYTHONPATH=. uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Development mode
npm run dev

# OR Production build
npm run build
npm run preview
```

### Local vLLM Setup (GPU Required)

1. Install vLLM:

```bash
pip install vllm
```

2. Download and serve the model:

```bash
vllm serve Qwen/Qwen3-0.6B --port 8001 --enable-reasoning --reasoning-parser deepseek_r1
```

Or use the provided script:

```bash
chmod +x backend/scripts/start_vllm.sh
./backend/scripts/start_vllm.sh
```

3. Update `.env`:

```env
LLM_MODE=local
LLM_API_BASE=http://localhost:8001/v1
LLM_API_KEY=EMPTY
LLM_MODEL=Qwen/Qwen3-0.6B
```

---

## Option 2: Docker Deployment

### Backend Only

```bash
cd backend
docker build -t alta-lex-backend .
docker run -p 8000:8000 --env-file .env alta-lex-backend
```

### Full Stack (docker-compose)

```bash
# From project root
docker-compose up -d
```

This starts:
- **backend** on port 8000
- **frontend** on port 5173

To include local vLLM:

```bash
docker-compose --profile gpu up -d
```

---

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_MODE` | `cloud` | `cloud` for DashScope, `local` for vLLM |
| `LLM_API_BASE` | `https://dashscope.aliyuncs.com/compatible-mode/v1` | API base URL |
| `LLM_API_KEY` | `EMPTY` | API key (required for cloud mode) |
| `LLM_MODEL` | `qwen3-0.6b` | Model name |

---

## Port Configuration

| Service | Default Port | Configurable |
|---------|-------------|-------------|
| Frontend (dev) | 5173 | `vite.config.ts` |
| Backend API | 8000 | `uvicorn --port` |
| vLLM (local) | 8001 | `start_vllm.sh` |

---

## DashScope Cloud Setup

1. Sign up at [Alibaba Cloud DashScope](https://dashscope.console.aliyun.com/)
2. Create an API key in the console
3. Set `LLM_API_KEY` in your `.env` file
4. Use model name `qwen3-0.6b` (or other available Qwen models)

---

## Troubleshooting

### Backend won't start
- Ensure `PYTHONPATH` includes the project root: `PYTHONPATH=. uvicorn ...`
- Check that `.env` file exists and has correct values

### Frontend CORS errors
- Ensure backend CORS allows the frontend origin (check `main.py`)
- Default allowed origins: `localhost:5173`, `localhost:5174`, `localhost:5175`

### LLM API errors
- Cloud mode: verify API key is valid and has credits
- Local mode: ensure vLLM is running on the configured port
- Check `LLM_API_BASE` matches the actual endpoint

### vLLM GPU issues
- Ensure CUDA is installed: `nvidia-smi`
- Check GPU memory: Qwen3-0.6B requires ~2 GB VRAM
- Try `--dtype float16` if running out of memory
