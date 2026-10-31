
import subprocess
import tempfile
import time
from pathlib import Path


DOCKER_IMAGE = "self-correcting-python-sandbox:latest"


def run_pytest_in_docker(code, test_code, timeout_seconds=20):
    """
    Run user-provided Python tests inside a restricted Docker container.

    The solution and test files are mounted read-only.
    """

    if not isinstance(code, str) or not code.strip():
        return {
            "passed": False,
            "message": "Solution code must not be empty.",
            "stdout": "",
            "stderr": "Solution code must not be empty.",
            "return_code": None,
            "timed_out": False,
        }

    if not isinstance(test_code, str) or not test_code.strip():
        return {
            "passed": False,
            "message": "Test code must not be empty.",
            "stdout": "",
            "stderr": "Test code must not be empty.",
            "return_code": None,
            "timed_out": False,
        }

    if not isinstance(timeout_seconds, (int, float)) or timeout_seconds <= 0:
        return {
            "passed": False,
            "message": "Timeout must be a positive number.",
            "stdout": "",
            "stderr": "Timeout must be a positive number.",
            "return_code": None,
            "timed_out": False,
        }

    start_time = time.time()

    try:
        with tempfile.TemporaryDirectory(prefix="pytest_sandbox_") as temp_dir:
            workspace = Path(temp_dir)

            solution_file = workspace / "solution.py"
            test_file = workspace / "test_solution.py"

            solution_file.write_text(code, encoding="utf-8")
            test_file.write_text(test_code, encoding="utf-8")

            docker_command = [
                "docker",
                "run",
                "--rm",
                "--pull=never",
                "--network", "none",
                "--memory=256m",
                "--cpus=0.5",
                "--pids-limit=64",
                "--read-only",
                "--tmpfs", "/tmp:rw,nosuid,nodev,size=32m",
                "--cap-drop=ALL",
                "--security-opt=no-new-privileges",
                "--user", "10001:10001",
                "--mount",
                f"type=bind,source={temp_dir},target=/workspace,readonly",
                "--workdir", "/tmp",
                DOCKER_IMAGE,
                "python",
                "-I",
                "-m",
                "pytest",
                "-q",
                "-p",
                "no:cacheprovider",
                "/workspace/test_solution.py",
            ]

            result = subprocess.run(
                docker_command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout_seconds,
                check=False,
            )

            execution_time = round(time.time() - start_time, 4)

            passed = result.returncode == 0

            if passed:
                message = "All tests passed."
            elif result.returncode == 1:
                message = "One or more tests failed."
            else:
                message = "Pytest could not complete successfully."

            return {
                "passed": passed,
                "message": message,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "timed_out": False,
                "execution_time": execution_time,
            }

    except subprocess.TimeoutExpired:
        return {
            "passed": False,
            "message": f"Pytest timed out after {timeout_seconds} seconds.",
            "stdout": "",
            "stderr": "Test execution exceeded the allowed time.",
            "return_code": None,
            "timed_out": True,
            "execution_time": round(time.time() - start_time, 4),
        }

    except FileNotFoundError:
        return {
            "passed": False,
            "message": "Docker command was not found.",
            "stdout": "",
            "stderr": "Check your Docker installation and PATH.",
            "return_code": None,
            "timed_out": False,
            "execution_time": round(time.time() - start_time, 4),
        }

    except subprocess.SubprocessError as error:
        return {
            "passed": False,
            "message": "Docker test execution failed.",
            "stdout": "",
            "stderr": str(error),
            "return_code": None,
            "timed_out": False,
            "execution_time": round(time.time() - start_time, 4),
        }

    except OSError as error:
        return {
            "passed": False,
            "message": "A system error occurred.",
            "stdout": "",
            "stderr": str(error),
            "return_code": None,
            "timed_out": False,
            "execution_time": round(time.time() - start_time, 4),
        }
