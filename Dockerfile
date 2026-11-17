# =============================================================================
# Stage 1: Build the React 19 Frontend Dashboard
# =============================================================================
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# =============================================================================
# Stage 2: Production Python API & Unified Server
# =============================================================================
FROM python:3.12-slim AS runner
WORKDIR /app

# Install minimal OS dependencies for compiled libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend & engine source code
COPY backend ./backend
COPY major ./major
COPY crypto_pipeline ./crypto_pipeline
COPY multi_backend ./multi_backend
COPY enhanced_dataset ./enhanced_dataset
COPY profiler ./profiler
COPY models ./models
COPY docs ./docs

# Copy built frontend assets into frontend/dist
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose production port
EXPOSE 8000

ENV PYTHONUNBUFFERED=1

# Run Uvicorn serving both REST API endpoints (/api/...) and React Frontend (/)
CMD ["uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
