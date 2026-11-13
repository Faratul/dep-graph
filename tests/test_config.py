"""Тесты разбора и проверки параметров."""

import unittest

from src.config import parse_config
from src.errors import ConfigError
from tests import data_path


class ParseConfigTest(unittest.TestCase):
    """Проверка параметров командной строки."""

    def test_real_mode_defaults(self):
        """Режим npm: значения по умолчанию."""
        config = parse_config(["-p", "debug"])
        self.assertEqual(config.package, "debug")
        self.assertEqual(config.repo, "https://registry.npmjs.org")
        self.assertFalse(config.test_mode)
        self.assertEqual(config.max_depth, 2)
        self.assertEqual(config.filter_substring, "")

    def test_scoped_package(self):
        """Имя пакета с областью видимости допустимо."""
        config = parse_config(["-p", "@babel/core"])
        self.assertEqual(config.package, "@babel/core")

    def test_test_mode(self):
        """Тестовый режим с существующим файлом."""
        path = data_path("simple.txt")
        config = parse_config(["-p", "A", "-t", "-r", path, "-a", "-d", "3"])
        self.assertTrue(config.test_mode)
        self.assertTrue(config.ascii_tree)
        self.assertEqual(config.max_depth, 3)

    def test_missing_package(self):
        """Имя пакета обязательно."""
        with self.assertRaises(ConfigError):
            parse_config([])

    def test_bad_package_names(self):
        """Неправильные имена пакетов."""
        with self.assertRaises(ConfigError):
            parse_config(["-p", "Bad Name!"])
        with self.assertRaises(ConfigError):
            parse_config(["-p", "abc", "-t", "-r", data_path("simple.txt")])

    def test_bad_url(self):
        """Некорректный URL репозитория."""
        with self.assertRaises(ConfigError):
            parse_config(["-p", "debug", "-r", "not-a-url"])
        with self.assertRaises(ConfigError):
            parse_config(["-p", "debug", "-r", "ftp://example.com"])

    def test_test_file_errors(self):
        """Файл тестового репозитория не задан или не найден."""
        with self.assertRaises(ConfigError):
            parse_config(["-p", "A", "-t"])
        with self.assertRaises(ConfigError):
            parse_config(["-p", "A", "-t", "-r", "no_such_file.txt"])

    def test_bad_depth(self):
        """Глубина: не число, отрицательная, слишком большая."""
        for value in ("abc", "-1", "1000", "1.5"):
            with self.assertRaises(ConfigError):
                parse_config(["-p", "debug", "-d", value])

    def test_filter_matches_package(self):
        """Фильтр не должен исключать сам анализируемый пакет."""
        with self.assertRaises(ConfigError):
            parse_config(["-p", "debug", "-f", "bug"])


if __name__ == "__main__":
    unittest.main()
