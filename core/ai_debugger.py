
import json
import requests

from prompts.debugging_prompts import (
    SYSTEM_PROMPT,
    build_debugging_prompt
)


OLLAMA_API_URL = "http://localhost:11434/api/chat"

DEFAULT_MODEL = "qwen2.5-coder:1.5b"


def analyze_error(
    code,
    execution_result,
    model=DEFAULT_MODEL,
    base_url=OLLAMA_API_URL
):
    """
    Send Python code and execution errors to Ollama.

    Receive an AI-generated debugging report
    containing root cause, explanation, and corrected code.
    """

    # Check whether execution actually failed.
    if execution_result.get("success", False):
        return {
            "success": False,
            "error": "The submitted code did not produce an execution failure."
        }

    # Construct the debugging prompt.
    user_prompt = build_debugging_prompt(
        code,
        execution_result
    )

    # Prepare the Ollama API request.
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.1
        }
    }

    try:
        # Send request to local Ollama server.
        response = requests.post(
            base_url,
            json=payload,
            timeout=180
        )

        # Raise an exception if the API returns an HTTP error.
        response.raise_for_status()

        # Extract the model's response.
        response_data = response.json()

        ai_content = response_data["message"]["content"]

        # Convert JSON text into a Python dictionary.
        debugging_report = json.loads(ai_content)

        # Validate important response fields.
        required_fields = [
            "error_type",
            "root_cause",
            "explanation",
            "corrected_code",
            "changes",
            "confidence"
        ]

        for field in required_fields:
            if field not in debugging_report:
                raise ValueError(
                    f"AI response is missing the field: {field}"
                )

        if not isinstance(debugging_report["corrected_code"], str):
            raise ValueError("Corrected code must be a string.")

        if not isinstance(debugging_report["changes"], list):
            raise ValueError("Changes must be returned as a list.")

        if not isinstance(debugging_report["confidence"], (int, float)):
            raise ValueError("Confidence must be a number.")

        if not 0 <= debugging_report["confidence"] <= 1:
            raise ValueError("Confidence must be between 0 and 1.")

        # Return a structured debugging report.
        return {
            "success": True,
            "model": model,
            "report": debugging_report
        }

    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": (
                "Cannot connect to Ollama. "
                "Make sure the Ollama server is running."
            )
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Ollama request timed out."
        }

    except requests.exceptions.RequestException as error:
        return {
            "success": False,
            "error": f"Ollama API request failed: {error}"
        }

    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        return {
            "success": False,
            "error": f"Invalid AI response: {error}"
        }
