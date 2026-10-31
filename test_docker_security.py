
from core.docker_executor import execute_code_in_docker


print("=" * 55)
print("DOCKER SANDBOX SECURITY TESTS")
print("=" * 55)


# TEST 1: Workspace must be read-only
print("\nTEST 1: Workspace write restriction")

code = """
from pathlib import Path

Path("/workspace/hacked.txt").write_text("This should not work")
print("Write succeeded")
"""

result = execute_code_in_docker(code)

print("Execution successful:", result["success"])
print("Write blocked:", not result["success"])
print("Error:", result["error_type"], result["error_message"])


# TEST 2: Network must be unavailable
print("\nTEST 2: Network restriction")

code = """
import socket

socket.create_connection(("1.1.1.1", 80), timeout=2)
print("Network connection succeeded")
"""

result = execute_code_in_docker(code)

print("Execution successful:", result["success"])
print("Network blocked:", not result["success"])
print("Error:", result["error_type"])


# TEST 3: Temporary directory should be writable
print("\nTEST 3: Temporary directory")

code = """
from pathlib import Path

path = Path("/tmp/test_file.txt")
path.write_text("Temporary file works")

print(path.read_text())
"""

result = execute_code_in_docker(code)

print("Execution successful:", result["success"])
print("Output:", result["stdout"])


# TEST 4: Timeout protection
print("\nTEST 4: Infinite loop protection")

code = """
while True:
    pass
"""

result = execute_code_in_docker(code, timeout_seconds=3)

print("Execution successful:", result["success"])
print("Timeout triggered:", result["timed_out"])


print("\n" + "=" * 55)
print("SECURITY TESTING FINISHED")
print("=" * 55)
