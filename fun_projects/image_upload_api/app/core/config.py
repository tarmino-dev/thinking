import os

class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/app_db"
    )

    STORAGE_TYPE: str = os.getenv("STORAGE_TYPE", "local")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_S3_BUCKET: str = os.getenv("AWS_S3_BUCKET")
    AWS_REGION: str = os.getenv("AWS_REGION", "eu-central-1")

settings = Settings()