"""Тесты синтаксиса, вычислений и формата TOML."""

import tomllib
import unittest

from src.translator import translate


class TranslatorTests(unittest.TestCase):
    """Проверка конструкций конфигурационного языка."""

    def test_numbers(self):
        """Проверить знаки, дробную часть и показатель степени."""
        text = "(list 1e2 -2.5E-1 +3.e+1 0e0)"
        expected = {"value": [100.0, -0.25, 30.0, 0.0]}
        self.assertEqual(tomllib.loads(translate(text)), expected)

    def test_comments(self):
        """Проверить комментарии обоих видов."""
        text = "C one\nbegin /+ two\nthree +/ a := 1e0; C four\nend"
        self.assertEqual(tomllib.loads(translate(text)), {"a": 1.0})

    def test_nested(self):
        """Проверить вложенные массивы и словари."""
        text = "begin a := (list (list 1e0) begin b := 2e0; end); end"
        expected = {"a": [[1.0], {"b": 2.0}]}
        self.assertEqual(tomllib.loads(translate(text)), expected)

    def test_nested_dictionary(self):
        """Проверить вложенность словарей."""
        text = "begin a := begin b := begin c := 3e0; end; end; end"
        expected = {"a": {"b": {"c": 3.0}}}
        self.assertEqual(tomllib.loads(translate(text)), expected)

    def test_empty(self):
        """Проверить пустые массивы и словари."""
        text = "begin a := (list); b := begin end; end"
        self.assertEqual(tomllib.loads(translate(text)), {"a": [], "b": {}})
        self.assertEqual(tomllib.loads(translate("begin end")), {})

    def test_names(self):
        """Проверить имена из строчных латинских букв."""
        text = "begin abc := 1e0; end := 2e0; end"
        expected = {"abc": 1.0, "end": 2.0}
        self.assertEqual(tomllib.loads(translate(text)), expected)

    def test_constant(self):
        """Проверить подстановку ранее объявленной константы."""
        text = "(define base 2e0) begin result := {base}; end"
        self.assertEqual(tomllib.loads(translate(text)), {"result": 2.0})

    def test_addition(self):
        """Проверить префиксное сложение."""
        text = "(define base 2e0) {+ base 3}"
        self.assertEqual(tomllib.loads(translate(text)), {"value": 5.0})

    def test_subtraction(self):
        """Проверить порядок операндов при вычитании."""
        self.assertEqual(tomllib.loads(translate("{- 2 5}")), {"value": -3.0})

    def test_nested_expressions(self):
        """Проверить вложенные выражения в объявлениях."""
        text = "(define a 2e0) (define b {+ a 3}) {- b {+ a 1}}"
        self.assertEqual(tomllib.loads(translate(text)), {"value": 2.0})

    def test_sort(self):
        """Проверить сортировку массива без изменения константы."""
        text = """(define a (list 3e0 -1e0 3e0 2e0))
        begin original := {a}; ordered := {sort a}; end"""
        expected = {"original": [3.0, -1.0, 3.0, 2.0],
                    "ordered": [-1.0, 2.0, 3.0, 3.0]}
        self.assertEqual(tomllib.loads(translate(text)), expected)

    def test_sort_literal(self):
        """Проверить сортировку литерала и пустого массива."""
        text = "begin a := {sort (list 2e0 1e0)}; b := {sort (list)}; end"
        self.assertEqual(tomllib.loads(translate(text)), {"a": [1.0, 2.0],
                                                          "b": []})

    def test_dictionary_constant(self):
        """Проверить словарь в константе и его подстановку."""
        text = "(define a begin b := 1e0; end) begin c := {a}; end"
        self.assertEqual(tomllib.loads(translate(text)), {"c": {"b": 1.0}})

    def test_root_number(self):
        """Проверить упаковку корневого числа в TOML."""
        self.assertEqual(tomllib.loads(translate("2e0")), {"value": 2.0})

    def test_syntax_errors(self):
        """Проверить отклонение неправильных конструкций."""
        samples = (
            "", "begin a := 1e0 end", "begin a := 1e0;",
            "begin a1 := 1e0; end", "begin A := 1e0; end",
            "begin a_b := 1e0; end", "begin a := 1; end",
            "begin a := 1.5; end", "begin a := .5e0; end",
            "begin a := 1e; end", "(list 1e0, 2e0)",
            "(list 1e0", "begin a = 1e0; end", '"text"',
            "{+ 1}", "{+ 1 2 3}", "{* 1 2}", "{sort}",
            "(define a 1e0)", "/+ unclosed", "1e0 2e0",
        )
        for text in samples:
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    translate(text)

    def test_semantic_errors(self):
        """Проверить ошибки вычисления и повторные объявления."""
        samples = (
            "{+ missing 1}", "(define a 1e0) (define a 2e0) {a}",
            "begin a := 1e0; a := 2e0; end", "{+ (list) 1}",
            "{- 1 begin end}", "{sort 1e0}",
            "{sort (list begin end)}", "1e999", "{+ 1e308 1e308}",
            "(define a {b}) (define b 1e0) {a}",
        )
        for text in samples:
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    translate(text)