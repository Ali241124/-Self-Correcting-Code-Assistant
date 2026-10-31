
from core.self_corrector import run_self_correction


# Intentionally incorrect Python code
original_code = original_code = """
x = 10
y = 20
print(x + y)
"""


print("=" * 55)
print("SELF-CORRECTING CODE ASSISTANT")
print("=" * 55)

result = run_self_correction(
    code=original_code,
    max_attempts=3
)

print("\nFINAL RESULT")
print("=" * 55)

print("Success:", result["success"])
print("Message:", result["message"])
print("AI correction attempts:", result["attempts"])

print("\nFINAL CODE:")
print(result["final_code"])

print("\nPROGRAM OUTPUT:")
print(result["execution_result"]["stdout"])

if result["execution_result"]["stderr"]:
    print("\nERROR DETAILS:")
    print(result["execution_result"]["stderr"])

print("\nCORRECTION HISTORY:")
for item in result["history"]:
    print(f"\nAttempt {item['attempt']}: {item['status']}")

    if "root_cause" in item:
        print("Root cause:", item["root_cause"])

    if "explanation" in item:
        print("Explanation:", item["explanation"])
