
from database.history import (
    initialize_database,
    save_run,
    get_recent_runs,
    get_run_by_id,
    delete_run
)

# Initialize the database
initialize_database()

# Sample debugging result
sample_result = {
    "success": True,
    "message": "AI-corrected code passed validation.",
    "attempts": 1,
    "final_code": "def add(a, b):\n    return a + b\n\nprint(add(10, 20))",
    "execution_result": {
        "stdout": "30\n"
    },
    "validation": {
        "syntax": {"valid": True},
        "execution": {"success": True},
        "tests": {"passed": True}
    },
    "history": [
        {
            "attempt": 1,
            "status": "Passed all supplied validation checks",
            "root_cause": "Subtraction was used instead of addition."
        }
    ]
}

original_code = """
def add(a, b):
    return a - b

print(add(10, 20))
"""

# 1. Save a debugging session
run_id = save_run(
    original_code=original_code,
    result=sample_result,
    test_code="def test_add(): assert add(10, 20) == 30"
)

print("Saved session ID:", run_id)

# 2. Retrieve recent sessions
runs = get_recent_runs()

print("\nRecent sessions:")

for run in runs:
    print(
        run["id"],
        run["success"],
        run["message"]
    )

# 3. Retrieve one session
saved_run = get_run_by_id(run_id)

print("\nRetrieved session:")
print("Original code:", saved_run["original_code"])
print("Corrected code:", saved_run["final_code"])

# 4. Delete the test session
deleted = delete_run(run_id)

print("\nSession deleted:", deleted)
