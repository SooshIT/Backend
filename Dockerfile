FROM python:3.10-slim AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    python3-pip \
    python3-dev \
    libpq-dev \
    ffmpeg \
    libsndfile1 \
    pkg-config \
    libmagic1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install build tools
RUN python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements files
COPY requirements-production.txt ./

# Install production dependencies (no TTS - using OpenAI instead)
RUN pip install --no-cache-dir -r requirements-production.txt

# Copy application code and verify installation
COPY . .
RUN python -c "import fastapi; import uvicorn; import sqlalchemy; print('Dependencies verified successfully!')"

# Set environment variables
ENV PORT=8000
ENV HOST=0.0.0.0

# Expose the port
EXPOSE 8000

# Start the application (use shell form to expand $PORT)
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}