"""Точка входа: запуск инструмента из командной строки."""

import sys
from dataclasses import asdict

from .config import parse_config
from .errors import ConfigError

EXIT_OK = 0
EXIT_ERROR = 1


def print_config(config):
    """Вывести все параметры в формате «ключ: значение»."""
    for key, value in asdict(config).items():
        print(f"{key}: {value}")


def main(argv=None):
    """Запустить программу и вернуть код завершения."""
    try:
        config = parse_config(argv)
    except ConfigError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return EXIT_ERROR
    print_config(config)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
