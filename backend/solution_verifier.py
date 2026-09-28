import os
import json
from typing import Any, Dict

from dotenv import load_dotenv

load_dotenv()


# =========================================================
# CONFIGURATION
# =========================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

GEMINI_MODEL = "gemini-3.6-flash"
GROQ_MODEL = "qwen/qwen3.6-27b"
OPENROUTER_MODEL = "openrouter/free"
HF_MODEL = "swiss-ai/Apertus-v1.5-8B:publicai"


# =========================================================
# VERIFIER PROMPT
# =========================================================

VERIFIER_PROMPT = """
You are the Solution Verification Agent of SolveCast AI.

Your job is to verify whether the generated solution correctly solves
the given question.

Check carefully:

1. Is the interpretation of the question correct?
2. Are formulas correct?
3. Are calculations correct?
4. Are mathematical operations correct?
5. Are units correct where applicable?
6. Are logical steps correct?
7. Is the final answer consistent with the steps?
8. Did the solution skip a necessary step?
9. For programming questions, check the algorithm and logic.
10. Do NOT mark a solution wrong only because the wording is different.

Return ONLY valid JSON.

Required format:

{{
    "valid": true,
    "errors": [],
    "warnings": [],
    "corrected_solution": null
}}

If the solution is incorrect:

{{
    "valid": false,
    "errors": [
        "Specific error 1",
        "Specific error 2"
    ],
    "warnings": [],
    "corrected_solution": "A corrected solution"
}}

Rules:

- valid must be true or false.
- errors must contain only actual correctness problems.
- warnings are minor issues that do not make the answer incorrect.
- corrected_solution should be provided only when the solution needs correction.
- Do not invent errors.
- Be strict about calculations and formulas.
- Return JSON only.

QUESTION:
{question}

GENERATED SOLUTION:
{solution}
"""


# =========================================================
# CLEAN JSON RESPONSE
# =========================================================

def clean_json_response(text: str) -> Dict[str, Any]:

    if not text:
        raise ValueError("Empty verifier response.")

    text = text.strip()

    # Remove markdown code fences
    if text.startswith("```"):

        lines = text.splitlines()

        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    # Find first { and last }
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError(
            "No valid JSON object found in verifier response."
        )

    text = text[start:end + 1]

    try:
        data = json.loads(text)

    except json.JSONDecodeError as e:
        raise ValueError(
            f"Invalid JSON from verifier: {e}"
        )

    if not isinstance(data, dict):
        raise ValueError(
            "Verifier response is not a JSON object."
        )

    return data


# =========================================================
# NORMALIZE RESULT
# =========================================================

def normalize_result(
    data: Dict[str, Any]
) -> Dict[str, Any]:

    valid = data.get("valid", False)

    # Convert string true/false to boolean
    if isinstance(valid, str):

        valid = valid.strip().lower() == "true"

    errors = data.get("errors", [])
    warnings = data.get("warnings", [])
    corrected_solution = data.get(
        "corrected_solution"
    )

    # Make sure errors is a list
    if not isinstance(errors, list):

        errors = [str(errors)]

    # Make sure warnings is a list
    if not isinstance(warnings, list):

        warnings = [str(warnings)]

    return {
        "valid": bool(valid),
        "errors": errors,
        "warnings": warnings,
        "corrected_solution": corrected_solution
    }


# =========================================================
# GEMINI VERIFIER
# =========================================================

def verify_with_gemini(
    prompt: str
) -> Dict[str, Any]:

    if not GEMINI_API_KEY:

        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    from google import genai

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json"
        }
    )

    if not response.text:

        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return clean_json_response(
        response.text
    )


# =========================================================
# GROQ VERIFIER
# =========================================================

def verify_with_groq(
    prompt: str
) -> Dict[str, Any]:

    if not GROQ_API_KEY:

        raise RuntimeError(
            "GROQ_API_KEY is not configured."
        )

    from groq import Groq

    client = Groq(
        api_key=GROQ_API_KEY
    )

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
        response_format={
            "type": "json_object"
        }
    )

    content = response.choices[0].message.content

    if not content:

        raise RuntimeError(
            "Groq returned an empty response."
        )

    return clean_json_response(
        content
    )


# =========================================================
# OPENROUTER VERIFIER
# =========================================================

