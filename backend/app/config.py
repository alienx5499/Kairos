import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://kairos:kairos@localhost:5432/kairos"
)
# force psycopg2 driver for bare postgresql:// urls
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

APP_NAME = os.getenv("APP_NAME", "Kairos SRE Incident Engine")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
PORT = int(os.getenv("PORT", "8000"))
