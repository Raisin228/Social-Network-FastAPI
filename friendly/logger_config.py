import sys
import traceback
from typing import List

from loguru import logger

logger.remove()

logger.add(sys.stdout, level="DEBUG", filter=lambda record: record["level"].name == "DEBUG")
logger.add(
    "../logs/friendly_app.log", level="INFO", rotation="2 MB", compression="zip", encoding="UTF-8"
)

log = logger


def filter_traceback(exc: Exception) -> List[str]:
    """Оставляем только то, что находится в нашем коде"""
    tb = traceback.format_exception(exc.__class__, exc, exc.__traceback__)

    filtered_tb = []
    for line in tb:
        if "site-packages" not in line:
            filtered_tb.append(line)
    return filtered_tb


# TODO сделать хранение логов в elasticsearch (на будущее)
