import os
import sys
import json
import logging
import logging.config
import logging.handlers
import functools
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional


LOGS_DIR = Path(__file__).parent / "logs"


class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[36m',
        'INFO': '\033[32m',
        'WARNING': '\033[33m',
        'ERROR': '\033[31m',
        'CRITICAL': '\033[35m',
    }
    RESET = '\033[0m'
    BOLD = '\033[1m'

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname_colored = f"{self.BOLD}{color}{record.levelname}{self.RESET}"
        record.name_colored = f"\033[34m{record.name}{self.RESET}"
        return super().format(record)


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info) if record.exc_info[0] else None
            }
        
        extra_data = getattr(record, 'extra_data', None)
        if extra_data is not None:
            log_data["extra"] = extra_data
            
        return json.dumps(log_data, default=str)


def get_log_level() -> str:
    level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
    if level not in valid_levels:
        level = 'INFO'
    return level


def get_logging_config() -> dict:
    log_level = get_log_level()
    log_file = str(LOGS_DIR / "bot.log")
    
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "colored": {
                "()": ColoredFormatter,
                "format": "%(asctime)s | %(levelname_colored)s | %(name_colored)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "json": {
                "()": JSONFormatter
            },
            "standard": {
                "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "colored",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "json",
                "filename": log_file,
                "maxBytes": 5 * 1024 * 1024,
                "backupCount": 3,
                "encoding": "utf-8"
            }
        },
        "root": {
            "level": log_level,
            "handlers": ["console", "file"]
        },
        "loggers": {
            "werkzeug": {
                "level": "WARNING",
                "handlers": ["console", "file"],
                "propagate": False
            },
            "urllib3": {
                "level": "WARNING",
                "handlers": ["console", "file"],
                "propagate": False
            }
        }
    }


def setup_logging() -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    config = get_logging_config()
    logging.config.dictConfig(config)
    logger = logging.getLogger(__name__)
    logger.debug(f"Logging initialized with level: {get_log_level()}")
    logger.debug(f"Log file: {LOGS_DIR / 'bot.log'}")


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_exceptions(logger: Optional[logging.Logger] = None, 
                   level: int = logging.ERROR,
                   reraise: bool = True) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            log = logger or logging.getLogger(func.__module__)
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log.log(level, f"Exception in {func.__name__}: {e}", exc_info=True)
                if reraise:
                    raise
                return None
        return wrapper
    return decorator


def async_log_exceptions(logger: Optional[logging.Logger] = None,
                         level: int = logging.ERROR,
                         reraise: bool = True) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            log = logger or logging.getLogger(func.__module__)
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                log.log(level, f"Exception in {func.__name__}: {e}", exc_info=True)
                if reraise:
                    raise
                return None
        return wrapper
    return decorator


def configure_flask_logging(app: Any) -> None:
    setup_logging()
    
    log_level = get_log_level()
    app.logger.setLevel(getattr(logging, log_level))
    
    for handler in app.logger.handlers[:]:
        app.logger.removeHandler(handler)
    
    config = get_logging_config()
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level))
    console_handler.setFormatter(ColoredFormatter(
        "%(asctime)s | %(levelname_colored)s | %(name_colored)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    
    log_file = str(LOGS_DIR / "bot.log")
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setLevel(getattr(logging, log_level))
    file_handler.setFormatter(JSONFormatter())
    
    app.logger.addHandler(console_handler)
    app.logger.addHandler(file_handler)
    
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.WARNING)


if __name__ == "__main__":
    setup_logging()
    logger = get_logger(__name__)
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    @log_exceptions()
    def test_sync_function():
        raise ValueError("Test sync exception")
    
    @async_log_exceptions()
    async def test_async_function():
        raise ValueError("Test async exception")
    
    try:
        test_sync_function()
    except ValueError:
        pass
    
    import asyncio
    try:
        asyncio.run(test_async_function())
    except ValueError:
        pass
    
    print(f"\nLog file created at: {LOGS_DIR / 'bot.log'}")
