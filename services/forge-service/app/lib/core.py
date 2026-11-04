# app/lib/core.py
import json
import logging
import logging.config
import os
import socket


def get_logger():
    """Provides a logging integration."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "log_config.json")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            log_conf = json.load(f)
        logging.config.dictConfig(log_conf)
    except Exception as e:
        logging.basicConfig(level=logging.INFO)
        logging.getLogger(__name__).error(
            f"Failed to load log config from {config_path}: {e}"
        )

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
