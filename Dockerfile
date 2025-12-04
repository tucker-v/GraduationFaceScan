# ---------- STAGE 1: Build Svelte frontend ----------
FROM node:22 AS frontend-builder

# Set working directory
WORKDIR /frontend

# Copy frontend code
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

COPY frontend/ .

# Build Svelte into /frontend/build
RUN npm run build


# ---------- STAGE 2: Build FastAPI backend ----------
FROM python:3.11-slim AS backend

# System deps
RUN apt-get update && apt-get install -y build-essential && apt-get clean

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy FastAPI app
COPY app/ ./app

# Copy built frontend from stage 1
COPY --from=frontend-builder /frontend/dist ./frontend/dist

# Run DB setup
COPY scripts/createDB.py ./scripts/
COPY scripts/main.py ./scripts/
COPY scripts/embeddings.pkl ./scripts/

# Environment variables
ENV PYTHONUNBUFFERED=1

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]