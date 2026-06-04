FROM mcr.microsoft.com/playwright/python:v1.49.1-noble

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy inner project directory (contains app/, templates/, static/)
COPY google-maps-lead-intelligence/ .

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
