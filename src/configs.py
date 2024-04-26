import argparse
import logging
from logging.handlers import RotatingFileHandler

from constants import (BASE_DIR, FILE_OUTPUT, LOGS_DIR,
                       LOG_FORMAT, PRETTY_OUTPUT, READABLE_DATETIME_FORMAT)


def configure_argument_parser(available_modes):
    parser = argparse.ArgumentParser(description='Парсер документации Python')

    parser.add_argument(
        'mode',
        choices=available_modes,
        help='Режимы работы парсера',
    )
    parser.add_argument(
        '-c',
        '--clear-cache',
        action='store_true',
        help='Очистка кеша',
    )
    parser.add_argument(
        '-o',
        '--output',
        choices=(PRETTY_OUTPUT, FILE_OUTPUT),
        help='Дополнительные способы вывода данных',
    )

    return parser


def configure_logging():
    logs_dir = BASE_DIR / LOGS_DIR
    logs_dir.mkdir(parents=True, exist_ok=True)
    logs_file = logs_dir / 'parser.log'

    rotating_handler = RotatingFileHandler(
        logs_file, maxBytes=10 ** 6, backupCount=5,
    )

    logging.basicConfig(
        datefmt=READABLE_DATETIME_FORMAT,
        format=LOG_FORMAT,
        level=logging.INFO,
        handlers=(rotating_handler, logging.StreamHandler()),
    )
