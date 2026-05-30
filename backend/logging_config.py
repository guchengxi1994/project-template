import os
import sys

from loguru import logger


def setup_logging() -> None:
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_dir = os.getenv("LOG_DIR", "logs")
    os.makedirs(log_dir, exist_ok=True)

    logger.remove()
    logger.add(
        sys.stdout,
        level=log_level,
        enqueue=True,
        backtrace=False,
        diagnose=False,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | {message}",
    )
    logger.add(
        os.path.join(log_dir, "app.log"),
        level=log_level,
        rotation="10 MB",
        retention="10 days",
        compression="zip",
        enqueue=True,
        backtrace=False,
        diagnose=False,
        encoding="utf-8",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {process.id} | {thread.id} | {name}:{function}:{line} | {message}",
    )


def get_logger():
    return logger

