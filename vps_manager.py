# vps_manager.py
import os
import uuid
import shlex
import subprocess
import time

STORE = {}  # vps_id -> info

# Requires tmate installed in the system / container
# The tmate process will create a socket at /tmp/tmate-<id>.sock
# We create a new detached session and read the tmate_ssh display

def _run(cmd, timeout=10):
    """Run shell command and return stdout (raises on failure)."""
    proc = subprocess.run(cmd, capture_output=True, text=True, shell=False, timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd} -> {proc.stderr.strip()}")
    return proc.stdout.strip()

def create_vps(owner_id: str, os_image: str, ram: str, disk: str):
    """
    Create a tmate session. Returns info:
    {
      id, ssh_command, host, user, port, backend
    }
    """
    vps_id = uuid.uuid4().hex[:8]
    sock = f"/tmp/tmate-{vps_id}.sock"
    # Start a new detached tmate session using the socket
    # 'tmate -S socket new-session -d'
    try:
        _run(["tmate", "-S", sock, "new-session", "-d"])
    except Exception as e:
        # maybe socket exists, try kill-server then new-session
        try:
            _run(["tmate", "-S", sock, "kill-server"])
        except Exception:
            pass
        _run(["tmate", "-S", sock, "new-session", "-d"])

    # wait for tmate to be ready (tmate-ready)
    start = time.time()
    ready = False
    while time.time() - start < 8:
        try:
            _run(["tmate", "-S", sock, "wait", "tmate-ready"], timeout=3)
            ready = True
            break
        except Exception:
            time.sleep(0.5)
    if not ready:
        raise RuntimeError("tmate session didn't become ready in time")

    # get ssh string and web, prefer ssh
    ssh_cmd = _run(["tmate", "-S", sock, "display", "-p", "#{tmate_ssh}"])
    web_cmd = ""
    try:
        web_cmd = _run(["tmate", "-S", sock, "display", "-p", "#{tmate_web}"])
    except Exception:
        pass

    # ssh_cmd looks like: 'ssh <user>@<host>'
    # parse host and user
    parts = ssh_cmd.strip().split()
    user_host = parts[-1] if parts else ""
    if "@" in user_host:
        user, host = user_host.split("@", 1)
    else:
        user, host = user_host, ""
    info = {
        "id": vps_id,
        "ssh_command": ssh_cmd,
        "web_command": web_cmd,
        "host": host,
        "user": user,
        "port": 22,
        "backend": "tmate",
        "sock": sock
    }
    STORE[vps_id] = info
    return info

def delete_vps(vps_id: str):
    info = STORE.get(vps_id)
    if not info:
        return False
    sock = info.get("sock")
    try:
        # try kill server for that socket
        subprocess.run(["tmate", "-S", sock, "kill-server"], timeout=5)
    except Exception:
        pass
    try:
        if os.path.exists(sock):
            os.remove(sock)
    except Exception:
        pass
    STORE.pop(vps_id, None)
    return True

def list_vps():
    return list(STORE.keys())

def get_vps_info(vps_id: str):
    return STORE.get(vps_id)
