FROM python:3.12-slim

WORKDIR /app

COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

COPY code/ ./code/

RUN mkdir -p /app/data

WORKDIR /app/code/backend

EXPOSE 8080

CMD ["sh", "-c", "python seed.py && exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]