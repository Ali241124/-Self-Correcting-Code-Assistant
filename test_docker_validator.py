
from core.docker_validator import run_pytest_in_docker


print("=" * 55)
print("DOCKER PYTEST VALIDATOR TEST")
print("=" * 55)


# TEST 1: Correct solution
print("\nTEST 1: All tests should pass")

solution = """
def add(a, b):
    return a + b
"""

tests = """
from solution import add


def test_positive_numbers():
    assert add(10, 20) == 30


def test_negative_numbers():
    assert add(-5, -5) == -10


def test_zero():
    assert add(0, 10) == 10
"""

result = run_pytest_in_docker(solution, tests)

print("Passed:", result["passed"])
print("Message:", result["message"])
print("Output:")
print(result["stdout"])
print("Execution time:", result["execution_time"])


# TEST 2: Incorrect solution
print("\nTEST 2: Incorrect solution should fail")

solution = """
def add(a, b):
    return a - b
"""

result = run_pytest_in_docker(solution, tests)

print("Passed:", result["passed"])
print("Message:", result["message"])
print("Output:")
print(result["stdout"])


print("\n" + "=" * 55)
print("DOCKER PYTEST TESTING FINISHED")
print("=" * 55)
