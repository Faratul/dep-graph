"""Тесты ASCII-дерева."""

import unittest

from src.ascii_tree import build_tree_lines
from src.file_repository import FileRepository
from src.graph import build_graph
from tests import data_path


def tree_for(file_name, root, max_depth):
    """Построить строки дерева для тестового файла."""
    repo = FileRepository(data_path(file_name))
    graph = build_graph(root, repo.get_dependencies, max_depth)
    return build_tree_lines(graph, root)


class AsciiTreeTest(unittest.TestCase):
    """Проверка вида дерева."""

    def test_chain(self):
        """Цепочка выводится лесенкой."""
        self.assertEqual(
            tree_for("chain.txt", "A", 3),
            ["A", "`-- B", "    `-- C", "        `-- D"],
        )

    def test_diamond_repeat(self):
        """Повторный пакет помечается и не раскрывается."""
        self.assertEqual(
            tree_for("simple.txt", "A", 3),
            [
                "A",
                "|-- B",
                "|   `-- D",
                "`-- C",
                "    `-- D",
            ],
        )

    def test_cycle(self):
        """Цикл помечается как повтор."""
        self.assertEqual(
            tree_for("cycle.txt", "A", 10),
            [
                "A",
                "|-- B",
                "|   `-- C",
                "|       `-- A (уже показан выше)",
                "`-- D",
                "    `-- D (уже показан выше)",
            ],
        )

    def test_only_root(self):
        """Граф из одного пакета."""
        self.assertEqual(tree_for("simple.txt", "D", 3), ["D"])


if __name__ == "__main__":
    unittest.main()
