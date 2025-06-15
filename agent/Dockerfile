FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY src/ ./src/
COPY start_web.sh start_api.sh ./

RUN chmod +x start_web.sh start_api.sh

RUN pip install -e .

EXPOSE 8002

CMD ["./start_web.sh"]
