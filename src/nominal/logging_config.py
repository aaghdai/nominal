"""
Logging configuration for the Nominal project.
Provides colored logging for all components (reader, processor, orchestrator).
"""

import logging
import sys
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m',       # Reset
        'BOLD': '\033[1m',        # Bold
    }
    
    def format(self, record):
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[levelname]}{self.COLORS['BOLD']}"
                f"{levelname:8s}{self.COLORS['RESET']}"
            )
        
        # Format the message
        message = super().format(record)
        
        return message


def setup_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Setup a logger with colored output.
    
    Args:
        name: Logger name (e.g., 'nominal.processor', 'nominal.reader')
        level: Logging level (defaults to INFO)
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    
    # Only add handler if none exists
    if not logger.handlers:
        # Set level
        if level is None:
            level = logging.INFO
        logger.setLevel(level)
        
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        
        # Create colored formatter
        formatter = ColoredFormatter(
            fmt='%(levelname)s [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get or create a logger for the given name."""
    return logging.getLogger(name)


def set_log_level(level: int, component: Optional[str] = None):
    """
    Set the log level for Nominal loggers.
    
    Args:
        level: Logging level (e.g., logging.DEBUG, logging.INFO)
        component: Optional component name to filter (e.g., 'processor', 'reader')
                   If None, sets level for all 'nominal.*' loggers
    """
    prefix = 'nominal'
    if component:
        prefix = f'nominal.{component}'
    
    # Get all logger names that start with the prefix
    for name in list(logging.Logger.manager.loggerDict.keys()):
        if name.startswith(prefix):
            logger = logging.getLogger(name)
            logger.setLevel(level)
            for handler in logger.handlers:
                handler.setLevel(level)


def configure_logging(level: int = logging.INFO, component: Optional[str] = None):
    """
    Configure logging for the Nominal project.
    
    This is the main entry point for configuring logging at the project level.
    
    Args:
        level: Logging level (defaults to INFO)
        component: Optional component name to configure ('processor', 'reader', etc.)
                   If None, configures all Nominal components
    
    Examples:
        # Configure all components to DEBUG level
        configure_logging(logging.DEBUG)
        
        # Configure only processor to DEBUG level
        configure_logging(logging.DEBUG, component='processor')
        
        # Configure only reader to WARNING level
        configure_logging(logging.WARNING, component='reader')
    """
    set_log_level(level, component=component)


# Default logger for the nominal package
_logger = setup_logger('nominal')

