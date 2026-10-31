
from core.code_executor import execute_code


def test_successful_execution():
    code = """
print("Hello AI Assistant")
print(10 + 20)
"""

    result = execute_code(code)

    assert result["success"] is True
    assert "Hello AI Assistant" in result["stdout"]
    assert "30" in result["stdout"]


def test_zero_division_error():
    code = """
x = 10
y = 0
print(x / y)
"""

    result = execute_code(code)

    assert result["success"] is False
    assert result["error_type"] == "ZeroDivisionError"
    assert "division by zero" in result["error_message"]


def test_name_error():
    code = """
numbers = [10, 20, 30]
print(number)
"""

    result = execute_code(code)

    assert result["success"] is False
    assert result["error_type"] == "NameError"


def test_syntax_error():
    code = """
if True
    print("Hello")
"""

    result = execute_code(code)

    assert result["success"] is False
    assert result["error_type"] == "SyntaxError"


def test_execution_timeout():
    code = """
while True:
    pass
"""

    result = execute_code(code, timeout_seconds=1)

    assert result["success"] is False
    assert result["timed_out"] is True
    assert result["error_type"] == "TimeoutError"


def test_empty_code():
    result = execute_code("")

    assert result["success"] is False
    assert result["error_type"] == "InputError"
