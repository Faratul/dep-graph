"""Тесты тестового репозитория (чтение файла)."""

import os
import tempfile
import unittest

from src.errors import RepoError
from src.file_repository import FileRepository, parse_repo_text
from tests import data_path


class ParseRepoTextTest(unittest.TestCase):
    """Проверка разбора текста файла."""

    def test_valid_text(self):
        """Обычный файл с комментарием и пустой строкой."""
        text = "# комментарий\n\nA: B C\nB:\n"
        self.assertEqual(
            parse_repo_text(text), {"A": ["B", "C"], "B": []}
        )

    def test_duplicate_dependencies_removed(self):
        """Повторы зависимостей в строке убираются."""
        self.assertEqual(parse_repo_text("A: B B"), {"A": ["B"]})

    def test_bad_lines(self):
        """Строки с ошибками формата."""
        for text in ("A B", "a: B", "A: b", "A: B\nA: C"):
            with self.assertRaises(RepoError):
                parse_repo_text(text)


class FileRepositoryTest(unittest.TestCase):
    """Проверка класса FileRepository."""

    def test_get_dependencies(self):
        """Зависимости известного пакета."""
        repo = FileRepository(data_path("simple.txt"))
        self.assertEqual(repo.get_dependencies("A"), ["B", "C"])
        self.assertEqual(repo.get_dependencies("D"), [])

    def test_package_only_in_dependencies(self):
        """Пакет, описанный только как зависимость, существует."""
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "repo.txt")
            with open(path, "w", encoding="utf-8") as file:
                file.write("A: Z\n")
            self.assertEqual(FileRepository(path).get_dependencies("Z"), [])

    def test_unknown_package(self):
        """Неизвестный пакет."""
        repo = FileRepository(data_path("simple.txt"))
        with self.assertRaises(RepoError):
            repo.get_dependencies("X")

    def test_missing_file(self):
        """Файла нет."""
        with self.assertRaises(RepoError):
            FileRepository(data_path("no_such_file.txt"))


if __name__ == "__main__":
    unittest.main()
