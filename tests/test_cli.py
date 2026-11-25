"""Интеграционные тесты консольного интерфейса и примеров."""

import subprocess
import sys
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUCCESS_CODE = 0
ERROR_CODE = 1


def run_cli(text):
    """Запустить CLI с исходным текстом через stdin."""
    return subprocess.run(
        [sys.executable, "-X", "utf8", "-m", "src.main"],
        input=text,
        capture_output=True,
        encoding="utf-8",
        cwd=ROOT,
        check=False,
    )


class CliTests(unittest.TestCase):
    """Проверка потоков ввода и вывода и примеров."""

    def check_example(self, filename, expected):
        """Проверить результат трансляции файла примера."""
        path = ROOT / "examples" / filename
        result = run_cli(path.read_text(encoding="utf-8"))
        self.assertEqual(result.returncode, SUCCESS_CODE)
        self.assertEqual(result.stderr, "")
        self.assertEqual(tomllib.loads(result.stdout), expected)

    def test_server(self):
        """Проверить конфигурацию веб-сервера."""
        expected = {"server": {"port": 8080.0, "timeout": 30.0},
                    "limits": [100.0, 300.0, 500.0]}
        self.check_example("server.cfg", expected)

    def test_warehouse(self):
        """Проверить конфигурацию склада."""
        expected = {
            "available": 1000.0,
            "warehouse": {
                "capacity": 2000.0,
                "zones": [{"capacity": 800.0}, {"capacity": 1200.0}],
            },
        }
        self.check_example("warehouse.cfg", expected)

    def test_syntax_error(self):
        """Проверить ненулевой код и вывод ошибки в stderr."""
        result = run_cli("begin a := 1e0 end")
        self.assertEqual(result.returncode, ERROR_CODE)
        self.assertEqual(result.stdout, "")
        self.assertIn("Синтаксическая ошибка", result.stderr)

    def test_semantic_error(self):
        """Проверить сообщение о неизвестной константе."""
        result = run_cli("{+ missing 1}")
        self.assertEqual(result.returncode, ERROR_CODE)
        self.assertEqual(result.stdout, "")
        self.assertIn("Неизвестная константа", result.stderr)