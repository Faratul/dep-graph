"""Точка входа: запуск инструмента из командной строки."""

import sys

from .ascii_tree import build_tree_lines
from .config import parse_config
from .errors import ConfigError, RenderError, RepoError
from .file_repository import FileRepository
from .graph import build_graph
from .npm_client import NpmRepository
from .plantuml import open_image, render_png, save_text, to_plantuml

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


def show_graph(config, graph):
    """Показать граф: список, ASCII-дерево, PlantUML и картинку."""
    print_graph(config, graph)
    if config.ascii_tree:
        print("ASCII-дерево зависимостей:")
        print("\n".join(build_tree_lines(graph, config.package)))
    text = to_plantuml(graph, config.package)
    print("Текст диаграммы PlantUML:")
    print(text, end="")
    puml_path = save_text(text)
    print(f"Диаграмма сохранена в файл: {puml_path}")
    png_path = render_png(puml_path)
    if not open_image(png_path):
        print(f"Не удалось открыть картинку, откройте файл: {png_path}")


def print_reverse(config, graph):
    """Вывести обратные зависимости: пакеты, зависящие от заданного."""
    others = [name for name in graph if name != config.package]
    print(
        f"Обратные зависимости пакета {config.package} "
        f"(глубина {config.max_depth}, фильтр {config.filter_substring!r}):"
    )
    for name in others:
        print(f"  - {name}")
    if not others:
        print(f"  {NO_DEPENDENCIES}")


def run(argv):
    """Выполнить работу программы."""
    config = parse_config(argv)
    repo = create_repository(config)
    if config.reverse:
        get_neighbors, show = repo.get_dependents, print_reverse
    else:
        get_neighbors, show = repo.get_dependencies, show_graph
    graph = build_graph(
        config.package,
        get_neighbors,
        config.max_depth,
        config.filter_substring,
    )
    show(config, graph)


def main(argv=None):
    """Запустить программу и вернуть код завершения."""
    try:
        run(argv)
    except (ConfigError, RepoError, RenderError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return EXIT_ERROR
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
