
from core.code_executor import execute_code
from core.ai_debugger import analyze_error


def run_self_correction(code, max_attempts=3):
    """
    Execute Python code and use AI to fix errors automatically.

    max_attempts means the maximum number of AI correction attempts.
    """

    if not isinstance(code, str) or not code.strip():
        return {
            "success": False,
            "message": "No Python code was provided.",
            "attempts": 0,
            "final_code": code,
            "history": []
        }

    if not isinstance(max_attempts, int) or isinstance(max_attempts, bool) or max_attempts < 0:
        raise ValueError("max_attempts must be a non-negative integer.")

    current_code = code
    history = []

    # First execution: check the original code.
    execution_result = execute_code(current_code)

    if execution_result["success"]:
        return {
            "success": True,
            "message": "The original code executed successfully.",
            "attempts": 0,
            "final_code": current_code,
            "execution_result": execution_result,
            "history": history
        }

    # Try to fix the code using AI.
    for attempt in range(1, max_attempts + 1):

        print(f"\nAI correction attempt: {attempt}/{max_attempts}")

        # Ask the AI to analyze the execution error.
        ai_result = analyze_error(current_code, execution_result)

        if not ai_result.get("success"):
            history.append({
                "attempt": attempt,
                "status": "AI analysis failed",
                "error": ai_result.get("error", "Unknown AI error")
            })
            break

        report = ai_result["report"]
        corrected_code = report["corrected_code"]

        # Avoid repeatedly executing unchanged code.
        if not corrected_code.strip() or corrected_code.strip() == current_code.strip():
            history.append({
                "attempt": attempt,
                "status": "AI did not provide a new correction",
                "root_cause": report["root_cause"]
            })
            break

        # Execute the AI-generated correction.
        corrected_result = execute_code(corrected_code)

        history.append({
            "attempt": attempt,
            "status": "Fixed" if corrected_result["success"] else "Still failing",
            "root_cause": report["root_cause"],
            "explanation": report["explanation"],
            "changes": report["changes"],
            "corrected_code": corrected_code,
            "execution_result": corrected_result
        })

        current_code = corrected_code
        execution_result = corrected_result

        if execution_result["success"]:
            return {
                "success": True,
                "message": "Code was successfully corrected by AI.",
                "attempts": attempt,
                "final_code": current_code,
                "execution_result": execution_result,
                "history": history
            }

    return {
        "success": False,
        "message": "AI could not fix the code within the allowed attempts.",
        "attempts": len(history),
        "final_code": current_code,
        "execution_result": execution_result,
        "history": history
    }
