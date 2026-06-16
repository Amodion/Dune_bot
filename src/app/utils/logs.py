from __future__ import annotations

import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from app.utils.env_config import Settings


class HealthcheckFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        return "/health" not in message and "/api/v1/health" not in message


def configure_logging(settings: Settings) -> None:
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    if not root_logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(_formatter())
        root_logger.addHandler(console_handler)

    for handler in root_logger.handlers:
        handler.setLevel(level)
        handler.addFilter(HealthcheckFilter())

    if settings.LOG_ENABLE_FILE and not _has_file_handler(root_logger, settings.LOG_FILE):
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        file_handler = TimedRotatingFileHandler(
            logs_dir / settings.LOG_FILE,
            when="midnight",
            backupCount=settings.LOG_BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(_formatter())
        root_logger.addHandler(file_handler)

    for noisy_logger in ("urllib3", "httpx", "httpcore", "multipart", "python_multipart"):
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)


def _formatter() -> logging.Formatter:
    return logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")


def _has_file_handler(logger: logging.Logger, filename: str) -> bool:
    return any(isinstance(handler, TimedRotatingFileHandler) and filename in handler.baseFilename for handler in logger.handlers)

