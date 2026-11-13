"""Тесты текста диаграммы PlantUML и запуска PlantUML."""

import os
import unittest
from unittest import mock

from src.errors import RenderError
from src.plantuml import PLANTUML_ENV, render_png, to_plantuml


class ToPlantUmlTest(unittest.TestCase):
    """Проверка текста диаграммы."""

    def test_text(self):
        """Узлы, рёбра и выделение корня."""
        graph = {"A": ["B"], "B": ["A"]}
        lines = to_plantuml(graph, "A").splitlines()
        self.assertEqual(lines[0], "@startuml")
        self.assertEqual(lines[-1], "@enduml")
        self.assertIn('component "A" as n0 #LightGreen', lines)
        self.assertIn('component "B" as n1', lines)
        self.assertIn("n0 --> n1", lines)
        self.assertIn("n1 --> n0", lines)

    def test_special_characters(self):
        """Имена вида @scope/name допустимы."""
        text = to_plantuml({"@a/b": ["c.js"], "c.js": []}, "@a/b")
        self.assertIn('component "@a/b" as n0', text)
        self.assertIn('component "c.js" as n1', text)


class RenderPngTest(unittest.TestCase):
    """Проверка ошибок запуска PlantUML."""

    def test_command_not_found(self):
        """PlantUML не установлен."""
        with mock.patch.dict(os.environ, {PLANTUML_ENV: "no-such-cmd-xyz"}):
            with self.assertRaises(RenderError):
                render_png("graph.puml")

    def test_command_fails(self):
        """PlantUML завершился с ошибкой."""
        with mock.patch.dict(os.environ, {PLANTUML_ENV: "false"}):
            with self.assertRaises(RenderError):
                render_png("graph.puml")


if __name__ == "__main__":
    unittest.main()
