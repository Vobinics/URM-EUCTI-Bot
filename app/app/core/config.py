from pathlib import Path
from typing import Any, Dict, Optional, List

from pydantic import BaseSettings, PostgresDsn, validator

BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    API_TOKEN: str
    ADMINS_IDS: List[int] = []
    CHAT_ID: int
    DEBUG: bool = False
    DATA_FOLDER: Path = BASE_DIR / 'data'

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:  # noqa
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    class Config:
        case_sensitive = True


settings = Settings()
