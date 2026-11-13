"""Вывод графа зависимостей в виде ASCII-дерева."""

BRANCH = "|-- "
LAST_BRANCH = "`-- "
PIPE = "|   "
SPACE = "    "
REPEAT_MARK = " (уже показан выше)"


def add_children(graph, name, prefix, shown, lines):
    """Добавить в ``lines`` строки дерева для зависимостей пакета.

    Пакет, который уже был показан выше (повтор или цикл), повторно
    не раскрывается, поэтому дерево всегда конечное.
    """
    children = graph.get(name, [])
    for child in children:
        is_last = child == children[-1]
        branch, extension = (LAST_BRANCH, SPACE) if is_last else (BRANCH, PIPE)
        if child in shown:
            mark = REPEAT_MARK if graph.get(child) else ""
            lines.append(f"{prefix}{branch}{child}{mark}")
            continue
        shown.add(child)
        lines.append(f"{prefix}{branch}{child}")
        add_children(graph, child, prefix + extension, shown, lines)


def build_tree_lines(graph, root):
    """Вернуть строки ASCII-дерева зависимостей пакета ``root``."""
    lines = [root]
    add_children(graph, root, "", {root}, lines)
    return lines
