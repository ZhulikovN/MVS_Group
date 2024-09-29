from typing import Any, Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    app_name: str = "Image Processing App"

    redis_host: str = Field(default="redis", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=0, description="Redis database number")
    redis_url: Optional[str] = None

    DB_NAME: str = Field(default="", description="Имя базы данных")
    DB_USER: str = Field(default="", description="Имя пользователя базы данных")
    DB_PASSWORD: str = Field(default="", description="Пароль пользователя базы данных")
    DB_HOST: str = Field(default="", description="Хост базы данных")
    DB_PORT: int = Field(default=5432, description="Порт подключения к базе данных")
    API_DEBUG: bool = Field(
        default=False,
        description="Отладочный режим API",
    )
    database_url: Optional[str] = None

    processed_images_dir: str = Field(
        default="/app/processed_images",
        description="Директория для хранения обработанных изображений",
    )
    font_path: str = Field(
        default="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        description="Путь к файлу шрифта",
    )
    font_size: int = Field(default=12, description="Размер шрифта")

    API_HOST: str = Field(default="0.0.0.0", description="Хост API")
    API_PORT: int = Field(default=8000, description="Порт API")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def log_level(self) -> str:
        return "DEBUG" if self.API_DEBUG else "INFO"

    @property
    def database_url_psycopg(self) -> str:
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def database_url_asyncpg(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def redis_url_full(self) -> str:
        url = f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return url

    def __init__(self, **values: Any) -> None:
        super().__init__(**values)
        self.database_url: str = self.database_url_asyncpg
        self.redis_url: str = self.redis_url_full


settings = Settings()
