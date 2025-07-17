FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV GOOGLE_CHROME_BIN=/usr/bin/google-chrome
ENV CHROME_BIN=/usr/bin/google-chrome
WORKDIR /app

COPY . .

RUN apt update && apt install -y \
    wget curl unzip gnupg ca-certificates chromium \
    libnss3 libxss1 libasound2 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libdbus-1-3 libgdk-pixbuf2.0-0 libnspr4 libx11-xcb1 libxcomposite1 \
    libxdamage1 libxrandr2 libgbm1 libgtk-3-0 fonts-liberation xdg-utils \
    --no-install-recommends && \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb && \
    apt clean && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir \
    discord.py==2.3.2 \
    undetected-chromedriver==3.5.5 \
    selenium==4.15.2 \
    openai==1.16.2 \
    python-dotenv

CMD ["python", "main.py"]
