FROM python:3.10-slim

WORKDIR /app

# Install system dependencies and ensure pip is available
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

# Install Python dependencies in smaller batches to avoid memory issues
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    --no-deps \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PORT=8000
ENV HOST=0.0.0.0

# Expose the port
EXPOSE 8000

# Start the application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]