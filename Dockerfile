# =============================================================================
# STAGE 1: Base Image
# =============================================================================
FROM python:3.13-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    gettext \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*


# =============================================================================
# STAGE 2: Development
# =============================================================================
FROM base AS development

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


# =============================================================================
# STAGE 3: Staging
# =============================================================================
FROM base AS staging

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]


# =============================================================================
# STAGE 4: Production
# =============================================================================
FROM base AS production

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Collect static files
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--worker-class", "sync", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "100", \
     "--timeout", "60", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
