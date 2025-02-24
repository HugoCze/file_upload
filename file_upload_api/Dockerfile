FROM python:3.8-slim

WORKDIR /app

COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./file_upload_api/main.py .

ENV PYTHONPATH=/app
WORKDIR /app
COPY . .

EXPOSE 8000

CMD ["python", "main.py"] 