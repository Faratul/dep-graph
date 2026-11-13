"""Тесты запуска программы целиком."""

import contextlib
import io
import unittest

from src.main import EXIT_ERROR, EXIT_OK, main
from tests import data_path


def run_main(*args):
    """Запустить main, вернуть код завершения, stdout и stderr."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(list(args))
    return code, out.getvalue(), err.getvalue()


class MainTest(unittest.TestCase):
    """Проверка вывода программы."""

    def test_graph_output(self):
        """Граф выводится по строке на пакет."""
        code, out, _ = run_main(
            "-p", "A", "-t", "-r", data_path("simple.txt"), "-d", "3"
        )
        self.assertEqual(code, EXIT_OK)
        self.assertIn("A -> B, C", out)
        self.assertIn("D -> (нет)", out)

    def test_unknown_package(self):
        """Неизвестный пакет даёт ошибку."""
        code, _, err = run_main(
            "-p", "X", "-t", "-r", data_path("simple.txt")
        )
        self.assertEqual(code, EXIT_ERROR)
        self.assertIn("Ошибка", err)


if __name__ == "__main__":
    unittest.main()
