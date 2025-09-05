# vps_manager.py
import os
import uuid
import random
import string
import time

try:
    import docker
except Exception:
    docker = None

STORE = {}  # id -> info
SSH_BASE_PORT = int(os.getenv("SSH_BASE_PORT", "22000"))
CREDITS = os.getenv("CREDITS", "Vasplayz90")


def _rand_pass(n=12):
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(n))


def _host_port():
    # choose random offset to avoid collision
    return SSH_BASE_PORT + random.randint(1, 2000)


def _ensure_client():
    if docker is None:
        raise RuntimeError("docker SDK is not installed")
    client = docker.from_env()
    return client


def create_vps(owner_id: str, image: str, ram: str, cpus: int, disk_label: str):
    """
    Create a Docker container as VPS.
    - image: docker image name (must provide sshd or the code will try to set up sshd).
    - ram: string like '2048m' or None
    - cpus: integer number of cores
    Returns info dict with id, username, passwords, host, port, direct_conn, ssh_command.
    """
    client = _ensure_client()
    vid = uuid.uuid4().hex[:8]
    host_port = _host_port()
    user = "root"
    root_password = _rand_pass(10)
    user_password = _rand_pass(10)

    # prepare container run args
    run_kwargs = {
        "image": image,
        "detach": True,
        "tty": True,
        "name": f"vps_{vid}",
        "labels": {"vps_id": vid, "owner": owner_id, "credits": CREDITS},
        "ports": {"22/tcp": host_port},
    }
    if ram:
        try:
            # mem_limit takes strings like '512m' or '1g'
            run_kwargs["mem_limit"] = ram
        except Exception:
            pass
    if cpus and cpus > 0:
        try:
            run_kwargs["nano_cpus"] = int(cpus * 1e9)
        except Exception:
            pass

    # pull image (best-effort)
    try:
        client.images.pull(image)
    except Exception:
        # continue; maybe image is local or pull fails
        pass

    # run container
    container = client.containers.run(**run_kwargs)

    # best-effort: set root password inside container
    try:
        # try chpasswd
        cmd = f"bash -lc \"echo root:{root_password} | chpasswd || true\""
        exec_id = client.api.exec_create(container.id, cmd)
        client.api.exec_start(exec_id)
    except Exception:
        pass

    # try to create a regular user with password
    try:
        cmd = f"bash -lc \"useradd -m -s /bin/bash user || true && echo user:{user_password} | chpasswd || true\""
        exec_id = client.api.exec_create(container.id, cmd)
        client.api.exec_start(exec_id)
    except Exception:
        pass

    # try to ensure sshd is running (many ssh-enabled images already run it)
    try:
        # attempt to start sshd if available
        exec_id = client.api.exec_create(container.id, cmd="bash -lc 'service ssh start || /etc/init.d/ssh start || true'")
        client.api.exec_start(exec_id)
    except Exception:
        pass

    info = {
        "id": vid,
        "container_id": container.id,
        "image": image,
        "username": "user",
        "user_password": user_password,
        "root_password": root_password,
        "host": os.getenv("HOST_IP", "127.0.0.1"),
        "port": host_port,
        "direct_conn": f"{os.getenv('HOST_IP','127.0.0.1')}:{host_port}",
        "ssh_command": f"ssh user@{os.getenv('HOST_IP','127.0.0.1')} -p {host_port}",
        "status": "running",
    }
    STORE[vid] = info
    return info


def delete_vps(vid: str):
    client = _ensure_client()
    info = STORE.get(vid)
    if not info:
        return False
    cid = info.get("container_id")
    try:
        c = client.containers.get(cid)
        c.stop(timeout=5)
        c.remove()
    except Exception:
        pass
    STORE.pop(vid, None)
    return True


def list_vps():
    return list(STORE.keys())


def get_vps_info(vid: str):
    return STORE.get(vid)


def start_vps(vid: str):
    client = _ensure_client()
    info = STORE.get(vid)
    if not info:
        return False
    try:
        c = client.containers.get(info["container_id"])
        c.start()
        info["status"] = "running"
        return True
    except Exception:
        return False


def stop_vps(vid: str):
    client = _ensure_client()
    info = STORE.get(vid)
    if not info:
        return False
    try:
        c = client.containers.get(info["container_id"])
        c.stop()
        info["status"] = "stopped"
        return True
    except Exception:
        return False


def restart_vps(vid: str):
    client = _ensure_client()
    info = STORE.get(vid)
    if not info:
        return False
    try:
        c = client.containers.get(info["container_id"])
        c.restart()
        info["status"] = "running"
        return True
    except Exception:
        return False


def reinstall_vps(vid: str, image: str):
    """
    Reinstall: remove container and create new container under same vps id (best-effort).
    Returns new info.
    """
    client = _ensure_client()
    info = STORE.get(vid)
    if not info:
        raise RuntimeError("VPS not found")
    # remove old container
    try:
        c = client.containers.get(info["container_id"])
        c.stop()
        c.remove()
    except Exception:
        pass
    # create new container but keep same vps id
    host_port = _host_port()
    root_password = _rand_pass(10)
    user_password = _rand_pass(10)
    run_kwargs = {
        "image": image,
        "detach": True,
        "tty": True,
        "name": f"vps_{vid}",
        "labels": {"vps_id": vid, "credits": CREDITS},
        "ports": {"22/tcp": host_port},
    }
    try:
        client.images.pull(image)
    except Exception:
        pass
    container = client.containers.run(**run_kwargs)
    try:
        cmd1 = f"bash -lc \"echo root:{root_password} | chpasswd || true\""
        exec_id = client.api.exec_create(container.id, cmd1)
        client.api.exec_start(exec_id)
    except Exception:
        pass
    try:
        cmd2 = f"bash -lc \"useradd -m -s /bin/bash user || true && echo user:{user_password} | chpasswd || true\""
        exec_id2 = client.api.exec_create(container.id, cmd2)
        client.api.exec_start(exec_id2)
    except Exception:
        pass
    try:
        client.api.exec_create(container.id, cmd="bash -lc 'service ssh start || /etc/init.d/ssh start || true'")
    except Exception:
        pass

    new_info = {
        "id": vid,
        "container_id": container.id,
        "image": image,
        "username": "user",
        "user_password": user_password,
        "root_password": root_password,
        "host": os.getenv("HOST_IP", "127.0.0.1"),
        "port": host_port,
        "direct_conn": f"{os.getenv('HOST_IP','127.0.0.1')}:{host_port}",
        "ssh_command": f"ssh user@{os.getenv('HOST_IP','127.0.0.1')} -p {host_port}",
        "status": "running",
    }
    STORE[vid] = new_info
    return new_info
