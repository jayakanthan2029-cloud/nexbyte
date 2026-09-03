from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "UrbanSenseAI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    DEBUG: bool = False
    
    # Server Settings
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    CORS_ORIGINS: list[str] = ["*"]
    
    # Database Settings
    DATABASE_URL: str = "postgresql://postgres:siharuvi@localhost:5432/urbansense"
    
    # Storage Settings
    MEDIA_DIR: str = "media"
    
    # Model Configuration
    YOLO_MODEL_PATH: str = "yolo11n.pt"
    URBAN_MODEL_PATH: str = "models/urban_model.pt"
    
    # System Flags
    DEMO_MODE: bool = True
    
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
