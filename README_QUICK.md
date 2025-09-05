# Quick run (Docker)

1) Copy files into a folder.
2) Create .env with real token & owner ID (see .env.example).
3) Build & run:

docker build -t discord-tmate-bot .
docker rm -f discord-tmate-bot || true
docker run -d --name discord-tmate-bot --env-file .env discord-tmate-bot

# Use:
- In Discord server, type /deploy os_image ram_gb disk_gb
  Example: /deploy ubuntu 512 1
- The bot will DM you a tmate "ssh ..." command (or web link).
- Paste the ssh command into PuTTY (host will be the tmate host; user provided).
- To remove the session: /deletevps <id>

Notes:
- tmate sessions are temporary and will end when session terminated.
- For permanent SSH access, use docker backend with SSH-enabled image (not included here).
- The bot sets presence to "Watching ArizNodes Cloud BY vASPLAYZ90" and DM messages include that credit text.
