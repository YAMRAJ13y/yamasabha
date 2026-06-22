FROM python:3.12-slim

# git is needed to install the 7 engine packages (git+https deps).
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir .

ENV YAMASABHA_HOST=0.0.0.0
EXPOSE 8000
CMD ["sh", "-c", "uvicorn yamasabha.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
