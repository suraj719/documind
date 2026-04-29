from pathlib import Path

from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

LOGS_DIR = BASE_DIR / "logs"
if not LOGS_DIR.exists():
    LOGS_DIR.mkdir()

logger.add(
    sink=LOGS_DIR / "gui_{time:YYYYMMDD}.log",
    level="INFO",
    rotation="00:00",
    retention="7 days",
    compression="zip",
)


class Settings(BaseSettings):
    backend_base_url: str = "http://127.0.0.1:8000/api/v1"
    model_names: list[str] = ["qwen/qwen3.8-27b", "openai/gpt-oss-120b"]

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="allow")



settings = Settings()  # type: ignore
