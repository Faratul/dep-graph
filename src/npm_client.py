"""Получение зависимостей пакетов из репозитория npm по URL.

Используется только стандартная библиотека Python. Для каждого пакета
запрашивается документ ``<репозиторий>/<имя>/latest`` с описанием
последней версии, из него берётся поле ``dependencies``.
"""

import json
import urllib.error
import urllib.request
from urllib.parse import quote

from .errors import RepoError

REQUEST_TIMEOUT = 15
HTTP_NOT_FOUND = 404
REQUEST_HEADERS = {
    "User-Agent": "dep-graph/1.0",
    "Accept": "application/json",
}


def build_url(repo, name):
    """Собрать URL описания последней версии пакета."""
    return f"{repo.rstrip('/')}/{quote(name, safe='@')}/latest"


def fetch_manifest(repo, name):
    """Скачать описание пакета и вернуть его как словарь."""
    url = build_url(repo, name)
    request = urllib.request.Request(url, headers=REQUEST_HEADERS)
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as error:
        if error.code == HTTP_NOT_FOUND:
            raise RepoError(f"пакет не найден в репозитории: {name}") \
                from None
        raise RepoError(f"ошибка HTTP {error.code} для пакета {name}") \
            from None
    except OSError as error:
        raise RepoError(f"не удалось получить {url}: {error}") from None
    except ValueError:
        raise RepoError(f"ответ для пакета {name} не является JSON") \
            from None


def extract_dependencies(manifest):
    """Вернуть отсортированный список имён прямых зависимостей."""
    if not isinstance(manifest, dict):
        raise RepoError("описание пакета имеет неверный формат")
    dependencies = manifest.get("dependencies") or {}
    if not isinstance(dependencies, dict):
        raise RepoError("поле dependencies имеет неверный формат")
    return sorted(dependencies)


class NpmRepository:
    """Репозиторий пакетов npm, доступный по URL."""

    def __init__(self, url):
        """Запомнить URL репозитория."""
        self.url = url

    def get_dependencies(self, name):
        """Вернуть список прямых зависимостей пакета."""
        return extract_dependencies(fetch_manifest(self.url, name))

    def get_dependents(self, name):
        """Обратные зависимости: реестр npm их не отдаёт, это ошибка."""
        raise RepoError(
            f"реестр npm не позволяет найти пакеты, зависящие от {name}; "
            "используйте тестовый режим (--test-mode)"
        )
