"""Вычисление значений и констант на этапе трансляции."""

import math
import operator

from lark import Transformer
from lark.exceptions import VisitError


def finite_number(value):
    """Проверить, что число конечно."""
    if not math.isfinite(value):
        raise ValueError("Число вне допустимого диапазона")
    return value


def arithmetic(items, operation):
    """Вычислить бинарную арифметическую операцию."""
    left, right = items
    if not isinstance(left, float) or not isinstance(right, float):
        raise ValueError("Арифметика требует числовых операндов")
    return finite_number(operation(left, right))


class Evaluator(Transformer):
    """Преобразовать дерево разбора в вычисленные значения."""

    def __init__(self):
        """Создать отдельную таблицу констант."""
        super().__init__()
        self.constants = {}

    def start(self, items):
        """Вернуть итоговое значение без объявлений констант."""
        return items[-1]

    def number(self, items):
        """Преобразовать числовой литерал в число."""
        return finite_number(float(items[0]))

    def array(self, items):
        """Сформировать массив значений."""
        return list(items)

    def pair(self, items):
        """Сформировать пару ключа и значения."""
        name, value = items
        return str(name), value

    def dictionary(self, items):
        """Сформировать словарь и проверить уникальность ключей."""
        result = {}
        for name, value in items:
            if name in result:
                raise ValueError(f"Повторяющийся ключ: {name}")
            result[name] = value
        return result

    def definition(self, items):
        """Сохранить вычисленное значение константы."""
        name, value = items
        name = str(name)
        if name in self.constants:
            raise ValueError(f"Константа уже объявлена: {name}")
        self.constants[name] = value

    def reference(self, items):
        """Получить значение ранее объявленной константы."""
        name = str(items[0])
        if name not in self.constants:
            raise ValueError(f"Неизвестная константа: {name}")
        return self.constants[name]

    def add(self, items):
        """Вычислить сумму."""
        return arithmetic(items, operator.add)

    def subtract(self, items):
        """Вычислить разность."""
        return arithmetic(items, operator.sub)

    def sort_values(self, items):
        """Отсортировать числовой массив по возрастанию."""
        values = items[0]
        if not isinstance(values, list):
            raise ValueError("sort требует массив")
        if not all(isinstance(value, float) for value in values):
            raise ValueError("sort требует массив чисел")
        return sorted(values)


def evaluate(tree):
    """Вычислить дерево и раскрыть ошибки преобразования Lark."""
    try:
        return Evaluator().transform(tree)
    except VisitError as error:
        if isinstance(error.orig_exc, ValueError):
            raise error.orig_exc from error
        raise