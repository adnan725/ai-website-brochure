# ── Stage 1: build ──────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# Install dependencies in isolation so they can be copied cleanly
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --prefix=/install --no-cache-dir -r requirements.txt


# ── Stage 2: runtime ─────────────────────────────────────────────────────────
FROM python:3.12-slim

# Security: run as non-root
RUN useradd --create-home appuser
WORKDIR /home/appuser/app
USER appuser

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY --chown=appuser:appuser . .

# Gunicorn is the production WSGI server
RUN pip install --no-cache-dir gunicorn

EXPOSE 8000

# ⬇ Change "app:app" if your Flask instance lives elsewhere
#   format → <module_filename>:<flask_variable_name>
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "app:app"]