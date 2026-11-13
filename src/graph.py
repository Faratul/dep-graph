"""Построение графа зависимостей обходом в ширину (BFS) с рекурсией."""

START_DEPTH = 0


def is_excluded(name, substring):
    """Проверить, что пакет нужно пропустить из-за подстроки-фильтра."""
    return bool(substring) and substring in name


def build_graph(root, get_neighbors, max_depth, substring=""):
    """Построить граф зависимостей пакета ``root``.

    ``get_neighbors(имя)`` возвращает список зависимостей пакета.
    Обход идёт в ширину: рекурсивная функция ``visit_level`` обрабатывает
    один уровень графа и вызывает сама себя для следующего уровня.

    - ``max_depth`` — сколько уровней зависимостей разбирать;
    - пакеты, в имени которых есть ``substring``, не учитываются;
    - уже посещённый пакет повторно не разбирается, поэтому циклы
      не приводят к бесконечной рекурсии (ребро цикла в граф попадает).

    Возвращает словарь «пакет -> список зависимостей». Пакеты стоят
    в порядке обхода (по уровням).
    """
    graph = {root: []}
    visited = {root}

    def visit_level(level, depth):
        """Обработать пакеты одного уровня, затем следующий уровень."""
        if not level or depth >= max_depth:
            return
        next_level = []
        for name in level:
            children = [
                child for child in get_neighbors(name)
                if not is_excluded(child, substring)
            ]
            graph[name] = children
            for child in children:
                if child not in visited:
                    visited.add(child)
                    graph[child] = []
                    next_level.append(child)
        visit_level(next_level, depth + 1)

    visit_level([root], START_DEPTH)
    return graph
