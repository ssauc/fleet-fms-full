from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    project_name: str = "fleet-fms"
    timezone: str = "America/Chicago"
    postgres_db: str = "fleet"
    postgres_user: str = "fleet"
    postgres_password: str = "fleetpass"
    postgres_host: str = "db"
    postgres_port: int = 5432
    api_jwt_secret: str = "change_me"
    api_jwt_expires_min: int = 120
    allowed_origins: str = "http://localhost:3000"
    redis_url: str = "redis://redis:6379/0"

    @property
    def database_url(self):
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

settings = Settings()
