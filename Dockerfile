FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

WORKDIR /app

# Install required system packages for OpenCV, PyMuPDF, and PaddleOCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -U pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Create all required workspace directories
RUN mkdir -p uploads/original uploads/pages outputs/json outputs/excel outputs/sql outputs/ocr temp

EXPOSE 8080

# Start FastAPI server binding to Railway dynamic $PORT
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8080}"]
