import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME = "Omdena Public Service Assistant"
    APP_VERSION = "0.2.0"
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
    MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-small-2506")
    ENVIRONMENT = os.getenv("APP_ENV", "development")


settings = Settings()