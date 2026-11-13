"""Тесты запуска программы целиком."""

import contextlib
import io
import unittest
from unittest import mock

from src.errors import RenderError
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

    @mock.patch("src.main.save_text", return_value="graph.puml")
    @mock.patch("src.main.open_image", return_value=True)
    @mock.patch("src.main.render_png", return_value="graph.png")
    def test_graph_output(self, render, show, save):
        """Граф выводится списком, затем PlantUML; картинка показывается."""
        code, out, _ = run_main(
            "-p", "A", "-t", "-r", data_path("simple.txt"), "-d", "3"
        )
        self.assertEqual(code, EXIT_OK)
        self.assertIn("A -> B, C", out)
        self.assertIn("D -> (нет)", out)
        self.assertIn("@startuml", out)
        self.assertNotIn("ASCII-дерево", out)
        render.assert_called_once_with("graph.puml")
        show.assert_called_once_with("graph.png")
        save.assert_called_once()

    @mock.patch("src.main.save_text", return_value="graph.puml")
    @mock.patch("src.main.open_image", return_value=True)
    @mock.patch("src.main.render_png", return_value="graph.png")
    def test_ascii_tree_option(self, *_):
        """С опцией --ascii-tree выводится дерево."""
        code, out, _ = run_main(
            "-p", "A", "-t", "-r", data_path("simple.txt"), "-d", "3", "-a"
        )
        self.assertEqual(code, EXIT_OK)
        self.assertIn("ASCII-дерево зависимостей:\nA\n|-- B\n", out)

    @mock.patch("src.main.save_text", return_value="graph.puml")
    @mock.patch("src.main.render_png", side_effect=RenderError("нет"))
    def test_render_error(self, *_):
        """Ошибка PlantUML выводится как ошибка."""
        code, _, err = run_main(
            "-p", "A", "-t", "-r", data_path("simple.txt")
        )
        self.assertEqual(code, EXIT_ERROR)
        self.assertIn("Ошибка: нет", err)

    def test_unknown_package(self):
        """Неизвестный пакет даёт ошибку."""
        code, _, err = run_main(
            "-p", "X", "-t", "-r", data_path("simple.txt")
        )
        self.assertEqual(code, EXIT_ERROR)
        self.assertIn("Ошибка", err)


if __name__ == "__main__":
    unittest.main()
