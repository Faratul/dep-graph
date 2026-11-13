"""Тестовый репозиторий: граф зависимостей, описанный в текстовом файле.

Формат файла: одна строка на пакет, ``ИМЯ: ЗАВИСИМОСТЬ ЗАВИСИМОСТЬ ...``.
Имена пакетов состоят из больших латинских букв. Пустые строки и
строки, начинающиеся с ``#``, пропускаются. Пример::

    A: B C
    B: C
    C:
"""

from .config import TEST_NAME_RE
from .errors import RepoError

COMMENT_PREFIX = "#"
SEPARATOR = ":"


def check_name(name, number):
    """Проверить имя пакета в строке файла."""
    if not TEST_NAME_RE.match(name):
        raise RepoError(
            f"строка {number}: имя {name!r} должно состоять из больших "
            "латинских букв"
        )


def parse_line(line, number):
    """Разобрать строку «ИМЯ: ЗАВИСИМОСТИ», вернуть пару (имя, список)."""
    name, separator, rest = line.partition(SEPARATOR)
    if not separator:
        raise RepoError(f"строка {number}: нет символа {SEPARATOR!r}")
    name = name.strip()
    check_name(name, number)
    dependencies = list(dict.fromkeys(rest.split()))
    for dependency in dependencies:
        check_name(dependency, number)
    return name, dependencies


def parse_repo_text(text):
    """Превратить текст файла в словарь «пакет -> список зависимостей»."""
    packages = {}
    for number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith(COMMENT_PREFIX):
            continue
        name, dependencies = parse_line(line, number)
        if name in packages:
            raise RepoError(f"строка {number}: пакет {name} описан дважды")
        packages[name] = dependencies
    return packages


class FileRepository:
    """Тестовый репозиторий, прочитанный из файла."""

    def __init__(self, path):
        """Прочитать и разобрать файл репозитория."""
        try:
            with open(path, encoding="utf-8") as file:
                text = file.read()
        except OSError as error:
            raise RepoError(f"не удалось прочитать {path}: {error}") \
                from None
        self.packages = parse_repo_text(text)
        self.known = set(self.packages)
        self.dependents = {}
        for name, dependencies in self.packages.items():
            self.known.update(dependencies)
            for dependency in dependencies:
                self.dependents.setdefault(dependency, []).append(name)

    def check_known(self, name):
        """Убедиться, что пакет есть в тестовом репозитории."""
        if name not in self.known:
            raise RepoError(f"пакет не найден в тестовом репозитории: {name}")

    def get_dependencies(self, name):
        """Вернуть список прямых зависимостей пакета."""
        self.check_known(name)
        return list(self.packages.get(name, []))

    def get_dependents(self, name):
        """Вернуть пакеты, которые напрямую зависят от пакета."""
        self.check_known(name)
        return list(self.dependents.get(name, []))
