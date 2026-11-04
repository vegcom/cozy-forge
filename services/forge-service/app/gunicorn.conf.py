import json
import multiprocessing
import os

bind = "0.0.0.0:8000"

workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"

keepalive = 5
timeout = 120
graceful_timeout = 30

loglevel = "info"

current_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(current_dir, "lib", "log_config.json")

try:
    with open(json_path, "r", encoding="utf-8") as f:
        config_data = json.load(f)
        if "main_log" in config_data:
            config_data["loggers"] = config_data.pop("main_log")
        logconfig_dict = config_data
except Exception as e:
    print(f"🚨 Failed to automatically load cozy log config: {e}")
