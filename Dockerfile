FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml uv.lock* ./
COPY main.py schemas.py database.py storage.py errors.py dashboard.py dashboard.html worker.py ./

RUN pip install --no-cache-dir fastapi "uvicorn[standard]" sqlalchemy pydantic-settings "psycopg[binary]"

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