def verify_with_openrouter(
    prompt: str
) -> Dict[str, Any]:

    if not OPENROUTER_API_KEY:

        raise RuntimeError(
            "OPENROUTER_API_KEY is not configured."
        )

    from openai import OpenAI

    client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1"
    )

    response = client.chat.completions.create(
        model=OPENROUTER_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
        response_format={
            "type": "json_object"
        }
    )

    content = response.choices[0].message.content

    if not content:

        raise RuntimeError(
            "OpenRouter returned an empty response."
        )

    return clean_json_response(
        content
    )


# =========================================================
# HUGGING FACE VERIFIER
# =========================================================

def verify_with_huggingface(
    prompt: str
) -> Dict[str, Any]:

    if not HF_TOKEN:

        raise RuntimeError(
            "HF_TOKEN is not configured."
        )

    from huggingface_hub import InferenceClient

    client = InferenceClient(
        provider="auto",
        api_key=HF_TOKEN
    )

    response = client.chat_completion(
        model=HF_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    content = response.choices[0].message.content

    if not content:

        raise RuntimeError(
            "Hugging Face returned an empty response."
        )

    return clean_json_response(
        content
    )


# =========================================================
# MAIN SOLUTION VERIFIER
# =========================================================

def verify_solution(
    question: str,
    solution: Any
) -> Dict[str, Any]:

    # -----------------------------------------------------
    # Check question
    # -----------------------------------------------------

    if not question or not question.strip():

        return {
            "valid": False,
            "errors": [
                "Question is empty."
            ],
            "warnings": [],
            "corrected_solution": None,
            "provider": None
        }

    # -----------------------------------------------------
    # Convert solution to text
    # -----------------------------------------------------

    if isinstance(solution, dict):

        solution_text = json.dumps(
            solution,
            ensure_ascii=False,
            indent=2
        )

    else:

        solution_text = str(solution)

    # -----------------------------------------------------
    # Create verifier prompt
    # -----------------------------------------------------

    try:

        prompt = VERIFIER_PROMPT.format(
            question=question,
            solution=solution_text
        )

    except Exception as e:

        return {
            "valid": False,
            "errors": [
                f"Failed to create verifier prompt: {str(e)}"
            ],
            "warnings": [],
            "corrected_solution": None,
            "provider": None
        }

    # -----------------------------------------------------
    # Provider fallback
    # -----------------------------------------------------

    providers = [
        (
            "gemini",
            verify_with_gemini
        ),
        (
            "groq",
            verify_with_groq
        ),
        (
            "openrouter",
            verify_with_openrouter
        ),
        (
            "huggingface",
            verify_with_huggingface
        )
    ]

    provider_errors = []

    # -----------------------------------------------------
    # Try providers
    # -----------------------------------------------------

    for provider_name, provider_function in providers:

        try:

            print(
                f"\nSolution verifier:"
                f" trying {provider_name}..."
            )

            result = provider_function(
                prompt
            )

            result = normalize_result(
                result
            )

            result["provider"] = provider_name

            print(
                f"Solution verifier:"
                f" {provider_name} success."
            )

            return result

        except Exception as e:

            error_message = str(e)

            provider_errors.append(
                f"{provider_name}: {error_message}"
            )

            print(
                f"Solution verifier:"
                f" {provider_name} failed."
            )

            print(
                f"Error: {error_message}"
            )

    # -----------------------------------------------------
    # All providers failed
    # -----------------------------------------------------

    return {
        "valid": False,
        "errors": [
            "All verification providers failed."
        ],
        "warnings": provider_errors,
        "corrected_solution": None,
        "provider": None
    }


# =========================================================
# STANDALONE TEST
# =========================================================

if __name__ == "__main__":

    print("\n")
    print("=" * 60)
    print("SolveCast AI - Solution Verification Agent")
    print("=" * 60)

    test_question = """
Solve the equation:

2x + 5 = 15
"""

    test_solution = """
2x + 5 = 15

2x = 15 - 5

2x = 10

x = 10 / 2

x = 5

Final Answer: x = 5
"""

    print("\nQuestion:")
    print(test_question)

    print("\nGenerated Solution:")
    print(test_solution)

    print("\nRunning verification...")

    result = verify_solution(
        question=test_question,
        solution=test_solution
    )

    print("\n")
    print("=" * 60)
    print("VERIFICATION RESULT")
    print("=" * 60)

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )

    print("=" * 60)
    