import logging
from pathlib import Path
from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme


def setup_logging(log_file: Path = Path(".log"), console_level=logging.INFO):
    """
    Set up a centralized logging system.

    :param log_file: Log file path
    :param console_level: Logging level for console output
    """
    # Rich console configuration
    console = Console(theme=Theme({"logging.level": "bold"}))

    # Log format configuration
    log_format = "%(message)s"
    date_format = "[%X]"

    # Rich handler configuration
    rich_handler = RichHandler(
        console=console,
        enable_link_path=False,
        markup=True,
        rich_tracebacks=True,
        tracebacks_show_locals=True,
        level=console_level,  # Set console logging level
    )

    # File handler configuration
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    file_handler.setLevel(logging.DEBUG)  # Keep all logs in the file

    # Root logger configuration
    logging.basicConfig(
        level=logging.DEBUG,  # Keep root logger at DEBUG to capture all logs
        format=log_format,
        datefmt=date_format,
        handlers=[rich_handler, file_handler],
    )


def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger with the specified name.

    :param name: Logger name
    :return: Logger instance set up
    """
    return logging.getLogger(name)
