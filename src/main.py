"""Точка входа: запуск инструмента из командной строки."""

import sys

from .config import parse_config
from .errors import ConfigError, RepoError
from .file_repository import FileRepository
from .graph import build_graph
from .npm_client import NpmRepository

EXIT_OK = 0
EXIT_ERROR = 1
NO_DEPENDENCIES = "(нет)"


def create_repository(config):
    """Создать тестовый репозиторий или репозиторий npm."""
    if config.test_mode:
        return FileRepository(config.repo)
    return NpmRepository(config.repo)


def print_graph(config, graph):
    """Вывести граф зависимостей: по строке на каждый пакет."""
    print(
        f"Граф зависимостей пакета {config.package} "
        f"(глубина {config.max_depth}, фильтр {config.filter_substring!r}):"
    )
    for name, children in graph.items():
        print(f"  {name} -> {', '.join(children) or NO_DEPENDENCIES}")
    edges = sum(len(children) for children in graph.values())
    print(f"Пакетов: {len(graph)}, зависимостей (рёбер): {edges}")


def run(argv):
    """Выполнить работу программы этапа 3."""
    config = parse_config(argv)
    repo = create_repository(config)
    graph = build_graph(
        config.package,
        repo.get_dependencies,
        config.max_depth,
        config.filter_substring,
    )
    print_graph(config, graph)


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
