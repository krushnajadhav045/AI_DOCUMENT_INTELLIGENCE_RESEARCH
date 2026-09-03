from pathlib import Path

from pydantic_settings import BaseSettings


# ============================================================
# SETTINGS
# ============================================================

class Settings(BaseSettings):

    GEMINI_API_KEY: str = ""

    DATABASE_URL: str = (
        "sqlite:///./documents.db"
    )

    UPLOAD_DIR: str = "uploads"

    OUTPUT_DIR: str = "outputs"

    TEMP_DIR: str = "temp"

    MAX_FILE_SIZE_MB: int = 25

    class Config:

        env_file = ".env"


settings = Settings()


# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = Path(
    __file__
).resolve().parent


# ============================================================
# MAIN DIRECTORIES
# ============================================================

UPLOAD_PATH = (
    BASE_DIR /
    settings.UPLOAD_DIR
)

OUTPUT_PATH = (
    BASE_DIR /
    settings.OUTPUT_DIR
)

TEMP_PATH = (
    BASE_DIR /
    settings.TEMP_DIR
)


# ============================================================
# ALL REQUIRED DIRECTORIES
# ============================================================

directories = [

    # -----------------------------
    # Uploads
    # -----------------------------

    UPLOAD_PATH,

    UPLOAD_PATH /
    "original",

    UPLOAD_PATH /
    "pages",


    # -----------------------------
    # Outputs
    # -----------------------------

    OUTPUT_PATH,

    OUTPUT_PATH /
    "json",

    OUTPUT_PATH /
    "excel",

    OUTPUT_PATH /
    "sql",

    OUTPUT_PATH /
    "ocr",


    # -----------------------------
    # Temporary files
    # -----------------------------

    TEMP_PATH
]


# ============================================================
# CREATE DIRECTORIES
# ============================================================

for directory in directories:

    directory.mkdir(
        parents=True,
        exist_ok=True
    )


# ============================================================
# PRINT CONFIGURATION
# ============================================================

print(
    f"Project directory: {BASE_DIR}"
)

print(
    f"Upload directory: {UPLOAD_PATH}"
)

print(
    f"Output directory: {OUTPUT_PATH}"
)