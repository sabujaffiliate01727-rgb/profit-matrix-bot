# Profit Matrix bot — runs anywhere (Koyeb, Railway, Fly, a VPS...)
FROM python:3.12-slim

WORKDIR /app

# Install deps first (better build caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Long-polling worker — no web port needed
CMD ["python", "bot.py"]
