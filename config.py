from pydantic_settings import BaseSettings
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "system.db"
MODELS_DIR = DATA_DIR / "models"
VIDEOS_DIR = DATA_DIR / "videos"

DATA_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    PROJECT_NAME: str = "Aeronex High-Altitude Anti-Drone System"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = f"sqlite:///{DATABASE_PATH}"
    
    # Simulation defaults
    SIM_TICK_SECONDS: float = 1.0
    DEFAULT_ALTITUDE_METERS: float = 1000.0
    
    # AI settings
    YOLO_MODEL_NAME: str = "yolov8n.pt"
    YOLO_CONFIDENCE_THRESHOLD: float = 0.35
    DEFAULT_CAMERA_INDEX: int = 0
    USE_SIMULATED_AI_FALLBACK: bool = True
    
    # System health thresholds
    CPU_TEMP_WARN: float = 75.0
    CPU_TEMP_CRIT: float = 85.0
    CPU_USAGE_WARN: float = 80.0
    CPU_USAGE_CRIT: float = 95.0
    FPS_WARN: float = 12.0
    FPS_CRIT: float = 5.0
    LATENCY_WARN_MS: float = 85.0
    LATENCY_CRIT_MS: float = 150.0
    VIBRATION_WARN: float = 0.50
    VIBRATION_CRIT: float = 0.80

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
