import logging
import os


def setup_logger(name, level=None):
    """Set up a logger with consistent formatting."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    
    log_level = level or (logging.DEBUG if os.getenv('FLASK_ENV') == 'development' else logging.INFO)
    logger.setLevel(log_level)
    
    handler = logging.StreamHandler()
    handler.setLevel(log_level)
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger
