# OmniParse AI — Enterprise Document Intelligence

A FastAPI-based document intelligence application that ingests uploaded documents, runs OCR/vision and AI extraction workflows, stores structured metadata, and exports outputs across multiple formats (`JSON`, `Excel`, `SQL`, and `OCR`).

---

Always learning, building projects, and exploring new technologies in Data Science, Data Analytics, and AI.

---

## Overview

* **Application Entrypoint:** `app_4.py` (`OmniParse AI — Enterprise Document Intelligence`, v1.0.0)
* **Configuration & Workspace Setup:** `config.py` (Pydantic `Settings` + automatic directory creation)
* **Dependencies:** `requirements_4.txt` (FastAPI, Uvicorn, OpenCV, PyMuPDF, PaddleOCR, Google GenAI, SQLAlchemy, Pandas, OpenPyXL)
* **Deployment:** Docker (`Dockerfile` on `python:3.10-slim`) and process configuration (`uvicorn` on `$PORT`)

## Project Structure

```text
├── app_4.py                 # FastAPI app, routes (/, /health, /favicon.ico), static/template mounting, routers
├── config.py                # Pydantic Settings and workspace directory initialization
├── requirements_4.txt       # Python package dependencies
├── Dockerfile               # Container build and Uvicorn runtime definition
├── .gitignore               # Ignored build artifacts, virtualenvs, local DB, and temp/output files
├── routes/
│   ├── upload.py            # Upload endpoint router
│   ├── process.py           # Document processing / OCR / extraction router
│   └── download.py          # Output export / download router
├── templates/
│   └── index.html           # Frontend HTML served at /
├── static/                  # Static assets mounted at /static
├── uploads/
│   ├── original/            # Uploaded source files
│   └── pages/               # Rendered document pages
├── outputs/
│   ├── json/                # JSON export artifacts
│   ├── excel/               # Excel (.xlsx) export artifacts
│   ├── sql/                 # SQL export artifacts
│   └── ocr/                 # OCR text/data artifacts
└── temp/                    # Temporary processing files
```

## Configuration (`config.py`)

Settings are loaded via `pydantic-settings` (with `.env` support):

| Variable | Default | Description |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | `""` | API key for Google GenAI (`google-genai`) integration |
| `DATABASE_URL` | `"sqlite:///./documents.db"` | Database connection string |
| `UPLOAD_DIR` | `"uploads"` | Base directory for uploaded files (`original/`, `pages/`) |
| `OUTPUT_DIR` | `"outputs"` | Base directory for generated exports (`json/`, `excel/`, `sql/`, `ocr/`) |
| `TEMP_DIR` | `"temp"` | Directory for temporary working files |
| `MAX_FILE_SIZE_MB` | `25` | Maximum allowed upload file size in megabytes |

> **Security Note:** Never commit real API keys or `.env` files with live secrets to version control. Rotate any exposed keys and keep secrets in environment variables or a local `.env` ignored by `.gitignore`.

## Getting Started (Local Setup)

### 1. Create a Virtual Environment & Install Dependencies

```bash
python -m venv .venv
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

pip install --upgrade pip setuptools wheel
pip install -r requirements_4.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=sqlite:///./documents.db
UPLOAD_DIR=uploads
OUTPUT_DIR=outputs
TEMP_DIR=temp
MAX_FILE_SIZE_MB=25
```

### 3. Run the FastAPI Server

Start Uvicorn for local development:

```bash
uvicorn app_4:app --reload --host 0.0.0.0 --port 8000
```

* Web UI: `http://localhost:8000/`
* Health check: `http://localhost:8000/health`

## Running with Docker

Build and run the container using the provided `Dockerfile` setup (note: update the module name in `CMD` to `app_4:app` if your entrypoint file is named `app_4.py`):

```bash
docker build -t omniparse-ai .
docker run -d -p 8080:8080 --env-file .env omniparse-ai
```

## Notes & Deployment Details

* **Entrypoint Module Name:** `app_4.py` defines the `app` FastAPI instance, while the sample `Dockerfile` and `Procfile` command reference `app:app`. Ensure your start command matches your actual filename (`app_4:app` or `app:app`).
* **System Libraries for Vision & OCR:** Running OpenCV, PyMuPDF, and PaddleOCR on slim Debian containers requires system libraries such as `build-essential`, `libgl1`, `libglib2.0-0`, `libgomp1`, and `curl`.

---

## 🌐 Socials:

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com)
[![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:your-email@example.com)

## 💻 Tech Stack:

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)

## 📊 GitHub Stats:

![GitHub Stats](https://github-readme-stats.vercel.app/api?username=your-github-username&show_icons=true&theme=default)

## Author

**Rushikesh Machindra Pawar** — MCA Department, Deogiri College, Chhatrapati Sambhajinagar
