
import subprocess
import sys
import tempfile
import time
import re
from pathlib import Path


def extract_error_details(stderr):
    """
    Extract the error type and error message
    from Python's traceback.
    """

    if not stderr:
        return None, None

    lines = stderr.strip().splitlines()

    for line in reversed(lines):
        line = line.strip()

        match = re.match(
            r"^([A-Za-z_][\w.]*(?:Error|Exception|Interrupt|Exit)):\s*(.*)$",
            line
        )

        if match:
            return match.group(1), match.group(2)

    return "ExecutionError", lines[-1]


def execute_code(code, timeout_seconds=5):
    """
    Execute Python source code in a separate process.

    Returns execution status, output, errors,
    and execution duration.
    """

    if not isinstance(code, str) or not code.strip():
        return {
            "success": False,
            "stdout": "",
            "stderr": "",
            "error_type": "InputError",
            "error_message": "No Python code was provided.",
            "return_code": None,
            "execution_time": 0,
            "timed_out": False
        }

    if not isinstance(timeout_seconds, (int, float)) or isinstance(timeout_seconds, bool) or timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be a positive number.")

    start_time = time.perf_counter()

    try:
        with tempfile.TemporaryDirectory() as temp_dir:

            workspace = Path(temp_dir)
            script_path = workspace / "main.py"

            # Save submitted code into a temporary Python file.
            script_path.write_text(code, encoding="utf-8")

            try:
                result = subprocess.run(
                    [
                        sys.executable,
                        "-I",
                        str(script_path)
                    ],
                    cwd=workspace,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=timeout_seconds,
                    check=False
                )

                execution_time = round(
                    time.perf_counter() - start_time, 4
                )

                error_type, error_message = extract_error_details(
                    result.stderr
                )

                return {
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "error_type": error_type,
                    "error_message": error_message,
                    "return_code": result.returncode,
                    "execution_time": execution_time,
                    "timed_out": False
                }

            except subprocess.TimeoutExpired as error:

                execution_time = round(
                    time.perf_counter() - start_time, 4
                )

                def normalize_output(value):
                    if isinstance(value, bytes):
                        return value.decode("utf-8", errors="replace")
                    return value or ""

                return {
                    "success": False,
                    "stdout": normalize_output(error.stdout),
                    "stderr": normalize_output(error.stderr),
                    "error_type": "TimeoutError",
                    "error_message": (
                        f"Execution exceeded the {timeout_seconds}-second limit."
                    ),
                    "return_code": None,
                    "execution_time": execution_time,
                    "timed_out": True
                }

    except OSError as error:

        execution_time = round(
            time.perf_counter() - start_time, 4
        )

        return {
            "success": False,
            "stdout": "",
            "stderr": str(error),
            "error_type": "ExecutionError",
            "error_message": str(error),
            "return_code": None,
            "execution_time": execution_time,
            "timed_out": False
        }
