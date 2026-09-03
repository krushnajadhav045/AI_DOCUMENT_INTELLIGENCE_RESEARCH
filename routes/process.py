from fastapi import APIRouter, HTTPException
from services.pipeline import process_document

router = APIRouter(
    prefix="/api/documents",
    tags=["Processing"]
)


@router.post("/{document_id}/process")
@router.post("/process/{document_id}")
async def process(document_id: str):


    try:

        result = await process_document(
            document_id
        )

        return {
            "success": True,
            "status": "completed",
            "document_id": document_id,
            "result": result
        }

    except FileNotFoundError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        print("PROCESSING ERROR:", e)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )