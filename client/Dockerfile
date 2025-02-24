FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./client /app/client

ENV PYTHONUNBUFFERED=1
ENV PYTHONMALLOC=malloc
ENV PYTHONDEVMODE=1
ENV PYTHONGC="aggressive"
ENV PYTHONASYNCIODEBUG=0
ENV PYTHONMEMORY_LIMIT="8G"
ENV PYTHONPATH=/app

CMD ["python", "-X", "dev", "client/app.py"] 