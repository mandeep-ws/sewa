"""
Logging configuration module for the SEWA application.
Provides centralized logging setup with configurable levels.
"""

import logging
import sys
import os
from datetime import datetime

class LoggerConfig:
    """Centralized logging configuration"""
    
    def __init__(self, log_level="INFO", log_file=None):
        """
        Initialize logging configuration
        
        Args:
            log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file (str): Optional log file path
        """
        self.log_level = log_level.upper()
        self.log_file = log_file
        self.logger = None
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        # Create logger
        self.logger = logging.getLogger('sewa')
        self.logger.setLevel(getattr(logging, self.log_level))
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, self.log_level))
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler (if specified)
        if self.log_file:
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(getattr(logging, self.log_level))
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def get_logger(self):
        """Get the configured logger instance"""
        return self.logger
    
    def set_level(self, level):
        """Change logging level at runtime"""
        self.log_level = level.upper()
        self.logger.setLevel(getattr(logging, self.log_level))
        for handler in self.logger.handlers:
            handler.setLevel(getattr(logging, self.log_level))

# Global logger instance
_logger_config = None
_logger = None

def setup_logging(log_level="INFO", log_file=None):
    """
    Setup global logging configuration
    
    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file (str): Optional log file path
    """
    global _logger_config, _logger
    
    # Create logs directory if it doesn't exist
    if log_file and not os.path.exists(os.path.dirname(log_file)):
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    _logger_config = LoggerConfig(log_level, log_file)
    _logger = _logger_config.get_logger()
    
    return _logger

def get_logger():
    """Get the global logger instance"""
    global _logger
    if _logger is None:
        # Default setup if not configured
        _logger = setup_logging()
    return _logger

def set_log_level(level):
    """Change global logging level"""
    global _logger_config
    if _logger_config:
        _logger_config.set_level(level)

# Convenience functions for different log levels
def debug(message):
    """Log debug message"""
    get_logger().debug(message)

def info(message):
    """Log info message"""
    get_logger().info(message)

def warning(message):
    """Log warning message"""
    get_logger().warning(message)

def error(message):
    """Log error message"""
    get_logger().error(message)

def critical(message):
    """Log critical message"""
    get_logger().critical(message)
