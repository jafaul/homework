import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic.v1 import BaseSettings

load_dotenv()


class Settings(BaseSettings):

    DB_USERNAME: str = os.environ.get("DB_USERNAME", "postgres")
    DB_PASSWORD: str = os.environ.get("DB_PASSWORD", "example")

    APP_HOST: str = os.environ.get("HOST", "0.0.0.0")
    APP_PORT: int = os.environ.get("PORT", 8000)

    DB_HOST: str = os.environ.get("DB_HOST", "db")
    DB_PORT: int = os.environ.get("DB_PORT", 5432)
    DB_NAME: str = os.environ.get("DB_NAME", "postgres")

    SECRET_KEY: str = os.environ.get("SECRET_KEY", "VerySecretKey")
    DEBUG: bool = os.environ.get("DEBUG", False)

    DB_URL: str = \
        f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


    class Config:
        env_file = "../.env"


@lru_cache()
def get_config():
    return Settings()


config = get_config()
