
import ast

from core.docker_validator import run_pytest_in_docker


def validate_syntax(code):
    """
    Check Python syntax without executing submitted code.
    """

    if not isinstance(code, str) or not code.strip():
        return {
            "valid": False,
            "error": "No Python code was provided."
        }

    try:
        ast.parse(code)

        return {
            "valid": True,
            "error": None
        }

    except SyntaxError as error:
        return {
            "valid": False,
            "error": f"{error.__class__.__name__}: {error.msg}",
            "line": error.lineno
        }


def run_pytest(code, test_code, timeout_seconds=20):
    """
    Run pytest inside the restricted Docker sandbox.

    Preserves the existing run_pytest() interface.
    """

    syntax_result = validate_syntax(code)

    if not syntax_result["valid"]:
        return {
            "passed": False,
            "message": "Code contains a syntax error.",
            "stdout": "",
            "stderr": syntax_result["error"]
        }

    if not isinstance(test_code, str) or not test_code.strip():
        return {
            "passed": False,
            "message": "No test code was provided.",
            "stdout": "",
            "stderr": ""
        }

    if (
        not isinstance(timeout_seconds, (int, float))
        or isinstance(timeout_seconds, bool)
        or timeout_seconds <= 0
    ):
        raise ValueError("timeout_seconds must be a positive number.")

    return run_pytest_in_docker(
        code=code,
        test_code=test_code,
        timeout_seconds=timeout_seconds
    )
