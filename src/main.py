"""Точка входа: запуск инструмента из командной строки."""

import sys

from .config import parse_config
from .errors import ConfigError, RepoError
from .npm_client import NpmRepository

EXIT_OK = 0
EXIT_ERROR = 1


def print_dependencies(package, dependencies):
    """Вывести на экран прямые зависимости пакета."""
    print(f"Прямые зависимости пакета {package}:")
    for name in dependencies:
        print(f"  - {name}")
    if not dependencies:
        print("  (зависимостей нет)")


def run(argv):
    """Выполнить работу программы этапа 2."""
    config = parse_config(argv)
    if config.test_mode:
        raise ConfigError("тестовый режим пока не поддерживается")
    repo = NpmRepository(config.repo)
    print_dependencies(config.package, repo.get_dependencies(config.package))


def main(argv=None):
    """Запустить программу и вернуть код завершения."""
    try:
        run(argv)
    except (ConfigError, RepoError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return EXIT_ERROR
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
