FROM python:3.11-slim

WORKDIR /app

LABEL name="Adnan Khan"
LABEL email="adnankhaan4488@gmail.com"
LABEL description="TriageFlow Industrial Maintenance AI — Backend API"

# Install dependencies first (separate layer so Docker caches this
# step and doesn't reinstall packages on every code change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "uvicorn", "backend.api.main:app", \
     "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]