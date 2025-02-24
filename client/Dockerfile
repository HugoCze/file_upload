FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./client/app.py ./client/file_gen.py ./

ENV PYTHONUNBUFFERED=1
ENV PYTHONMALLOC=malloc
ENV PYTHONDEVMODE=1
ENV PYTHONGC="aggressive"
ENV PYTHONASYNCIODEBUG=0
ENV PYTHONMEMORY_LIMIT="8G"

CMD ["python", "-X", "dev", "app.py"] 