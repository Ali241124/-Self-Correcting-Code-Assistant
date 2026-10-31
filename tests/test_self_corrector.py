
import core.self_corrector as self_corrector


def test_already_correct_code():
    code = """
x = 10
y = 20
print(x + y)
"""

    result = self_corrector.run_self_correction(code)

    assert result["success"] is True
    assert result["attempts"] == 0
    assert result["validation"]["syntax"]["valid"] is True


def test_ai_corrects_logical_error(monkeypatch):
    original_code = """
def add(a, b):
    return a - b

print(add(10, 20))
"""

    corrected_code = """
def add(a, b):
    return a + b

print(add(10, 20))
"""

    test_code = """
from solution import add

def test_add():
    assert add(10, 20) == 30

def test_negative_numbers():
    assert add(-5, -5) == -10
"""

    def fake_analyze_error(code, execution_result):
        return {
            "success": True,
            "report": {
                "root_cause": "The function uses subtraction instead of addition.",
                "explanation": "The function should add both arguments.",
                "corrected_code": corrected_code,
                "changes": ["Changed subtraction to addition."],
                "confidence": 0.99
            }
        }

    monkeypatch.setattr(
        self_corrector,
        "analyze_error",
        fake_analyze_error
    )

    result = self_corrector.run_self_correction(
        original_code,
        max_attempts=3,
        test_code=test_code
    )

    assert result["success"] is True
    assert result["attempts"] == 1
    assert "return a + b" in result["final_code"]
    assert result["validation"]["tests"]["passed"] is True


def test_zero_attempts_does_not_call_ai(monkeypatch):
    code = """
def add(a, b):
    return a - b
"""

    def unexpected_ai_call(code, execution_result):
        raise AssertionError("AI should not be called.")

    monkeypatch.setattr(
        self_corrector,
        "analyze_error",
        unexpected_ai_call
    )

    test_code = """
from solution import add

def test_add():
    assert add(10, 20) == 30
"""

    result = self_corrector.run_self_correction(
        code,
        max_attempts=0,
        test_code=test_code
    )

    assert result["success"] is False
    assert result["attempts"] == 0
