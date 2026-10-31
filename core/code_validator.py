
import ast
import subprocess
import sys
import tempfile
from pathlib import Path


def validate_syntax(code):
    """
    Check whether Python code has valid syntax.
    Does not execute the submitted code.
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


def run_pytest(code, test_code, timeout_seconds=15):
    """
    Run pytest tests against submitted Python code.

    The submitted code is saved as solution.py.
    The tests are saved as test_solution.py.

    Only use this with trusted code. This is not a secure sandbox.
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

    if not isinstance(timeout_seconds, (int, float)) or isinstance(timeout_seconds, bool) or timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be a positive number.")

    try:
        with tempfile.TemporaryDirectory() as temp_dir:

            project_path = Path(temp_dir)

            solution_path = project_path / "solution.py"
            test_path = project_path / "test_solution.py"

            solution_path.write_text(code, encoding="utf-8")
            test_path.write_text(test_code, encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "-q",
                    str(test_path)
                ],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout_seconds
            )

            passed = result.returncode == 0

            return {
                "passed": passed,
                "message": (
                    "All tests passed."
                    if passed
                    else "One or more tests failed."
                ),
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }

    except subprocess.TimeoutExpired:
        return {
            "passed": False,
            "message": "Test execution timed out.",
            "stdout": "",
            "stderr": f"Tests exceeded {timeout_seconds} seconds."
        }

    except OSError as error:
        return {
            "passed": False,
            "message": "Could not start the test process.",
            "stdout": "",
            "stderr": str(error)
        }
