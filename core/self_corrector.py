
from core.code_executor import execute_code
from core.ai_debugger import analyze_error
from core.code_validator import validate_syntax, run_pytest


def check_candidate(code, test_code=None):
    """
    Validate code through syntax checking, execution,
    and optional automated tests.
    """

    syntax_result = validate_syntax(code)

    if not syntax_result["valid"]:
        error_message = syntax_result["error"]

        return {
            "success": False,
            "error": {
                "success": False,
                "error_type": "SyntaxError",
                "error_message": error_message,
                "stdout": "",
                "stderr": error_message
            },
            "validation": {
                "syntax": syntax_result,
                "execution": None,
                "tests": None
            }
        }

    execution_result = execute_code(code)

    if not execution_result["success"]:
        return {
            "success": False,
            "error": execution_result,
            "validation": {
                "syntax": syntax_result,
                "execution": execution_result,
                "tests": None
            }
        }

    test_result = None

    if test_code is not None:
        test_result = run_pytest(code, test_code)

        if not test_result["passed"]:
            test_error = {
                "success": False,
                "error_type": "TestFailure",
                "error_message": test_result["message"],
                "stdout": execution_result["stdout"],
                "stderr": (
                    test_result.get("stdout", "")
                    + "\n"
                    + test_result.get("stderr", "")
                )
            }

            return {
                "success": False,
                "error": test_error,
                "validation": {
                    "syntax": syntax_result,
                    "execution": execution_result,
                    "tests": test_result
                }
            }

    return {
        "success": True,
        "error": None,
        "validation": {
            "syntax": syntax_result,
            "execution": execution_result,
            "tests": test_result
        }
    }


def run_self_correction(code, max_attempts=3, test_code=None):
    """
    Automatically debug, correct, execute, and validate Python code.

    When test_code is provided, the correction must also pass pytest.
    """

    if not isinstance(code, str) or not code.strip():
        return {
            "success": False,
            "message": "No Python code was provided.",
            "attempts": 0,
            "final_code": code,
            "execution_result": None,
            "validation": None,
            "history": []
        }

    if (
        not isinstance(max_attempts, int)
        or isinstance(max_attempts, bool)
        or max_attempts < 0
    ):
        raise ValueError("max_attempts must be a non-negative integer.")

    current_code = code
    history = []

    # Check the original code before asking AI for help.
    candidate = check_candidate(current_code, test_code)

    if candidate["success"]:
        return {
            "success": True,
            "message": "The original code passed validation.",
            "attempts": 0,
            "final_code": current_code,
            "execution_result": candidate["validation"]["execution"],
            "validation": candidate["validation"],
            "history": history
        }

    current_error = candidate["error"]

    # AI correction loop.
    for attempt in range(1, max_attempts + 1):

        print(f"\nAI correction attempt: {attempt}/{max_attempts}")

        ai_result = analyze_error(current_code, current_error)

        if not ai_result.get("success"):
            history.append({
                "attempt": attempt,
                "status": "AI analysis failed",
                "error": ai_result.get("error", "Unknown AI error")
            })
            break

        report = ai_result["report"]
        corrected_code = report["corrected_code"]

        if (
            not isinstance(corrected_code, str)
            or not corrected_code.strip()
            or corrected_code.strip() == current_code.strip()
        ):
            history.append({
                "attempt": attempt,
                "status": "No new correction provided",
                "root_cause": report["root_cause"]
            })
            break

        # Validate the AI-generated code.
        candidate = check_candidate(corrected_code, test_code)

        if candidate["success"]:
            status = "Passed all supplied validation checks"
        else:
            status = "Validation failed"

        history.append({
            "attempt": attempt,
            "status": status,
            "root_cause": report["root_cause"],
            "explanation": report["explanation"],
            "changes": report["changes"],
            "corrected_code": corrected_code,
            "validation": candidate["validation"]
        })

        current_code = corrected_code

        if candidate["success"]:
            return {
                "success": True,
                "message": "AI-corrected code passed validation.",
                "attempts": attempt,
                "final_code": current_code,
                "execution_result": candidate["validation"]["execution"],
                "validation": candidate["validation"],
                "history": history
            }

        # Send the latest validation failure to the AI.
        current_error = candidate["error"]

    return {
        "success": False,
        "message": "Code could not pass validation within the allowed attempts.",
        "attempts": len(history),
        "final_code": current_code,
        "execution_result": candidate["validation"]["execution"],
        "validation": candidate["validation"],
        "history": history
    }
