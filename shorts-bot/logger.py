"""
logger.py — Colored logging utility using colorlog.
"""

import logging
import sys
import colorlog


def get_logger(name: str = "shorts-bot", level: int = logging.DEBUG) -> logging.Logger:
    """
    Return a logger with coloured console output.

    Colours:
        DEBUG    → cyan
        INFO     → green
        WARNING  → yellow
        ERROR    → red
        CRITICAL → bold red
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers when called multiple times
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # 1. Console Handler (Colored)
    console_handler = colorlog.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(
        colorlog.ColoredFormatter(
            fmt="%(log_color)s%(asctime)s [%(levelname)-8s]%(reset)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG":    "cyan",
                "INFO":     "green",
                "WARNING":  "yellow",
                "ERROR":    "red",
                "CRITICAL": "bold_red",
            },
        )
    )
    logger.addHandler(console_handler)

    # 2. File Handler (Persistent)
    file_handler = logging.FileHandler("latest.log", mode="w", encoding="utf-8")
    file_handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s [%(levelname)-8s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(file_handler)

    return logger


# Module-level convenience instance
log = get_logger()
