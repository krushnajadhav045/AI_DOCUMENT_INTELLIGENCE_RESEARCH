from pathlib import Path
import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from config import (
    UPLOAD_PATH,
    OUTPUT_PATH
)


router = APIRouter(
    prefix="/api/documents",
    tags=["Downloads"]
)


# ============================================================
# FIND ORIGINAL DOCUMENT
# ============================================================

def find_original_file(
    document_id: str
):
    doc_dir = UPLOAD_PATH / document_id
    if doc_dir.exists() and doc_dir.is_dir():
        files = [f for f in doc_dir.iterdir() if f.is_file()]
        if files:
            return files[0]

    original_dir = (
        UPLOAD_PATH /
        "original"
    )

    for extension in [
        ".pdf",
        ".png",
        ".jpg",
        ".jpeg"
    ]:

        file_path = (
            original_dir /
            f"{document_id}{extension}"
        )

        if file_path.exists():

            return file_path

    return None



# ============================================================
# JSON DOWNLOAD
# ============================================================

@router.get(
    "/{document_id}/download/json"
)
async def download_json(
    document_id: str
):

    json_file = (
        OUTPUT_PATH /
        "ocr" /
        document_id /
        "json" /
        "document_result.json"
    )

    if not json_file.exists():

        raise HTTPException(
            status_code=404,
            detail="JSON result not found. Process the document first."
        )

    return FileResponse(

        path=str(json_file),

        media_type="application/json",

        filename=(
            f"{document_id}_result.json"
        )
    )


# ============================================================
# ORIGINAL PDF DOWNLOAD
# ============================================================

@router.get(
    "/{document_id}/download/original"
)
async def download_original(
    document_id: str
):

    file_path = find_original_file(
        document_id
    )

    if file_path is None:

        raise HTTPException(
            status_code=404,
            detail="Original document not found."
        )

    return FileResponse(

        path=str(file_path),

        filename=file_path.name
    )


# ============================================================
# PROCESSED IMAGE DOWNLOAD
# ============================================================

@router.get(
    "/{document_id}/download/image"
)
async def download_processed_image(
    document_id: str
):

    processed_dir = (
        OUTPUT_PATH /
        "ocr" /
        document_id /
        "processed"
    )

    if not processed_dir.exists():

        raise HTTPException(
            status_code=404,
            detail="Processed image not found."
        )

    images = list(
        processed_dir.glob("*.png")
    )

    if not images:

        raise HTTPException(
            status_code=404,
            detail="No processed image available."
        )

    image_file = images[0]

    return FileResponse(

        path=str(image_file),

        media_type="image/png",

        filename=(
            f"{document_id}_processed.png"
        )
    )


# ============================================================
# OCR TEXT DOWNLOAD
# ============================================================

@router.get(
    "/{document_id}/download/text"
)
async def download_text(
    document_id: str
):

    ocr_dir = (
        OUTPUT_PATH /
        "ocr" /
        document_id /
        "ocr"
    )

    if not ocr_dir.exists():

        raise HTTPException(
            status_code=404,
            detail="OCR result not found."
        )

    json_files = list(
        ocr_dir.rglob("*.json")
    )


    if not json_files:

        raise HTTPException(
            status_code=404,
            detail="OCR JSON not found."
        )

    output_file = (
        OUTPUT_PATH /
        "ocr" /
        document_id /
        "ocr_text.txt"
    )

    text_parts = []

    for json_file in json_files:

        try:

            with open(
                json_file,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(
                    file
                )

            text_parts.append(
                json.dumps(
                    data,
                    indent=2,
                    ensure_ascii=False
                )
            )

        except Exception as e:

            text_parts.append(
                f"Unable to read {json_file.name}: {e}"
            )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "\n\n".join(text_parts)
        )

    return FileResponse(

        path=str(output_file),

        media_type="text/plain",

        filename=(
            f"{document_id}_ocr.txt"
        )
    )

@router.get(
    "/{document_id}/download/excel"
)
async def download_excel(
    document_id: str
):

    excel_file = (
        OUTPUT_PATH /
        "excel" /
        f"{document_id}_result.xlsx"
    )

    if not excel_file.exists():

        raise HTTPException(
            status_code=404,
            detail="Excel file not found. Process the document first."
        )

    download_name = f"{document_id}_result.xlsx"
    orig_file = find_original_file(document_id)
    if orig_file:
        download_name = f"{orig_file.stem}.xlsx"

    return FileResponse(

        path=str(excel_file),

        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),

        filename=download_name
    )