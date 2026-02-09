# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (gcc is good for pandas/scikit build)
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
# Usamos "COPY . ." para copiar todo lo que no esté en .dockerignore
# Es más limpio que copiar uno por uno.
COPY . .

# Expose port
EXPOSE 8000

# Health check
# CAMBIO: Apuntamos a "/" que sí existe en tu main.py, o verificamos que el puerto responda.
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; response = requests.get('http://localhost:8000/'); exit(0) if response.status_code == 200 else exit(1)"

# Run the application
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]