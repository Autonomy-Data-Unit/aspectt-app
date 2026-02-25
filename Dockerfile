# Stage 1: Build SvelteKit frontend
FROM node:20-slim AS frontend-build
WORKDIR /app/frontend
COPY aspectt-frontend/package*.json ./
RUN npm ci
COPY aspectt-frontend/ ./
RUN npm run build

# Stage 2: Python runtime
FROM python:3.12-slim
WORKDIR /app

# Install Python dependencies
COPY aspectt-backend/pyproject.toml ./
RUN pip install --no-cache-dir fastapi uvicorn[standard]

# Copy backend code
COPY aspectt-backend/main.py ./main.py

# Copy data files
COPY aspectt-pipeline/data/uk_onet/ ./data/uk_onet/

# Copy built frontend
COPY --from=frontend-build /app/frontend/build ./static/

# Set environment
ENV ASPECTT_DATA_DIR=/app/data/uk_onet
ENV ASPECTT_STATIC_DIR=/app/static

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
