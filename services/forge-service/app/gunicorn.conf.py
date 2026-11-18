import json
import logging
import os

bind = "0.0.0.0:8000"

workers = 1
worker_class = "uvicorn.workers.UvicornWorker"

keepalive = 5
timeout = 120
graceful_timeout = 30

loglevel = "info"

current_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(current_dir, "lib", "log_config.json")


class PidTagFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, "pid_tag"):
            record.pid_tag = ""
        return True


try:
    with open(json_path, "r", encoding="utf-8") as f:
        config_data = json.load(f)
    logconfig_dict = config_data
    for logger_name in ("", "forge", "health_check"):
        logger = logging.getLogger(logger_name)
        for handler in logger.handlers:
            fmt = getattr(handler.formatter, "_fmt", "") or ""
            if "pid_tag" in fmt:
                handler.addFilter(PidTagFilter())
except Exception as e:
    print(f"🚨 Failed to load log config: {e}")
    logconfig_dict = None


def post_fork(server, worker):
    # This runs after the worker process is forked
    for logger_name in ("", "forge", "health_check"):
        logger = logging.getLogger(logger_name)
        for handler in logger.handlers:
            if isinstance(handler.formatter, logging.Formatter):
                fmt = getattr(handler.formatter, "_fmt", "")
                if "pid_tag" in str(fmt):
                    handler.addFilter(PidTagFilter())
