"""
Logging configuration for the Nominal project.
Provides colored logging for all components (reader, processor, orchestrator).
"""

import inspect
import logging
import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
# Look for .env in project root (parent of src directory)
project_root = Path(__file__).parent.parent.parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output."""

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
        "BOLD": "\033[1m",  # Bold
    }

    def format(self, record):
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[levelname]}{self.COLORS['BOLD']}{levelname:8s}{self.COLORS['RESET']}"
            )

        # Format the message
        message = super().format(record)

        return message


def _get_log_level() -> int:
    """
    Get the log level from environment variable.

    Returns:
        Logging level (defaults to INFO if not set or invalid)
    """
    level_str = os.getenv("NOMINAL_LOG_LEVEL", "INFO").upper()
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    return level_map.get(level_str, logging.INFO)


def setup_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Setup a logger with colored output.

    Log level is determined from the NOMINAL_LOG_LEVEL environment variable
    (defaults to INFO if not set).

    Args:
        name: Logger name (e.g., 'nominal.processor', 'nominal.reader').
              If None, automatically detects the calling module's fully qualified name.

    Returns:
        Configured logger
    """
    # Auto-detect module name if not provided
    if name is None:
        # Get the calling frame (skip this function and any intermediate helpers)
        frame = inspect.currentframe()
        try:
            # Go up the stack to find the caller
            caller_frame = frame.f_back
            if caller_frame is not None:
                module = inspect.getmodule(caller_frame)
                if module is not None and module.__name__ != "__main__":
                    name = module.__name__
                else:
                    # Fallback to filename-based name
                    filename = caller_frame.f_globals.get("__file__", "")
                    if filename:
                        # Convert file path to module-like name
                        filename = os.path.splitext(os.path.basename(filename))[0]
                        name = f"nominal.{filename}"
                    else:
                        name = "nominal"
            else:
                name = "nominal"
        finally:
            del frame

    logger = logging.getLogger(name)

    # Only add handler if none exists
    if not logger.handlers:
        # Get log level from environment
        level = _get_log_level()
        logger.setLevel(level)

        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)

        # Create colored formatter
        formatter = ColoredFormatter(
            fmt="%(levelname)s [%(name)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)

        logger.addHandler(handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get or create a logger for the given name."""
    return logging.getLogger(name)


def set_log_level(level: int, component: str | None = None):
    """
    Set the log level for Nominal loggers.

    Args:
        level: Logging level (e.g., logging.DEBUG, logging.INFO)
        component: Optional component name to filter (e.g., 'processor', 'reader')
                   If None, sets level for all 'nominal.*' loggers
    """
    prefix = "nominal"
    if component:
        prefix = f"nominal.{component}"

    # Get all logger names that start with the prefix
    for name in list(logging.Logger.manager.loggerDict.keys()):
        if name.startswith(prefix):
            logger = logging.getLogger(name)
            logger.setLevel(level)
            for handler in logger.handlers:
                handler.setLevel(level)


def configure_logging(level: Optional[int] = None, component: Optional[str] = None):
    """
    Configure logging for the Nominal project.

    This function sets the log level for Nominal loggers. If level is not provided,
    it uses the NOMINAL_LOG_LEVEL environment variable (defaults to INFO).

    Args:
        level: Logging level (e.g., logging.DEBUG, logging.INFO).
               If None, uses NOMINAL_LOG_LEVEL environment variable.
        component: Optional component name to configure ('processor', 'reader', etc.)
                   If None, configures all Nominal components

    Examples:
        # Configure all components using environment variable
        configure_logging()

        # Configure all components to DEBUG level
        configure_logging(logging.DEBUG)

        # Configure only processor to DEBUG level
        configure_logging(logging.DEBUG, component='processor')

        # Configure only reader to WARNING level
        configure_logging(logging.WARNING, component='reader')
    """
    if level is None:
        level = _get_log_level()
    set_log_level(level, component=component)


# Default logger for the nominal package
_logger = setup_logger("nominal")
