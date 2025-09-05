FROM python:3.12-slim

# install tmate + dependencies
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    tmate \
    openssh-client \
    ca-certificates \
    git \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# copy files
COPY . .

# install python deps
RUN pip install --no-cache-dir -r requirements.txt

# ensure /tmp is writable (it is)
# Run bot
CMD ["python3", "bot.py"]
