# CityScope Konya - Docker Image
# ================================

FROM python:3.11-slim

# Labels
LABEL maintainer="tugrulkaya"
LABEL description="CityScope Konya - Urban Simulation Platform"
LABEL version="1.0.0"

# Environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=backend/server.py
ENV FLASK_ENV=production

# Working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Generate sample data if not exists
RUN python data/generate_sample_data.py || true

# Expose port
EXPOSE 5555

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5555/ || exit 1

# Run server
CMD ["python", "backend/server.py"]
