FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create logs directory
RUN mkdir -p /app/logs

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x Main.py

# Create a non-root user for security
RUN useradd -m -u 1000 userbot && chown -R userbot:userbot /app
USER userbot

CMD ["python", "Main.py"]