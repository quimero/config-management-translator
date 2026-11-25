"""Синтаксический анализ учебного языка."""

from pathlib import Path

from lark import Lark
from lark.exceptions import UnexpectedInput


FIRST_LINE = 1
GRAMMAR_PATH = Path(__file__).with_name("grammar.lark")
PARSER = Lark.open(str(GRAMMAR_PATH), parser="earley")


def parse_text(text):
    """Построить дерево разбора или сообщить о синтаксической ошибке."""
    try:
        return PARSER.parse(text)
    except UnexpectedInput as error:
        context = error.get_context(text).strip()
        if error.line < FIRST_LINE:
            message = "Синтаксическая ошибка: неожиданный конец ввода"
        else:
            message = (
                f"Синтаксическая ошибка: строка {error.line}, "
                f"столбец {error.column}"
            )
        raise ValueError(f"{message}\n{context}") from error