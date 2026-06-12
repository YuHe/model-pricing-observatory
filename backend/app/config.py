from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_url: str = "postgresql+asyncpg://pricing:pricing@postgres:5432/pricing"
    redis_url: str = "redis://redis:6379/0"
    admin_api_key: str = "change-me-in-production"
    domain: str = "price.ihope.cc"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_pass: str = ""
    alert_webhook_url: str = ""
    together_api_key: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
