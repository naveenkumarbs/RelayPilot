import logging
from logging.config import dictConfig

def configure_logging(log_level: str) -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": (
                        "%(asctime)s %(levelname)s "
                        "%(name)s %(message)s"
                    ),
                    "datefmt": "%Y-%m-%dT%H:%M:%S %Z",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "formatter": "standard",
                }
            },
            "root": {
                "handlers": ["console"],
                "level": log_level,
            },
            "loggers": {
                "relaypilot": {
                    "level": log_level,
                    "propagate": True,
                },
                "uvicron.access": {
                    "handlers": [],
                    "propagate": False,
                },
            },
        }
    )