
from core.docker_executor import execute_code_in_docker


print("=" * 55)
print("DOCKER CODE EXECUTOR TEST")
print("=" * 55)


# TEST 1: Normal Python code
print("\nTEST 1: Normal execution")

code = """
numbers = [10, 20, 30]
print(sum(numbers))
"""

result = execute_code_in_docker(code)

print("Success:", result["success"])
print("Output:", result["stdout"])
print("Execution time:", result["execution_time"])


# TEST 2: Python error
print("\nTEST 2: Error detection")

code = """
numbers = [10, 20, 30]
print(number)
"""

result = execute_code_in_docker(code)

print("Success:", result["success"])
print("Error type:", result["error_type"])
print("Error message:", result["error_message"])


# TEST 3: Network isolation
print("\nTEST 3: Network isolation")

code = """
import socket
socket.create_connection(("google.com", 80), timeout=2)
"""

result = execute_code_in_docker(code)

print("Success:", result["success"])
print("Error type:", result["error_type"])
print("Network access blocked:", not result["success"])


# TEST 4: Execution timeout
print("\nTEST 4: Timeout protection")

code = """
while True:
    pass
"""

result = execute_code_in_docker(code, timeout_seconds=3)

print("Success:", result["success"])
print("Timed out:", result["timed_out"])
print("Error:", result["error_message"])


print("\n" + "=" * 55)
print("DOCKER TESTING FINISHED")
print("=" * 55)
