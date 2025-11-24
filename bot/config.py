from pydantic_settings import BaseSettings


class BotSettings(BaseSettings):
    BOT_TOKEN: str = "8350395273:AAEFuqUZi7Gpaq1MCzM2Cn3HbmguI37lECg"
    BACKEND_URL: str = "https://subs-saas.onrender.com"
    DEFAULT_LANGUAGE: str = "en"

    class Config:
        env_file = ".env"


settings = BotSettings()
