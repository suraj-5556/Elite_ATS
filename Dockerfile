# AI Job Portal - Production Dockerfile
FROM python:3.11-slim

LABEL maintainer="AI Job Portal"
LABEL description="AI-powered resume matching portal with Flask, ML, and Claude AI"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    FLASK_ENV=production

WORKDIR /app


# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('punkt_tab')"

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p uploads logs experiments ml_models/inference ml_models/training ml_models/datasets

# Pre-train ML model
RUN python -c "from app.services.ml_model import load_or_train_model; load_or_train_model()" || true

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Run application with gunicorn for production
CMD ["python", "app.py"]
