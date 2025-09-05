FROM python:3.12-slim

# install docker CLI deps if you plan to run docker-in-docker (optional)
RUN apt-get update && apt-get install -y \
    ca-certificates curl gnupg lsb-release \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "bot.py"]
