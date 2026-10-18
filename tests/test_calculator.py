
import pytest

from app.tools.calculator import calculate


def test_addition():
    assert calculate("10 + 5") == 15


def test_operator_precedence():
    assert calculate("10 + 5 * 2") == 20


def test_parentheses():
    assert calculate("(10 + 5) * 2") == 30


def test_division():
    assert calculate("(22 + 37) / 2") == 29.5


def test_division_by_zero():
    with pytest.raises(ValueError):
        calculate("10 / 0")


def test_rejects_python_code():
    with pytest.raises(ValueError):
        calculate("__import__('os').system('echo unsafe')")
