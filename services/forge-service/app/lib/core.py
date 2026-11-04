# app/lib/core.py
import logging
import logging.config
import socket


def get_logger():
    """Provides a logging integration."""
    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.handlers = []
        uvicorn_logger.propagate = True

    return logging.getLogger("forge.core")


def get_random_free_port() -> int:
    """Finds and returns a guaranteed available port on the host machine."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]
