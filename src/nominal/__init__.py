"""
Nominal: Tax document processing system.

This package provides tools for reading, processing, and organizing tax documents.
"""

# Logging configuration - available at project level
from .logging_config import (
    setup_logger,
    get_logger,
    set_log_level,
    configure_logging,
)

__all__ = [
    'setup_logger',
    'get_logger',
    'set_log_level',
    'configure_logging',
]

