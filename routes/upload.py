from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, HTTPException


router = APIRouter(
    prefix="/api/documents",
    tags=["Upload"]
)


# ============================================================
# BASE DIRECTORIES
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

UPLOADS_DIR = BASE_DIR / "uploads"

UPLOADS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# SUPPORTED FILE TYPES
# ============================================================

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".bmp",
    ".tiff",
    ".tif"
}


# ============================================================
# UPLOAD DOCUMENT
# ============================================================

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    # --------------------------------------------------------
    # CHECK FILE NAME
    # --------------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected"
        )

    # --------------------------------------------------------
    # CHECK EXTENSION
    # --------------------------------------------------------

    extension = Path(
        file.filename
    ).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type: {extension}. "
                f"Supported types: PDF, PNG, JPG, JPEG, "
                f"WEBP, BMP, TIFF"
            )
        )

    # --------------------------------------------------------
    # CREATE DOCUMENT ID
    # --------------------------------------------------------

    document_id = str(uuid4())

    # --------------------------------------------------------
    # CREATE DOCUMENT DIRECTORY
    # --------------------------------------------------------

    document_dir = (
        UPLOADS_DIR /
        document_id
    )

    document_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # SAFE FILE NAME
    # --------------------------------------------------------

    original_name = Path(
        file.filename
    ).name

    file_path = (
        document_dir /
        original_name
    )

    # --------------------------------------------------------
    # SAVE FILE
    # --------------------------------------------------------

    try:

        with open(
            file_path,
            "wb"
        ) as buffer:

            while True:

                chunk = await file.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                buffer.write(chunk)

    except Exception as e:

        # Remove failed upload directory
        if document_dir.exists():

            import shutil

            shutil.rmtree(
                document_dir,
                ignore_errors=True
            )

        raise HTTPException(
            status_code=500,
            detail=f"File upload failed: {str(e)}"
        )

    finally:

        await file.close()

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {

        "success": True,

        "status": "uploaded",

        "document_id":
            document_id,

        "filename":
            original_name,

        "file_type":
            extension,

        "message":
            "Document uploaded successfully",

        "next_step":
            f"/api/documents/process/{document_id}"

    }