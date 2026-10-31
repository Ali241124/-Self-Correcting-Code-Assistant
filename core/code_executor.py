
from core.docker_executor import execute_code_in_docker


def execute_code(code, timeout_seconds=5):
    """
    Execute Python code inside the restricted Docker sandbox.

    Keeps the original execute_code() interface so the
    self-correction engine and dashboard remain compatible.
    """

    return execute_code_in_docker(
        code=code,
        timeout_seconds=timeout_seconds
    )
