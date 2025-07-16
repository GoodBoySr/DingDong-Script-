=========================

🚀 Dockerfile for Bypass Bot

=========================

FROM python:3.11-slim

Install dependencies

RUN apt-get update && apt-get install -y 
wget 
curl 
gnupg 
unzip 
fonts-liberation 
libnss3 
libatk-bridge2.0-0 
libgtk-3-0 
libxss1 
libasound2 
libgbm1 
libu2f-udev 
libxshmfence1 
libxrandr2 
xvfb 
--no-install-recommends 
&& rm -rf /var/lib/apt/lists/*

=========================

Install Chrome (for uChrome)

=========================

RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-linux-keyring.gpg 
&& echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list 
&& apt-get update 
&& apt-get install -y google-chrome-stable 
&& rm -rf /var/lib/apt/lists/*

=========================

Set up working dir and Python deps

=========================

WORKDIR /app COPY requirements.txt ./ RUN pip install --no-cache-dir -r requirements.txt

Copy project files

COPY . .

=========================

ENV vars to help uChrome

=========================

ENV GOOGLE_CHROME_BIN="/usr/bin/google-chrome" 
ENV CHROME_BIN="/usr/bin/google-chrome"

Optional: Expose port if needed

EXPOSE 7860

Entry point

CMD ["python", "main.py"]

