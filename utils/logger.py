"""
Logging Module

Provides centralized logging with color formatting and structured output.
Supports both console and in-app logging for Streamlit.
"""

import logging
import sys
from datetime import datetime
from typing import List, Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Format: [TIME] [LEVEL] [AGENT/MODULE] Message
        message = f"[{timestamp}] {color}[{record.levelname}]{self.RESET} [{record.name}] {record.getMessage()}"
        return message


class StreamlitLogHandler(logging.Handler):
    """Custom handler to capture logs for Streamlit display."""
    
    _logs: List[str] = []
    
    @classmethod
    def get_logs(cls) -> List[str]:
        """Get all captured logs."""
        return cls._logs.copy()
    
    @classmethod
    def clear_logs(cls) -> None:
        """Clear all logs."""
        cls._logs.clear()
    
    @classmethod
    def add_log(cls, message: str) -> None:
        """Add a log message directly."""
        cls._logs.append(message)
    
    def emit(self, record):
        """Emit a log record."""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            message = f"[{timestamp}] [{record.levelname}] [{record.name}] {record.getMessage()}"
            StreamlitLogHandler._logs.append(message)
        except Exception:
            self.handleError(record)


def get_logger(name: str, capture_for_streamlit: bool = True) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name (str): Logger name (typically __name__)
        capture_for_streamlit (bool): Whether to capture logs for Streamlit display
    
    Returns:
        logging.Logger: Configured logger
    """
    logger = logging.getLogger(name)
    
    # Always ensure StreamlitLogHandler is present for Streamlit compatibility
    has_streamlit_handler = any(isinstance(h, StreamlitLogHandler) for h in logger.handlers)
    has_console_handler = any(isinstance(h, logging.StreamHandler) and not isinstance(h, StreamlitLogHandler) for h in logger.handlers)
    
    if not logger.handlers or not has_console_handler:
        # Reset handlers to avoid duplicates
        logger.handlers.clear()
        logger.setLevel(logging.DEBUG)
        
        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(ColoredFormatter())
        
        logger.addHandler(console_handler)
    
    # Always add Streamlit handler if requested
    if capture_for_streamlit and not has_streamlit_handler:
        streamlit_handler = StreamlitLogHandler()
        streamlit_handler.setLevel(logging.DEBUG)
        logger.addHandler(streamlit_handler)
    
    logger.propagate = False
    
    return logger


def log_agent_start(logger: logging.Logger, agent_name: str, input_data: dict) -> None:
    """Log when an agent starts processing."""
    logger.info(f"{'='*60}")
    logger.info(f"AGENT START: {agent_name}")
    logger.info(f"Input: {input_data}")
    logger.info(f"{'='*60}")


def log_agent_thinking(logger: logging.Logger, thinking: str) -> None:
    """Log agent's reasoning/thinking."""
    logger.info(f"THINKING: {thinking}")


def log_agent_output(logger: logging.Logger, output: str) -> None:
    """Log agent's output."""
    logger.info(f"OUTPUT: {output}")


def log_agent_end(logger: logging.Logger, agent_name: str, output_data: dict) -> None:
    """Log when an agent finishes processing."""
    logger.info(f"AGENT END: {agent_name}")
    logger.info(f"Output Keys: {list(output_data.keys())}")
    logger.info(f"{'='*60}")


def log_communication(logger: logging.Logger, from_agent: str, to_agent: str, data: dict) -> None:
    """Log communication between agents."""
    logger.info(f"COMMUNICATION: {from_agent} → {to_agent}")
    logger.info(f"Data: {list(data.keys())}")

