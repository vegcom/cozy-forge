# app/lib/core.py
import socket


def get_random_free_port() -> int:
    """Finds and returns a guaranteed available port on the host machine."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]
