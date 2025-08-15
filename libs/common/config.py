
import os

def get_required_env(var: str) -> str:
    """Get required environment variable or raise a clear error."""
    value = os.getenv(var)
    if value is None or value.strip() == "":
        raise EnvironmentError(f"Missing required environment variable: {var}")
    return value

class Config:
    # Database
    POSTGRES_USER = get_required_env("POSTGRES_USER")
    POSTGRES_PASSWORD = get_required_env("POSTGRES_PASSWORD")
    POSTGRES_HOST = get_required_env("POSTGRES_HOST")
    POSTGRES_PORT = get_required_env("POSTGRES_PORT")
    POSTGRES_DB = get_required_env("POSTGRES_DB")
    POSTGRES_DSN = (
        f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
        f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )

    # Redis
    REDIS_HOST = get_required_env("REDIS_HOST")
    REDIS_PORT = get_required_env("REDIS_PORT")
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"

    # MinIO
    MINIO_ENDPOINT = get_required_env("MINIO_ENDPOINT")
    MINIO_ROOT_USER = get_required_env("MINIO_ROOT_USER")
    MINIO_ROOT_PASSWORD = get_required_env("MINIO_ROOT_PASSWORD")
    MINIO_BUCKET = get_required_env("MINIO_BUCKET")

    # Blockchain APIs
    ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "")
    ETH_RPC_URL = os.getenv("ETH_RPC_URL", "")
    BLOCKSTREAM_API_BASE = os.getenv("BLOCKSTREAM_API_BASE", "https://blockstream.info/api")

    # Twilio / WhatsApp Alerts
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "")
    WHATSAPP_ALERT_TO = os.getenv("WHATSAPP_ALERT_TO", "")

    # Google Geolocation
    GOOGLE_GEOLOCATION_API_KEY = get_required_env("GOOGLE_GEOLOCATION_API_KEY")

    # Sentry
    SENTRY_DSN = os.getenv("SENTRY_DSN", "")

CFG = Config()
