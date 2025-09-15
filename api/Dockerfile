FROM python:3.12-slim AS api

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# (optional but recommended)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# If you have a requirements file, copy & install first to leverage caching
COPY api/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your FastAPI source
COPY api/ ./

EXPOSE 8000

# If your entrypoint file is main.py and the FastAPI instance is `app`
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]