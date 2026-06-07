FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .

# 80番ポートで起動
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]