
from core.code_executor import execute_code
from core.ai_debugger import analyze_error


# Example program containing a NameError.
original_code = """
numbers = [10, 20, 30]

print(number)
"""

print("=" * 60)
print("SELF-CORRECTING CODE ASSISTANT")
print("=" * 60)

# STEP 1: Execute original code.
print("\n[1] Executing original code...")

execution_result = execute_code(original_code)

print("Execution successful:", execution_result["success"])

# STEP 2: Display detected error.
if not execution_result["success"]:

    print("\n[2] Error detected!")
    print("Error type:", execution_result["error_type"])
    print("Error message:", execution_result["error_message"])

    # STEP 3: Ask AI to analyze the error.
    print("\n[3] Sending code to Qwen 2.5 7B...")

    ai_result = analyze_error(
        original_code,
        execution_result
    )

    # STEP 4: Display AI debugging report.
    if ai_result["success"]:

        report = ai_result["report"]

        print("\n[4] AI DEBUGGING REPORT")
        print("-" * 60)

        print("\nRoot cause:")
        print(report["root_cause"])

        print("\nExplanation:")
        print(report["explanation"])

        print("\nCorrected code:")
        print(report["corrected_code"])

        print("\nChanges:")
        for change in report["changes"]:
            print("-", change)

        print("\nAI confidence:", report["confidence"])

    else:
        print("\nAI debugging failed:")
        print(ai_result["error"])

else:
    print("\nNo errors detected. AI debugging is not required.")
