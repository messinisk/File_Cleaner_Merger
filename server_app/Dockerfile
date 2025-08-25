FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY pyproject.toml .
COPY server_app/ ./server_app
COPY pure_core/ ./pure_core

RUN pip install --no-cache-dir .[server]

# Expose FastAPI port
EXPOSE 8000

# Start the server
CMD ["uvicorn", "server_app.app:app", "--host", "0.0.0.0", "--port", "8000"]
