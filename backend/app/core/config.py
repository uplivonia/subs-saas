from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = "Telegram Subscription SaaS"
    API_V1_STR: str = "/api/v1"

    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "app"
    POSTGRES_PASSWORD: str = "app"
    POSTGRES_DB: str = "app"

    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")

    BACKEND_PUBLIC_URL: str = os.getenv("BACKEND_PUBLIC_URL", "")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "https://fanstero.netlify.app")

    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "8350395273:AAEFuqUZi7Gpaq1MCzM2Cn3HbmguI37lECg")

    SECRET_KEY: str = (
        "4c52f9b0b2a64a0d847d9300dcf742b2a0a6c97f8c1b49e9b6e15a84f3fdc9ad"
    )

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()



