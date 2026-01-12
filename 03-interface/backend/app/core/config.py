import os

class Settings:
    PROJECT_NAME: str = "Smart Meeting Scribe API V5"
    
    # --- Redis ---
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379")
    
    # --- MinIO (S3) ---
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "minio:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ROOT_USER", "admin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_ROOT_PASSWORD", "minio_admin_password")
    MINIO_BUCKET_AUDIO: str = "uploads"
    STORAGE_PROTOCOL: str = "s3"

    # --- Postgres (DB) ---
    # Format: postgresql+asyncpg://user:password@host:port/dbname
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "app")
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:5432/{self.POSTGRES_DB}"

    # --- Sécurité ---
    SECRET_KEY: str = os.getenv("SECRET_KEY", "CHANGE_ME_IN_PROD_SUPER_SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()
