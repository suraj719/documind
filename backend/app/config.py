import logging
from pathlib import Path

from loguru import logger
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

LOGS_DIR = BASE_DIR / "logs"
if not LOGS_DIR.exists():
    LOGS_DIR.mkdir()

logging.basicConfig(
    level=logging.INFO,  # For displaying the default model calling logs
)

logger.add(
    sink=LOGS_DIR / "api_{time:YYYYMMDD}.log",
    level="INFO",
    rotation="00:00",
    retention="7 days",
    compression="zip",
)


class Settings(BaseSettings):
    api_key: SecretStr = Field(alias="OPENAI_API_KEY")
    tavily_api_key: str | None = None
    model_provider: str = "groq"
    model_names: list[str] = ["qwen/qwen3.8-27b", "openai/gpt-oss-120b"]
    model_base_url: str | None = None
    embeddings_model_name: str = "text-embedding-3-large"
    embeddings_base_url: str | None = None
    token_bearer_url: str = "/api/v1/auth/login"
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expiry_mins: int = 1440
    refresh_token_expiry_days: int = 1
    postgres_host: str = "127.0.0.1"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = "test"
    postgres_database: str = "documind_db"
    pgvector_collection_name: str = "documind_embeddings"


    @property
    def is_remote_db(self) -> bool:
        return self.postgres_host not in ("127.0.0.1", "localhost", "documind_postgres")

    @property
    def database_uri(self) -> str:
        """Generate PostgreSQL connection string for sqlalchemy."""
        base = f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_database}"
        return f"{base}?ssl=require" if self.is_remote_db else base

    @property
    def checkpointer_uri(self) -> str:
        """Generate PostgreSQL connection string for checkpointer."""
        ssl_val = "require" if self.is_remote_db else "disable"
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_database}?sslmode={ssl_val}"

    @property
    def pgvector_connection(self) -> str:
        """Generate PostgreSQL connection string for PGVector."""
        base = f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_database}"
        return f"{base}?sslmode=require" if self.is_remote_db else base


    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="allow")


settings = Settings()  # type: ignore
