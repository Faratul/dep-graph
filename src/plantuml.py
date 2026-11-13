"""Текстовое представление графа на языке PlantUML и показ картинки.

Для построения изображения нужен PlantUML. По умолчанию запускается
команда ``plantuml``; другую команду можно задать переменной окружения
``PLANTUML``, например ``PLANTUML="java -jar plantuml.jar"``.
"""

import os
import shlex
import subprocess
import sys

from .errors import RenderError

PUML_FILE = "graph.puml"
PLANTUML_ENV = "PLANTUML"
DEFAULT_COMMAND = "plantuml"
ROOT_COLOR = "#LightGreen"


def to_plantuml(graph, root):
    """Построить текст диаграммы PlantUML по графу зависимостей."""
    ids = {name: f"n{index}" for index, name in enumerate(graph)}
    lines = [
        "@startuml",
        "left to right direction",
        f"title Зависимости пакета {root}",
    ]
    for name, node_id in ids.items():
        color = f" {ROOT_COLOR}" if name == root else ""
        lines.append(f'component "{name}" as {node_id}{color}')
    for name, children in graph.items():
        for child in children:
            lines.append(f"{ids[name]} --> {ids[child]}")
    lines.append("@enduml")
    return "\n".join(lines) + "\n"


def save_text(text, path=PUML_FILE):
    """Сохранить текст диаграммы в файл и вернуть путь к файлу."""
    with open(path, "w", encoding="utf-8") as file:
        file.write(text)
    return path


def render_png(puml_path):
    """Построить PNG-картинку с помощью PlantUML, вернуть путь к ней."""
    command = shlex.split(os.environ.get(PLANTUML_ENV, DEFAULT_COMMAND))
    command += ["-tpng", puml_path]
    try:
        subprocess.run(command, check=True, capture_output=True)
    except OSError as error:
        raise RenderError(
            f"не удалось запустить PlantUML ({command[0]}): {error}"
        ) from None
    except subprocess.CalledProcessError as error:
        details = error.stderr.decode("utf-8", errors="replace").strip()
        raise RenderError(f"PlantUML завершился с ошибкой: {details}") \
            from None
    return os.path.splitext(puml_path)[0] + ".png"


def open_image(path):
    """Показать картинку в программе просмотра. Вернуть True при успехе."""
    if sys.platform.startswith("win"):
        os.startfile(path)
        return True
    opener = "open" if sys.platform == "darwin" else "xdg-open"
    try:
        subprocess.run([opener, path], check=True, capture_output=True)
    except (OSError, subprocess.CalledProcessError):
        return False
    return True
