import sys

from loguru import logger

logger.remove()

logger.add(sys.stdout, level="DEBUG")
logger.add("../logs/friendly_app.log", level="DEBUG", rotation="2 MB", compression="zip", encoding="UTF-8")

log = logger

# TODO сделать хранение логов в elasticsearch
