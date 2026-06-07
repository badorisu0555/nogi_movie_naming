FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt .
RUN python3.11 -m pip install -r requirements.txt

COPY . .
CMD ["uvicorn","app.api.main:app", "--host","0.0.0.0","--port","80"]
