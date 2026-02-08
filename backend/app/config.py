import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))


class Settings:
    LLM_MODE: str = os.getenv("LLM_MODE", "cloud")
    LLM_API_BASE: str = os.getenv(
        "LLM_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "EMPTY")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen3-0.6b")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))


settings = Settings()
