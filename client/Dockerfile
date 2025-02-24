FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY client/app.py client/file_gen.py ./

EXPOSE 5000

CMD ["python", "app.py"] 