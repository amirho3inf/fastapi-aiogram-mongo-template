import logging
from typing import Any

from fastapi_cli.utils.cli import get_rich_toolkit, get_uvicorn_log_config
from uvicorn.logging import DefaultFormatter


class ModuleFormatter(DefaultFormatter):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.toolkit = get_rich_toolkit()

    def formatMessage(self, record: logging.LogRecord) -> str:
        return self.toolkit.print_as_string(
            f"[bold blue]{record.name.capitalize()}[/bold blue] - {record.getMessage()}",
            tag=record.levelname)


config = get_uvicorn_log_config()
config['formatters']['module'] = {
    '()': ModuleFormatter,
    'fmt': config['formatters']['default']['fmt']
}
config['handlers']['module'] = {
    'class': config['handlers']['default']['class'],
    'formatter': 'module',
    'stream': config['handlers']['default']['stream']
}


def get_logger(name: str = "uvicorn"):
    if not config['loggers'].get(name):
        config['loggers'][name] = {
            'handlers': ['module'],
            'level': config['loggers']['uvicorn']['level']
        }
    logging.config.dictConfig(config)

    logger = logging.getLogger(name)
    return logger
