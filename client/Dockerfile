FROM python:3.9-slim

WORKDIR /app

COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY client/app.py client/file_gen.py ./

# Improve memory management settings
ENV PYTHONUNBUFFERED=1
ENV PYTHONMALLOC=malloc
ENV PYTHONDEVMODE=1
# Add memory management settings
ENV PYTHONGC="aggressive"
ENV PYTHONASYNCIODEBUG=0
# Limit max memory usage for Python
ENV PYTHONMEMORY_LIMIT="8G"

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import os, sys; sys.exit(0 if os.path.exists('/app') else 1)"

CMD ["python", "-X", "dev", "app.py"] 