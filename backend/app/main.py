from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .document_parser import parse_document

app = FastAPI(
    title="Alta-Lex PII Shield",
    description="PII Masking API powered by Qwen3-0.6B",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MaskRequest(BaseModel):
    text: str
    categories: list[str] = [
        "name", "phone", "email", "address",
        "id_number", "bank_card", "social_media",
    ]


class Detection(BaseModel):
    type: str
    original: str
    start: int
    end: int


class MaskResponse(BaseModel):
    masked_text: str
    detections: list[Detection]


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "Alta-Lex PII Shield"}


@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    content = await file.read()

    try:
        text = parse_document(file.filename, content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"text": text}


@app.post("/api/mask", response_model=MaskResponse)
async def mask_pii(request: MaskRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    from .llm_service import llm_service

    result = await llm_service.detect_pii(request.text, request.categories)

    if "error" in result and not result["detections"]:
        raise HTTPException(
            status_code=502,
            detail=f"LLM service error: {result['error']}",
        )

    # Build masked text by replacing detections (process from end to start)
    detections = sorted(result["detections"], key=lambda d: d["start"], reverse=True)
    masked_text = request.text

    for det in detections:
        start = det["start"]
        end = det["end"]
        if 0 <= start < end <= len(masked_text):
            masked_text = masked_text[:start] + "████" + masked_text[end:]

    # Re-sort detections by position for output
    detections_sorted = sorted(result["detections"], key=lambda d: d["start"])

    return MaskResponse(
        masked_text=masked_text,
        detections=[Detection(**d) for d in detections_sorted],
    )
