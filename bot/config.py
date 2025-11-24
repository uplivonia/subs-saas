from pydantic_settings import BaseSettings


class BotSettings(BaseSettings):
    BOT_TOKEN: str = "8350395273:AAEFuqUZi7Gpaq1MCzM2Cn3HbmguI37lECg"
    BACKEND_URL: str = "http://127.0.0.1:8000"
    DEFAULT_LANGUAGE: str = "en"

    class Config:
        env_file = ".env"


settings = BotSettings()
