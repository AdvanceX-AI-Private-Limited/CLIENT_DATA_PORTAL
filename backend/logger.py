import os
import logging
import inspect
from logging.handlers import TimedRotatingFileHandler
from typing import Optional

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def create_logger(file_name: Optional[str] = None) -> logging.Logger:
    """
    Creates and configures a logger with file rotation and detailed formatting.
    
    Args:
        file_name (Optional[str]): Optional name for the log file. If not provided,
                                  the name will be derived from the calling script.
    
    Returns:
        logging.Logger: Configured logger instance.
    
    Raises:
        OSError: If there are issues creating directories.
        Exception: For other unexpected errors during logger setup.
    """
    try:
        # Determine the log file name
        if file_name is None:
            frame = inspect.stack()[1]
            file_path = frame.filename
            file_name = os.path.splitext(os.path.basename(file_path))[0]

        root = ROOT_DIR

        # Create directory structure
        logdir = os.path.join(root, 'logs')
        os.makedirs(logdir, exist_ok=True)

        # Create subdirectory for this script's logs
        filedir = os.path.join(logdir, file_name)
        os.makedirs(filedir, exist_ok=True)

        # Configure log file path and formatting
        log_file_path = os.path.join(filedir, f'{file_name}.log')
        
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Configure rotating file handler
        handler = TimedRotatingFileHandler(
            log_file_path,
            when='midnight',
            interval=1,
            encoding='utf-8',
            backupCount=5  # Keep logs for 5 days
        )
        handler.suffix = "%Y-%m-%d.log"
        handler.setFormatter(formatter)

        # Create and configure logger
        logger = logging.getLogger(file_name)
        logger.setLevel(logging.INFO)
        
        # Avoid duplicate handlers
        if not logger.handlers:
            logger.addHandler(handler)
        
        # Add console handler for development
        if os.getenv('ENVIRONMENT', 'production').lower() == 'development':
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        return logger

    except OSError as e:
        print(f"Failed to create logger directories: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error creating logger: {e}")
        raise