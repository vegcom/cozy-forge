import logging
import logging.config
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


class PidTagFilter(logging.Filter):
    """
    Ensures 'pid_tag' always exists on the record.
    The _ProcessLogAdapter will overwrite it with a real value when it can.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "pid_tag"):
            record.pid_tag = ""
        return True


def get_logger(name: str | None = None) -> logging.Logger:
    """Get a properly configured logger."""
    if name is None:
        name = "forge"

    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    return logger
