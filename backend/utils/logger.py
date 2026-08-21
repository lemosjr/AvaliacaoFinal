# backend/utils/logger.py
"""
Logging configuration using loguru.
Provides structured logging with rotation, retention, and formatting.
"""

import sys
from pathlib import Path
from loguru import logger as loguru_logger
from datetime import datetime

from backend.config.settings import Settings


def setup_logging() -> None:
    """
    Configures the logging system with loguru.
    
    Features:
    - Console logging with colors
    - File logging with rotation (10 MB)
    - Retention of 30 days
    - Structured format with timestamp, level, module, and message
    """
    
    # Remove default handlers
    loguru_logger.remove()
    
    # Console handler - with colors for development
    loguru_logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=Settings.LOG_LEVEL,
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # File handler - with rotation and retention
    log_dir = Settings.LOGS_DIR
    log_dir.mkdir(exist_ok=True)
    
    log_file_path = log_dir / 'app.log'
    
    loguru_logger.add(
        str(log_file_path),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=Settings.LOG_LEVEL,
        rotation="10 MB",       # Rotate when file reaches 10MB
        retention="30 days",    # Keep logs for 30 days
        compression="zip",      # Compress rotated files
        backtrace=True,
        diagnose=False         # Don't include sensitive data in production logs
    )
    
    # Optional: Error-only file for easier debugging
    error_log_path = log_dir / 'errors.log'
    loguru_logger.add(
        str(error_log_path),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )
    
    # Log startup message
    loguru_logger.info(f"🚀 Logging initialized for {Settings.APP_NAME} v{Settings.APP_VERSION}")
    loguru_logger.info(f"📁 Log directory: {log_dir}")
    loguru_logger.info(f"📊 Log level: {Settings.LOG_LEVEL}")


# Export logger instance
logger = loguru_logger

# Auto-setup on import (only if not already configured)
if not logger._core.handlers:
    setup_logging()