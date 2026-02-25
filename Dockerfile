# ── Stage 1: Build ────────────────────────────────────────────
FROM python:3.11-slim AS base

# Install system dependencies for PyMuPDF, python-docx
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ── Install Python dependencies ────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('wordnet')"

# Download spaCy model
RUN python -m spacy download en_core_web_sm || echo "spaCy model download failed (non-critical)"

# ── Copy Application ───────────────────────────────────────────
COPY . .

# Create upload directory
RUN mkdir -p app/static/uploads ml_models/inference mlruns

# ── Train ML model at build time ───────────────────────────────
# This ensures the model exists in the container. In production,
# mount a pre-trained model volume instead.
RUN python -m ml_models.training.train_model || echo "Model training skipped (MongoDB not available at build)"

# ── Non-root user for security ─────────────────────────────────
RUN useradd --create-home --shell /bin/bash appuser
RUN chown -R appuser:appuser /app
USER appuser

# ── Expose and run ─────────────────────────────────────────────
EXPOSE 5000

# Use gunicorn for production; 4 workers for concurrency
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "4", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "run:app"]
