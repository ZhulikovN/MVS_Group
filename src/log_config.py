import logging
import sys
from types import TracebackType
from typing import Optional, Type

from src.settings import settings


def setup_logging() -> None:
    logger = logging.getLogger()

    log_level = settings.log_level
    logger.setLevel(log_level)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(formatter)

    file_handler = logging.FileHandler("app.log")
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    if logger.hasHandlers():
        logger.handlers.clear()

    logger.addHandler(stdout_handler)
    logger.addHandler(file_handler)

    logging.debug(f"Логирование настроено. Уровень: {log_level}")


def handle_exception(
    exc_type: Type[BaseException], exc_value: BaseException, exc_traceback: Optional[TracebackType]
) -> None:
    if issubclass(exc_type, KeyboardInterrupt):
        sys.exit(1)
    logging.critical("Необработанное исключение", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception
setup_logging()
