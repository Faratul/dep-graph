"""Тесты инструмента визуализации зависимостей."""

import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def data_path(name):
    """Вернуть путь к файлу тестового репозитория."""
    return os.path.join(DATA_DIR, name)
