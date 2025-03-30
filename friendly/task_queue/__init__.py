import logging
import sys

import firebase  # noqa
import mail  # noqa
from celery.signals import setup_logging
from loguru import logger

from .celery_settings import celery


class InterceptHandler(logging.Handler):
    """Перехватывает стандартный celery.log и преобразует в формат понятный logguru"""

    def emit(self, record: logging.LogRecord) -> None:
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        mapper = {10: "DEBUG", 20: "INFO", 30: "WARNING", 40: "ERROR", 50: "CRITICAL"}
        logger_opt.log(mapper.get(record.levelno), record.getMessage())


@setup_logging.connect
def setup_logging(*args, **kwargs) -> None:
    """Заменить стандартный логгер на кастомный при запуске Celery"""
    logger.remove()
    logger.add(sys.stdout, level="DEBUG")
    logger.add(
        "../logs/celery.log", level="INFO", rotation="2 MB", compression="zip", encoding="UTF-8"
    )

    logging.basicConfig(handlers=[InterceptHandler()], level="INFO")
