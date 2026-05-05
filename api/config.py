"""API Configuration"""

from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    """API Settings"""

    # API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", 8000))
    API_DEBUG: bool = os.getenv("API_DEBUG", "False").lower() == "true"

    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

    # CORS
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:admin@localhost:5432/smart-trade"
    )

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

    # Broker
    BROKER_DEFAULT: str = os.getenv("BROKER_DEFAULT", "angel_one")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
