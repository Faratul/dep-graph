"""Тесты обратных зависимостей."""

import unittest

from src.config import parse_config
from src.errors import RepoError
from src.file_repository import FileRepository
from src.graph import build_graph
from src.npm_client import NpmRepository
from tests import data_path
from tests.test_main import run_main


def reverse_names(file_name, root, max_depth, substring=""):
    """Вернуть имена пакетов, зависящих от root, в порядке обхода."""
    repo = FileRepository(data_path(file_name))
    graph = build_graph(root, repo.get_dependents, max_depth, substring)
    return [name for name in graph if name != root]


class ReverseDependenciesTest(unittest.TestCase):
    """Проверка обратных зависимостей на тестовом репозитории."""

    def test_direct_dependents(self):
        """Глубина 1: только пакеты, зависящие напрямую."""
        self.assertEqual(reverse_names("simple.txt", "D", 1), ["B", "C"])

    def test_transitive_dependents(self):
        """Глубина 2: добавляются транзитивные зависимости."""
        self.assertEqual(
            reverse_names("simple.txt", "D", 2), ["B", "C", "A"]
        )

    def test_no_dependents(self):
        """От корня никто не зависит."""
        self.assertEqual(reverse_names("simple.txt", "A", 5), [])

    def test_filter(self):
        """Фильтр исключает пакет и его ветку."""
        self.assertEqual(reverse_names("simple.txt", "D", 5, "B"), ["C", "A"])

    def test_cycle(self):
        """В цикле обход завершается."""
        self.assertEqual(reverse_names("cycle.txt", "A", 50), ["C", "B"])

    def test_self_dependency(self):
        """Самозависимость D -> D не добавляет D в список."""
        self.assertEqual(
            reverse_names("cycle.txt", "D", 5), ["A", "C", "B"]
        )

    def test_unknown_package(self):
        """Неизвестный пакет."""
        repo = FileRepository(data_path("simple.txt"))
        with self.assertRaises(RepoError):
            repo.get_dependents("X")

    def test_npm_not_supported(self):
        """Реестр npm не умеет искать обратные зависимости."""
        with self.assertRaises(RepoError):
            NpmRepository("https://registry.npmjs.org").get_dependents("a")


class ReverseCliTest(unittest.TestCase):
    """Проверка режима --reverse из командной строки."""

    def test_option(self):
        """Опция разбирается."""
        self.assertTrue(parse_config(["-p", "debug", "-R"]).reverse)
        self.assertFalse(parse_config(["-p", "debug"]).reverse)

    def test_output(self):
        """Вывод списка обратных зависимостей."""
        code, out, _ = run_main(
            "-p", "D", "-t", "-r", data_path("simple.txt"), "-d", "3", "-R"
        )
        self.assertEqual(code, 0)
        self.assertIn("  - B\n  - C\n  - A\n", out)

    def test_npm_error(self):
        """Для реального npm режим выдаёт понятную ошибку."""
        code, _, err = run_main("-p", "debug", "-R")
        self.assertEqual(code, 1)
        self.assertIn("Ошибка", err)


if __name__ == "__main__":
    unittest.main()
