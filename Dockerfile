FROM python:3.14-slim

WORKDIR /app
ENV PYTHONPATH=/app

COPY requirements.txt pyproject.toml uv.lock ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY data/model/ ./data/model/
COPY .env .

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]