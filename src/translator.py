"""Преобразование вычисленных значений в TOML."""

from src.evaluator import evaluate
from src.parser import parse_text


def format_value(value):
    """Записать число, массив или вложенный словарь в TOML."""
    if isinstance(value, dict):
        pairs = (
            f"{name} = {format_value(item)}"
            for name, item in value.items()
        )
        return "{" + ", ".join(pairs) + "}"
    if isinstance(value, list):
        items = (format_value(item) for item in value)
        return "[" + ", ".join(items) + "]"
    return repr(value)


def to_toml(value):
    """Сформировать документ TOML с корневыми ключами."""
    if not isinstance(value, dict):
        value = {"value": value}
    lines = [
        f"{name} = {format_value(item)}"
        for name, item in value.items()
    ]
    return "\n".join(lines) + "\n" if lines else ""


def translate(text):
    """Разобрать исходный текст и вернуть готовый TOML."""
    return to_toml(evaluate(parse_text(text)))