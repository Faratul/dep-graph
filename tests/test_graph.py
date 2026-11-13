"""Тесты построения графа зависимостей."""

import unittest

from src.file_repository import FileRepository
from src.graph import build_graph
from tests import data_path


def make_graph(file_name, root, max_depth, substring=""):
    """Построить граф для тестового файла."""
    repo = FileRepository(data_path(file_name))
    return build_graph(root, repo.get_dependencies, max_depth, substring)


class BuildGraphTest(unittest.TestCase):
    """Проверка обхода в ширину."""

    def test_full_diamond(self):
        """Ромб при достаточной глубине."""
        graph = make_graph("simple.txt", "A", 3)
        self.assertEqual(
            graph, {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
        )

    def test_bfs_order(self):
        """Пакеты идут в порядке обхода по уровням."""
        graph = make_graph("demo.txt", "A", 10)
        self.assertEqual(
            list(graph), ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
        )

    def test_depth_limit(self):
        """Глубина 1: только прямые зависимости."""
        graph = make_graph("simple.txt", "A", 1)
        self.assertEqual(graph, {"A": ["B", "C"], "B": [], "C": []})

    def test_chain_depth(self):
        """Длинная цепочка обрезается по глубине."""
        graph = make_graph("chain.txt", "A", 2)
        self.assertEqual(list(graph), ["A", "B", "C"])

    def test_filter(self):
        """Пакеты с подстрокой в имени не учитываются."""
        graph = make_graph("simple.txt", "A", 3, "C")
        self.assertEqual(graph, {"A": ["B"], "B": ["D"], "D": []})

    def test_filter_removes_branch(self):
        """Вместе с отфильтрованным пакетом исчезает его ветка."""
        graph = make_graph("chain.txt", "A", 10, "C")
        self.assertEqual(graph, {"A": ["B"], "B": []})

    def test_cycle(self):
        """Цикл и самозависимость не вызывают бесконечного обхода."""
        graph = make_graph("cycle.txt", "A", 50)
        self.assertEqual(
            graph, {"A": ["B", "D"], "B": ["C"], "C": ["A"], "D": ["D"]}
        )

    def test_each_package_requested_once(self):
        """Зависимости каждого пакета запрашиваются один раз."""
        repo = FileRepository(data_path("demo.txt"))
        calls = []

        def get_neighbors(name):
            """Запомнить запрос и вернуть зависимости."""
            calls.append(name)
            return repo.get_dependencies(name)

        build_graph("A", get_neighbors, 10)
        self.assertEqual(len(calls), len(set(calls)))


if __name__ == "__main__":
    unittest.main()
