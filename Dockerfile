FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

CMD ["uvicorn", "server:application", "--host", "0.0.0.0", "--port", "8000"]