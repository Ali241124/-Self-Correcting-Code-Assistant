
from core.self_corrector import run_self_correction

original_code = """
def add(a, b):
    return a - b

print(add(10, 20))
"""

test_code = """
from solution import add

def test_add_positive_numbers():
    assert add(10, 20) == 30

def test_add_negative_numbers():
    assert add(-5, -5) == -10

def test_add_zero():
    assert add(10, 0) == 10
"""

print("=" * 55)
print("SELF-CORRECTING CODE ASSISTANT")
print("=" * 55)

result = run_self_correction(
    code=original_code,
    max_attempts=3,
    test_code=test_code
)

print("\nFINAL RESULT")
print("=" * 55)

print("Success:", result["success"])
print("Message:", result["message"])
print("Correction attempts:", result["attempts"])

print("\nFINAL CODE:")
print(result["final_code"])

print("\nPROGRAM OUTPUT:")

if result["execution_result"]:
    print(result["execution_result"]["stdout"])

print("\nVALIDATION RESULTS:")

print("Syntax:", result["validation"]["syntax"]["valid"])

if result["validation"]["execution"]:
    print("Execution:", result["validation"]["execution"]["success"])

if result["validation"]["tests"]:
    print("Automated tests:", result["validation"]["tests"]["message"])
    print(result["validation"]["tests"]["stdout"])

print("\nCORRECTION HISTORY:")

for item in result["history"]:
    print(f"\nAttempt {item['attempt']}: {item['status']}")

    if "root_cause" in item:
        print("Root cause:", item["root_cause"])
