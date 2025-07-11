import logging
from pathlib import Path


class Color:
    black = "\033[30m"
    red = "\033[31m"
    green = "\033[32m"
    orange = "\033[33m"
    blue = "\033[34m"
    purple = "\033[35m"
    cyan = "\033[36m"
    lightgrey = "\033[37m"
    darkgrey = "\033[90m"
    lightred = "\033[91m"
    lightgreen = "\033[92m"
    yellow = "\033[93m"
    lightblue = "\033[94m"
    pink = "\033[95m"
    lightcyan = "\033[96m"
    reset = "\033[0m"
    bold = "\033[01m"
    disable = "\033[02m"
    underline = "\033[04m"
    reverse = "\033[07m"
    strikethrough = "\033[09m"


def setup_logger(logger_name: str, output_folder_path: str = "./logs", file_name: str = "main.log") -> logging.Logger:
    """
    Set up a logger with the given name that writes to the specified file.
    Returns a configured logger instance.
    """
    output_path = Path(output_folder_path)
    output_path.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    log_file = output_path / file_name

    # Check if the logger already has handlers to avoid duplicates
    logger = logging.getLogger(logger_name)

    # Remove existing handlers if any
    if logger.hasHandlers():
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    # Add file handler
    handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)

    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    return logger


def color_log(logger: logging.Logger, value: str, color: Color | None, level: str | None = None):
    # Default to 'info' level if none specified
    if level is None:
        level = "info"

    # Format the message with color
    if color is None:
        message = f"{Color.black} {value} {Color.reset}"
    else:
        message = f"{color} {value} {Color.reset}"

    # Log according to the specified level
    level_lower = level.lower()
    if level_lower == "debug":
        logger.debug(message)
    elif level_lower == "info":
        logger.info(message)
    elif level_lower == "warning" or level_lower == "warn":
        logger.warning(message)
    elif level_lower == "error":
        logger.error(message)
    elif level_lower == "critical":
        logger.critical(message)
    else:
        # Default to info for unknown levels
        logger.info(message)
