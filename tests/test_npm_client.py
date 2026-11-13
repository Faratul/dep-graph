"""Тесты получения зависимостей из репозитория npm."""

import functools
import json
import os
import tempfile
import threading
import unittest
from http.server import HTTPServer, SimpleHTTPRequestHandler

from src.errors import RepoError
from src.npm_client import (
    NpmRepository,
    build_url,
    extract_dependencies,
)

PACKAGES = {
    "a/latest": {"name": "a", "dependencies": {"c": "^1", "b": "^2"}},
    "leaf/latest": {"name": "leaf"},
    "@sc/pkg/latest": {"name": "@sc/pkg", "dependencies": {"x": "1"}},
}


class QuietHandler(SimpleHTTPRequestHandler):
    """Отдаёт файлы из папки и не печатает журнал запросов."""

    def log_message(self, *args):
        """Не печатать журнал запросов."""


def write_packages(folder):
    """Создать в папке файлы с описанием пакетов, как в реестре npm."""
    for relative, document in PACKAGES.items():
        path = os.path.join(folder, *relative.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as file:
            json.dump(document, file)


class BuildUrlTest(unittest.TestCase):
    """Проверка построения URL."""

    def test_plain_name(self):
        """Обычное имя пакета."""
        self.assertEqual(
            build_url("https://r.io/", "debug"), "https://r.io/debug/latest"
        )

    def test_scoped_name(self):
        """Имя с областью видимости: слэш кодируется."""
        self.assertEqual(
            build_url("https://r.io", "@sc/pkg"),
            "https://r.io/@sc%2Fpkg/latest",
        )


class ExtractDependenciesTest(unittest.TestCase):
    """Проверка чтения поля dependencies."""

    def test_sorted_names(self):
        """Имена возвращаются отсортированными."""
        manifest = {"dependencies": {"b": "1", "a": "2"}}
        self.assertEqual(extract_dependencies(manifest), ["a", "b"])

    def test_no_dependencies(self):
        """Поля dependencies нет — зависимостей нет."""
        self.assertEqual(extract_dependencies({"name": "x"}), [])

    def test_bad_format(self):
        """Неверный формат документа."""
        with self.assertRaises(RepoError):
            extract_dependencies({"dependencies": ["a"]})
        with self.assertRaises(RepoError):
            extract_dependencies([])


class NpmRepositoryTest(unittest.TestCase):
    """Проверка запросов к локальному серверу."""

    @classmethod
    def setUpClass(cls):
        """Запустить локальный сервер."""
        cls.folder = tempfile.TemporaryDirectory()
        write_packages(cls.folder.name)
        handler = functools.partial(QuietHandler, directory=cls.folder.name)
        cls.server = HTTPServer(("127.0.0.1", 0), handler)
        cls.url = f"http://127.0.0.1:{cls.server.server_port}"
        thread = threading.Thread(target=cls.server.serve_forever)
        thread.daemon = True
        thread.start()

    @classmethod
    def tearDownClass(cls):
        """Остановить локальный сервер."""
        cls.server.shutdown()
        cls.server.server_close()
        cls.folder.cleanup()

    def test_dependencies(self):
        """Прямые зависимости найдены."""
        repo = NpmRepository(self.url)
        self.assertEqual(repo.get_dependencies("a"), ["b", "c"])

    def test_leaf_and_scoped(self):
        """Пакет без зависимостей и пакет с областью видимости."""
        repo = NpmRepository(self.url)
        self.assertEqual(repo.get_dependencies("leaf"), [])
        self.assertEqual(repo.get_dependencies("@sc/pkg"), ["x"])

    def test_not_found(self):
        """Несуществующий пакет."""
        with self.assertRaises(RepoError):
            NpmRepository(self.url).get_dependencies("missing")

    def test_connection_error(self):
        """Репозиторий недоступен."""
        with self.assertRaises(RepoError):
            NpmRepository("http://127.0.0.1:9").get_dependencies("a")


if __name__ == "__main__":
    unittest.main()
