"""Консольный интерфейс транслятора."""

import sys

from src.translator import translate


SUCCESS_CODE = 0
ERROR_CODE = 1


def main():
    """Прочитать stdin и вывести TOML или сообщение об ошибке."""
    try:
        result = translate(sys.stdin.read())
    except (ValueError, RecursionError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return ERROR_CODE
    sys.stdout.write(result)
    return SUCCESS_CODE


if __name__ == "__main__":
    raise SystemExit(main())