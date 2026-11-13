"""Разбор и проверка параметров командной строки."""

import argparse
import os
import re
from dataclasses import dataclass
from urllib.parse import urlparse

from .errors import ConfigError

DEFAULT_REPO = "https://registry.npmjs.org"
DEFAULT_DEPTH = 2
MIN_DEPTH = 1
MAX_DEPTH_LIMIT = 100
NPM_NAME_MAX_LENGTH = 214
URL_SCHEMES = ("http", "https")
NPM_NAME_RE = re.compile(
    r"^(?:@[A-Za-z0-9~-][A-Za-z0-9._~-]*/)?[A-Za-z0-9~-][A-Za-z0-9._~-]*$"
)
TEST_NAME_RE = re.compile(r"^[A-Z]+$")


@dataclass(frozen=True)
class Config:
    """Параметры, которые настраивает пользователь."""

    package: str
    repo: str
    test_mode: bool
    ascii_tree: bool
    max_depth: int
    filter_substring: str
    reverse: bool


def build_parser():
    """Создать разборщик параметров командной строки."""
    parser = argparse.ArgumentParser(
        prog="dep-graph",
        description="Визуализация графа зависимостей пакетов npm.",
    )
    parser.add_argument(
        "-p", "--package", help="имя анализируемого пакета"
    )
    parser.add_argument(
        "-r", "--repo",
        help="URL репозитория npm или путь к файлу тестового репозитория",
    )
    parser.add_argument(
        "-t", "--test-mode", action="store_true",
        help="работать с тестовым репозиторием (файлом)",
    )
    parser.add_argument(
        "-a", "--ascii-tree", action="store_true",
        help="вывести зависимости в виде ASCII-дерева",
    )
    parser.add_argument(
        "-d", "--max-depth", default=str(DEFAULT_DEPTH),
        help="максимальная глубина анализа (по умолчанию 2)",
    )
    parser.add_argument(
        "-f", "--filter", dest="filter_substring", default="",
        help="не учитывать пакеты, в имени которых есть эта подстрока",
    )
    parser.add_argument(
        "-R", "--reverse", action="store_true",
        help="вывести обратные зависимости (кто зависит от пакета)",
    )
    return parser


def check_package(name, test_mode):
    """Проверить имя пакета и вернуть его."""
    if not name:
        raise ConfigError("не указано имя пакета (--package)")
    pattern = TEST_NAME_RE if test_mode else NPM_NAME_RE
    if not pattern.match(name) or len(name) > NPM_NAME_MAX_LENGTH:
        raise ConfigError(f"некорректное имя пакета: {name!r}")
    return name


def check_repo(repo, test_mode):
    """Проверить URL или путь к файлу и вернуть значение."""
    if test_mode:
        if not repo:
            raise ConfigError("в режиме тестирования укажите файл (--repo)")
        if not os.path.isfile(repo):
            raise ConfigError(f"файл тестового репозитория не найден: {repo}")
        return repo
    repo = repo or DEFAULT_REPO
    parts = urlparse(repo)
    if parts.scheme not in URL_SCHEMES or not parts.netloc:
        raise ConfigError(f"некорректный URL репозитория: {repo}")
    return repo


def check_depth(text):
    """Проверить глубину анализа и вернуть её как число."""
    try:
        depth = int(text)
    except ValueError:
        raise ConfigError(f"глубина должна быть целым числом: {text}") \
            from None
    if depth < MIN_DEPTH or depth > MAX_DEPTH_LIMIT:
        raise ConfigError(
            f"глубина должна быть от {MIN_DEPTH} до {MAX_DEPTH_LIMIT}"
        )
    return depth


def check_filter(substring, package):
    """Проверить, что фильтр не исключает сам анализируемый пакет."""
    if substring and substring in package:
        raise ConfigError(
            f"имя пакета {package!r} содержит подстроку фильтра "
            f"{substring!r}"
        )
    return substring


def parse_config(argv=None):
    """Разобрать параметры, проверить их и вернуть объект Config."""
    args = build_parser().parse_args(argv)
    package = check_package(args.package, args.test_mode)
    return Config(
        package=package,
        repo=check_repo(args.repo, args.test_mode),
        test_mode=args.test_mode,
        ascii_tree=args.ascii_tree,
        max_depth=check_depth(args.max_depth),
        filter_substring=check_filter(args.filter_substring, package),
        reverse=args.reverse,
    )
