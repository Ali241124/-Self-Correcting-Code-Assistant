
import subprocess
import tempfile
import time
import re
import uuid
from pathlib import Path


DOCKER_IMAGE = "python:3.11-slim"


def extract_error_details(stderr):
    """
    Extract the Python error type and message from traceback output.
    """
    if not stderr:
        return None, None

    lines = stderr.strip().splitlines()

    for line in reversed(lines):
        match = re.match(
            r"^([A-Za-z_][A-Za-z0-9_.]*Error|Exception|SystemExit):\s*(.*)$",
            line.strip()
        )

        if match:
            return match.group(1), match.group(2)

    return "ExecutionError", lines[-1] if lines else "Unknown error"


def execute_code_in_docker(code, timeout_seconds=5):
    """
    Execute Python code inside a restricted Docker container.

    Security features:
    - No network access
    - Non-root user
    - Read-only root filesystem
    - Read-only submitted source file
    - Limited memory and CPU
    - Limited process count
    - Dropped Linux capabilities
    - Host-side execution timeout
    """

    # 1. Validate submitted code
    if not isinstance(code, str) or not code.strip():
        return {
            "success": False,
            "stdout": "",
            "stderr": "No Python code was provided.",
            "error_type": "InputError",
            "error_message": "No Python code was provided.",
            "return_code": None,
            "execution_time": 0,
            "timed_out": False,
        }

    # 2. Validate timeout
    if (
        not isinstance(timeout_seconds, (int, float))
        or isinstance(timeout_seconds, bool)
        or timeout_seconds <= 0
    ):
        return {
            "success": False,
            "stdout": "",
            "stderr": "Timeout must be a positive number.",
            "error_type": "ValueError",
            "error_message": "Timeout must be a positive number.",
            "return_code": None,
            "execution_time": 0,
            "timed_out": False,
        }

    start_time = time.time()
    container_label = f"self-correcting-run-{uuid.uuid4().hex}"

    try:
        with tempfile.TemporaryDirectory(prefix="code_sandbox_") as temp_dir:

            # 3. Save submitted Python code in a temporary directory
            host_script = Path(temp_dir) / "submission.py"
            host_script.write_text(code, encoding="utf-8")

            # 4. Configure restricted Docker execution
            docker_command = [
                "docker",
                "run",
                "--rm",
                "--pull=never",
                "--label", container_label,
                "--network", "none",
                "--memory=128m",
                "--cpus=0.5",
                "--pids-limit=64",
                "--read-only",
                "--tmpfs", "/tmp:rw,nosuid,nodev,size=16m",
                "--cap-drop=ALL",
                "--security-opt=no-new-privileges",
                "--user", "10001:10001",
                "--mount",
                f"type=bind,source={temp_dir},target=/workspace,readonly",
                "--workdir", "/tmp",
                DOCKER_IMAGE,
                "python",
                "-I",
                "/workspace/submission.py",
            ]

            # 5. Execute code inside Docker
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
                "timed_out": False,
            }

    # 6. Handle execution timeout
    except subprocess.TimeoutExpired:

        # Attempt to stop the container if it is still running
        try:
            containers = subprocess.run(
                [
                    "docker",
                    "ps",
                    "-q",
                    "--filter",
                    f"label={container_label}",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            for container_id in containers.stdout.splitlines():
                subprocess.run(
                    ["docker", "stop", "--time", "1", container_id],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

        except (subprocess.SubprocessError, OSError):
            pass

        return {
            "success": False,
            "stdout": "",
            "stderr": f"Execution timed out after {timeout_seconds} seconds.",
            "error_type": "TimeoutError",
            "error_message": f"Execution exceeded {timeout_seconds} seconds.",
            "return_code": None,
            "execution_time": round(time.time() - start_time, 4),
            "timed_out": True,
        }

    # 7. Handle missing Docker installation
    except FileNotFoundError:
        return {
            "success": False,
            "stdout": "",
            "stderr": "Docker command was not found. Check your Docker installation.",
            "error_type": "DockerNotFound",
            "error_message": "Docker command was not found.",
            "return_code": None,
            "execution_time": round(time.time() - start_time, 4),
            "timed_out": False,
        }

    # 8. Handle Docker-related errors
    except subprocess.SubprocessError as error:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(error),
            "error_type": "DockerExecutionError",
            "error_message": str(error),
            "return_code": None,
            "execution_time": round(time.time() - start_time, 4),
            "timed_out": False,
        }

    # 9. Handle operating-system errors
    except OSError as error:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(error),
            "error_type": "SystemError",
            "error_message": str(error),
            "return_code": None,
            "execution_time": round(time.time() - start_time, 4),
            "timed_out": False,
        }
