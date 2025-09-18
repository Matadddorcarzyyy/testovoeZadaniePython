from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_dsn: str
    wb_base_url: str = "https://feedbacks1.wb.ru/feedbacks/v1"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()