from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles

from routes.upload import router as upload_router
from routes.process import router as process_router
from routes.download import router as download_router


BASE_DIR = Path(__file__).resolve().parent

STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
UPLOADS_DIR = BASE_DIR / "uploads"
OUTPUTS_DIR = BASE_DIR / "outputs"


STATIC_DIR.mkdir(
    parents=True,
    exist_ok=True
)

TEMPLATES_DIR.mkdir(
    parents=True,
    exist_ok=True
)

UPLOADS_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


app = FastAPI(
    title="OmniParse AI — Enterprise Document Intelligence",
    version="1.0.0"
)




app.mount(
    "/static",
    StaticFiles(
        directory=str(STATIC_DIR)
    ),
    name="static"
)


@app.get(
    "/",
    response_class=HTMLResponse
)
async def home():

    index_file = (
        TEMPLATES_DIR /
        "index.html"
    )

    if not index_file.exists():

        return HTMLResponse(
            content="""
            <h1>index.html not found</h1>
            <p>
                Put index.html inside templates/
            </p>
            """,
            status_code=500
        )

    return HTMLResponse(
        content=index_file.read_text(
            encoding="utf-8"
        )
    )


@app.get("/health")
async def health():

    return {
        "application":
            "OmniParse AI",

        "status":
            "running",

        "message":
            "API is working successfully"
    }


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)



app.include_router(
    upload_router
)

app.include_router(
    process_router
)

app.include_router(
    download_router
)