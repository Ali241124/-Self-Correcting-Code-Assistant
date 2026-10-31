
from core.code_validator import validate_syntax, run_pytest


def test_valid_syntax():
    code = """
x = 10
print(x)
"""

    result = validate_syntax(code)

    assert result["valid"] is True


def test_invalid_syntax():
    code = """
if True
    print("Hello")
"""

    result = validate_syntax(code)

    assert result["valid"] is False
    assert "SyntaxError" in result["error"]


def test_empty_code():
    result = validate_syntax("")

    assert result["valid"] is False


def test_pytest_success():
    code = """
def add(a, b):
    return a + b
"""

    test_code = """
from solution import add

def test_add():
    assert add(10, 20) == 30

def test_add_negative():
    assert add(-5, 5) == 0
"""

    result = run_pytest(code, test_code)

    assert result["passed"] is True


def test_pytest_failure():
    code = """
def add(a, b):
    return a - b
"""

    test_code = """
from solution import add

def test_add():
    assert add(10, 20) == 30
"""

    result = run_pytest(code, test_code)

    assert result["passed"] is False
    assert "failed" in result["message"].lower()
