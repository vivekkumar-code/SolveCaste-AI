# ============================================================
# SolveCast AI - FastAPI Backend
# Phase 1
# Solver + Vision + Diagram Agent + Verifier + Doubt
# ============================================================

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from google import genai
from groq import Groq
from openai import OpenAI

from dotenv import load_dotenv

import os
import json
import base64
from typing import Any, Dict

# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# API KEYS
# ============================================================

GEMINI_API_KEY = (
    os.getenv("GEMINI_API_KEY")
    or os.getenv("GOOGLE_API_KEY")
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)

HF_TOKEN = os.getenv("HF_TOKEN")


# ============================================================
# CLIENTS
# ============================================================

gemini_client = (
    genai.Client(
        api_key=GEMINI_API_KEY
    )
    if GEMINI_API_KEY
    else None
)

groq_client = (
    Groq(
        api_key=GROQ_API_KEY
    )
    if GROQ_API_KEY
    else None
)

openrouter_client = (
    OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY
    )
    if OPENROUTER_API_KEY
    else None
)

hf_client = (
    OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=HF_TOKEN
    )
    if HF_TOKEN
    else None
)


# ============================================================
# MODELS
# ============================================================

GEMINI_MODEL = "gemini-3.6-flash"

GROQ_MODEL = "qwen/qwen3.6-27b"

OPENROUTER_MODEL = "openrouter/free"

HF_MODEL = "swiss-ai/Apertus-v1.5-8B:publicai"


# ============================================================
# DIAGRAM MODULES
# ============================================================

from diagram_agent import (
    analyze_diagram,
    improve_diagram
)

from diagram_validator import (
    validate_diagram_plan
)

from diagram_renderer import (
    render_diagram
)


# ============================================================
# SOLUTION VERIFIER
# ============================================================

from solution_verifier import (
    verify_solution
)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="SolveCast AI API",
    version="3.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "https://solve-caste-ai.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "message": "SolveCast AI API is running",
        "version": "3.0.0"
    }


# ============================================================
# SOLUTION PROMPT
# ============================================================

SOLUTION_PROMPT = r"""
You are SolveCast AI, an intelligent academic question solving assistant.

Your job is to solve the given academic question accurately.

============================================================
STYLE
============================================================

1. Solve like a student writing in a notebook.

2. Use minimum English.

3. Use mathematical operations wherever possible.

4. Explain step-by-step.

5. Do not skip important calculations.

6. Do not invent information.

7. Keep the solution easy to understand.

8. Use simple mathematical notation.

9. Do not use unnecessary explanations.

10. The final answer must be clearly visible.

============================================================
GENERAL ACADEMIC SUPPORT
============================================================

The question can belong to:

- Mathematics
- Physics
- Chemistry
- Biology
- Computer Science
- Data Structures
- Algorithms
- Engineering
- Electronics
- Statistics
- General academics

Solve according to the subject.

============================================================
DIAGRAM
============================================================

Do NOT generate the diagram yourself.

Only determine whether a diagram may be useful.

Set:

diagram_required = true

when a meaningful diagram is required.

Otherwise:

diagram_required = false

diagram_type = "none"

The actual diagram will be generated separately
by SolveCast AI's Diagram Agent.

============================================================
IMPORTANT
============================================================

Do not invent values.

Do not invent assumptions unless absolutely necessary.

If information is missing, clearly mention it.

Check calculations before giving the final answer.

============================================================
OUTPUT
============================================================

Return ONLY valid JSON.

Use exactly this structure:

{
    "question": "original question",
    "steps": [
        "Step 1",
        "Step 2",
        "Step 3"
    ],
    "final_answer": "final answer",
    "diagram_required": false,
    "diagram_type": "none"
}

QUESTION:
"""


# ============================================================
# GEMINI TEXT
# ============================================================

def gemini_text(prompt: str):

    if not gemini_client:

        raise Exception(
            "Gemini API key not configured."
        )

    response = gemini_client.models.generate_content(

        model=GEMINI_MODEL,

        contents=prompt
    )

    if not response.text:

        raise Exception(
            "Gemini returned empty response."
        )

    return response.text


# ============================================================
# GROQ TEXT
# ============================================================

def groq_text(
    prompt: str,
    json_mode: bool = False
):

    if not groq_client:

        raise Exception(
            "Groq API key not configured."
        )

    kwargs = {

        "model": GROQ_MODEL,

        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],

        "temperature": 0
    }

    if json_mode:

        kwargs["response_format"] = {
            "type": "json_object"
        }

    response = (
        groq_client
        .chat
        .completions
        .create(**kwargs)
    )

    text = (
        response
        .choices[0]
        .message
        .content
    )

    if not text:

        raise Exception(
            "Groq returned empty response."
        )

    return text


# ============================================================
# OPENROUTER TEXT
# ============================================================

def openrouter_text(prompt: str):

    if not openrouter_client:

        raise Exception(
            "OpenRouter API key not configured."
        )

    response = (
        openrouter_client
        .chat
        .completions
        .create(

            model=OPENROUTER_MODEL,

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0
        )
    )

    text = (
        response
        .choices[0]
        .message
        .content
    )

    if not text:

        raise Exception(
            "OpenRouter returned empty response."
        )

    return text


# ============================================================
# HUGGING FACE TEXT
# ============================================================

def hf_text(prompt: str):

    if not hf_client:

        raise Exception(
            "Hugging Face token not configured."
        )

    response = (
        hf_client
        .chat
        .completions
        .create(

            model=HF_MODEL,

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0
        )
    )

    text = (
        response
        .choices[0]
        .message
        .content
    )

    if not text:

        raise Exception(
            "Hugging Face returned empty response."
        )

    return text


# ============================================================
# SOLUTION FALLBACK
# ============================================================

def ask_solution_with_fallback(
    prompt: str
):

    providers = [

        (
            "Gemini",
            lambda: gemini_text(prompt)
        ),

        (
            "Groq",
            lambda: groq_text(
                prompt,
                True
            )
        ),

        (
            "OpenRouter",
            lambda: openrouter_text(prompt)
        ),

        (
            "Hugging Face",
            lambda: hf_text(prompt)
        )
    ]

    errors = []

    for name, function in providers:

        try:

            print(
                f"\nTrying {name}..."
            )

            result = function()

            print(
                f"{name} SUCCESS"
            )

            return result

        except Exception as e:

            print(
                f"{name} FAILED: {e!r}"
            )

            errors.append(
                f"{name}: {e}"
            )

    raise Exception(
        "All AI providers failed.\n"
        + "\n".join(errors)
    )


# ============================================================
# CLEAN JSON
# ============================================================

def clean_json_text(
    raw: str
):

    raw = raw.strip()

    # Remove markdown code block
    if raw.startswith("```"):

        lines = raw.splitlines()

        if lines:

            lines = lines[1:]

        if lines and lines[-1].strip() == "```":

            lines = lines[:-1]

        raw = "\n".join(lines).strip()

    # Find JSON object
    start = raw.find("{")

    end = raw.rfind("}")

    if start == -1 or end == -1:

        raise Exception(
            "AI response does not contain valid JSON."
        )

    raw = raw[start:end + 1]

    try:

        return json.loads(raw)

    except json.JSONDecodeError as e:

        raise Exception(
            f"AI JSON parsing failed: {e}"
        )


# ============================================================
# PARSE SOLUTION
# ============================================================

def parse_solution(
    raw: str
):

    data = clean_json_text(raw)

    # Required fields
    question = data.get(
        "question",
        ""
    )

    steps = data.get(
        "steps",
        []
    )

    final_answer = data.get(
        "final_answer",
        ""
    )

    diagram_required = data.get(
        "diagram_required",
        False
    )

    diagram_type = data.get(
        "diagram_type",
        "none"
    )

    # Safety
    if not isinstance(
        steps,
        list
    ):

        steps = [
            str(steps)
        ]

    return {

        "question": str(
            question
        ),

        "steps": [
            str(step)
            for step in steps
        ],

        "final_answer": str(
            final_answer
        ),

        "diagram_required": bool(
            diagram_required
        ),

        "diagram_type": str(
            diagram_type
        ),

        "diagram_svg": None
    }


# ============================================================
# IMAGE DATA URL
# ============================================================

def data_url(
    image_bytes: bytes,
    mime_type: str
):

    encoded = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    return (
        f"data:{mime_type};base64,{encoded}"
    )


# ============================================================
# GEMINI IMAGE
# ============================================================

def gemini_image(
    prompt: str,
    image_bytes: bytes,
    mime_type: str
):

    if not gemini_client:

        raise Exception(
            "Gemini API key not configured."
        )

    response = (
        gemini_client
        .models
        .generate_content(

            model=GEMINI_MODEL,

            contents=[
                prompt,

                {
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": image_bytes
                    }
                }
            ]
        )
    )

    if not response.text:

        raise Exception(
            "Gemini returned empty image response."
        )

    return response.text


# ============================================================
# OPENAI-COMPATIBLE VISION
# ============================================================

def openai_vision(
    client,
    model: str,
    prompt: str,
    image_bytes: bytes,
    mime_type: str,
    provider_name: str
):

    if not client:

        raise Exception(
            f"{provider_name} API not configured."
        )

    response = (
        client
        .chat
        .completions
        .create(

            model=model,

            messages=[
                {
                    "role": "user",

                    "content": [

                        {
                            "type": "text",
                            "text": prompt
                        },

                        {
                            "type": "image_url",

                            "image_url": {
                                "url": data_url(
                                    image_bytes,
                                    mime_type
                                )
                            }
                        }
                    ]
                }
            ],

            temperature=0
        )
    )

    text = (
        response
        .choices[0]
        .message
        .content
    )

    if not text:

        raise Exception(
            f"{provider_name} returned empty image response."
        )

    return text


# ============================================================
# GROQ IMAGE
# ============================================================

def groq_image(
    prompt,
    image_bytes,
    mime_type
):

    return openai_vision(

        groq_client,

        GROQ_MODEL,

        prompt,

        image_bytes,

        mime_type,

        "Groq"
    )


# ============================================================
# OPENROUTER IMAGE
# ============================================================

def openrouter_image(
    prompt,
    image_bytes,
    mime_type
):

    return openai_vision(

        openrouter_client,

        OPENROUTER_MODEL,

        prompt,

        image_bytes,

        mime_type,

        "OpenRouter"
    )


# ============================================================
# HUGGING FACE IMAGE
# ============================================================

def hf_image(
    prompt,
    image_bytes,
    mime_type
):

    return openai_vision(

        hf_client,

        HF_MODEL,

        prompt,

        image_bytes,

        mime_type,

        "Hugging Face"
    )


# ============================================================
# IMAGE FALLBACK
# ============================================================

def ask_image_with_fallback(
    prompt,
    image_bytes,
    mime_type
):

    providers = [

        (
            "Gemini Vision",

            lambda: gemini_image(
                prompt,
                image_bytes,
                mime_type
            )
        ),

        (
            "Groq Vision",

            lambda: groq_image(
                prompt,
                image_bytes,
                mime_type
            )
        ),

        (
            "OpenRouter Vision",

            lambda: openrouter_image(
                prompt,
                image_bytes,
                mime_type
            )
        ),

        (
            "Hugging Face Vision",

            lambda: hf_image(
                prompt,
                image_bytes,
                mime_type
            )
        )
    ]

    errors = []

    for name, function in providers:

        try:

            print(
                f"\nTrying {name}..."
            )

            result = function()

            print(
                f"{name} SUCCESS"
            )

            return result

        except Exception as e:

            print(
                f"{name} FAILED: {e!r}"
            )

            errors.append(
                f"{name}: {e}"
            )

    raise Exception(
        "All Vision AI providers failed.\n"
        + "\n".join(errors)
    )


# ============================================================
# DIAGRAM GENERATION
# ============================================================

def generate_diagram(
    question: str
):

    MAX_ATTEMPTS = 2

    plan = None

    validation = None

    for attempt in range(
        MAX_ATTEMPTS
    ):

        print(
            f"\nDiagram attempt "
            f"{attempt + 1}/{MAX_ATTEMPTS}"
        )

        # First attempt
        if attempt == 0:

            plan = analyze_diagram(
                question
            )

        # Second attempt
        else:

            plan = improve_diagram(

                question,

                plan,

                validation
            )

        # ----------------------------------------------------
        # No diagram required
        # ----------------------------------------------------

        if not plan.get(
            "required",
            False
        ):

            return {

                "required": False,

                "plan": plan,

                "validation": None,

                "svg": None
            }

        # ----------------------------------------------------
        # Validate diagram
        # ----------------------------------------------------

        validation = (
            validate_diagram_plan(
                plan
            )
        )

        print(
            "Diagram validation:",
            validation
        )

        # ----------------------------------------------------
        # Valid diagram
        # ----------------------------------------------------

        if validation.get(
            "valid",
            False
        ):

            try:

                svg = render_diagram(
                    plan
                )

                return {

                    "required": True,

                    "plan": plan,

                    "validation": validation,

                    "svg": svg
                }

            except Exception as e:

                return {

                    "required": True,

                    "plan": plan,

                    "validation": validation,

                    "svg": None,

                    "error": str(e)
                }

    # --------------------------------------------------------
    # Failed after retries
    # --------------------------------------------------------

    return {

        "required": True,

        "plan": plan,

        "validation": validation,

        "svg": None,

        "error":
            "Unable to create a valid diagram plan."
    }


# ============================================================
# ADD DIAGRAM TO SOLUTION
# ============================================================

def attach_diagram(
    solution: Dict[str, Any],
    question: str
):

    try:

        diagram_result = generate_diagram(
            question
        )

        solution[
            "diagram_required"
        ] = diagram_result.get(
            "required",
            False
        )

        plan = diagram_result.get(
            "plan"
        )

        if isinstance(
            plan,
            dict
        ):

            solution[
                "diagram_type"
            ] = plan.get(
                "diagram_type",
                solution.get(
                    "diagram_type",
                    "none"
                )
            )

        solution[
            "diagram_svg"
        ] = diagram_result.get(
            "svg"
        )

        solution[
            "diagram_validation"
        ] = diagram_result.get(
            "validation"
        )

        return solution

    except Exception as e:

        print(
            "DIAGRAM ERROR:",
            repr(e)
        )

        # Do not destroy solution
        solution[
            "diagram_svg"
        ] = None

        solution[
            "diagram_error"
        ] = str(e)

        return solution


# ============================================================
# VERIFY SOLUTION
# ============================================================

def attach_verification(
    solution: Dict[str, Any],
    question: str
):

    try:

        verification = verify_solution(

            question=question,

            solution=solution
        )

        solution[
            "verification"
        ] = verification

        return solution

    except Exception as e:

        print(
            "VERIFICATION ERROR:",
            repr(e)
        )

        solution[
            "verification"
        ] = {

            "valid": False,

            "errors": [
                "Verification could not be completed."
            ],

            "warnings": [
                str(e)
            ],

            "corrected_solution": None,

            "provider": None
        }

        return solution


# ============================================================
# DOUBT FALLBACK
# ============================================================

def ask_doubt_with_fallback(
    prompt: str
):

    providers = [

        (
            "Gemini",

            lambda: gemini_text(
                prompt
            )
        ),

        (
            "Groq",

            lambda: groq_text(
                prompt,
                False
            )
        ),

        (
            "OpenRouter",

            lambda: openrouter_text(
                prompt
            )
        ),

        (
            "Hugging Face",

            lambda: hf_text(
                prompt
            )
        )
    ]

    errors = []

    for name, function in providers:

        try:

            print(
                f"\nTrying {name} for doubt..."
            )

            result = function()

            print(
                f"{name} DOUBT SUCCESS"
            )

            return result

        except Exception as e:

            print(
                f"{name} DOUBT FAILED: {e!r}"
            )

            errors.append(
                f"{name}: {e}"
            )

    raise Exception(
        "All AI providers failed for doubt.\n"
        + "\n".join(errors)
    )


# ============================================================
# TEXT SOLVE
# ============================================================

@app.post("/solve")
async def solve_question(
    question: str = Form(...)
):

    try:

        question = question.strip()

        if not question:

            return {

                "success": False,

                "error":
                    "Question cannot be empty."
            }

        print(
            "\n=============================="
        )

        print(
            "TEXT QUESTION"
        )

        print(
            "=============================="
        )

        print(
            question
        )

        # ----------------------------------------------------
        # STEP 1 - AI SOLVER
        # ----------------------------------------------------

        raw = ask_solution_with_fallback(

            SOLUTION_PROMPT
            + "\n"
            + question
        )

        solution = parse_solution(
            raw
        )

        # ----------------------------------------------------
        # STEP 2 - DIAGRAM AGENT
        # ----------------------------------------------------

        solution = attach_diagram(

            solution,

            question
        )

        # ----------------------------------------------------
        # STEP 3 - SOLUTION VERIFIER
        # ----------------------------------------------------

        solution = attach_verification(

            solution,

            question
        )

        # ----------------------------------------------------
        # FINAL RESPONSE
        # ----------------------------------------------------

        print(
            "\nTEXT SOLUTION COMPLETE"
        )

        return {

            "success": True,

            "solution": solution
        }

    except Exception as e:

        print(
            "SOLVE ERROR:",
            repr(e)
        )

        return {

            "success": False,

            "error": str(e)
        }


# ============================================================
# IMAGE SOLVE
# ============================================================

@app.post("/solve-image")
async def solve_image(
    file: UploadFile = File(...)
):

    try:

        # ----------------------------------------------------
        # Validate image
        # ----------------------------------------------------

        if (
            not file.content_type
            or
            not file.content_type.startswith(
                "image/"
            )
        ):

            return {

                "success": False,

                "error":
                    "Please upload an image."
            }

        image_bytes = await file.read()

        if not image_bytes:

            return {

                "success": False,

                "error":
                    "Image is empty."
            }

        print(
            "\n=============================="
        )

        print(
            "IMAGE QUESTION"
        )

        print(
            "=============================="
        )

        # ----------------------------------------------------
        # STEP 1 - IMAGE UNDERSTANDING
        # ----------------------------------------------------

        extraction_prompt = """
You are the image understanding module
of SolveCast AI.

Read the complete academic question
from the uploaded image.

Read carefully:

- Mathematical expressions
- Numbers
- Symbols
- Diagram labels
- Given values
- Units
- Requested values
- Tables
- Equations

Do NOT invent missing information.

If the image is too blurry or unreadable,
return exactly:

Image clear nahi hai

Otherwise return ONLY the extracted
question as plain text.
"""

        extracted = ask_image_with_fallback(

            extraction_prompt,

            image_bytes,

            file.content_type
        )

        extracted = extracted.strip()

        # ----------------------------------------------------
        # Image not readable
        # ----------------------------------------------------

        if (
            "Image clear nahi hai"
            in extracted
        ):

            return {

                "success": False,

                "error":
                    "Image clear nahi hai. "
                    "Please upload a clearer image."
            }

        if not extracted:

            return {

                "success": False,

                "error":
                    "Question image se read nahi ho paya."
            }

        print(
            "\nExtracted Question:"
        )

        print(
            extracted
        )

        # ----------------------------------------------------
        # STEP 2 - SOLVE QUESTION
        # ----------------------------------------------------

        raw = ask_solution_with_fallback(

            SOLUTION_PROMPT
            + "\n"
            + extracted
        )

        solution = parse_solution(
            raw
        )

        # Make sure actual extracted
        # question is used
        solution[
            "question"
        ] = extracted

        # ----------------------------------------------------
        # STEP 3 - DIAGRAM
        # ----------------------------------------------------

        solution = attach_diagram(

            solution,

            extracted
        )

        # ----------------------------------------------------
        # STEP 4 - VERIFICATION
        # ----------------------------------------------------

        solution = attach_verification(

            solution,

            extracted
        )

        # ----------------------------------------------------
        # FINAL
        # ----------------------------------------------------

        print(
            "\nIMAGE SOLUTION COMPLETE"
        )

        return {

            "success": True,

            "solution": solution
        }

    except Exception as e:

        print(
            "IMAGE SOLVE ERROR:",
            repr(e)
        )

        return {

            "success": False,

            "error": str(e)
        }


# ============================================================
# DOUBT
# ============================================================

@app.post("/doubt")
async def ask_doubt(
    request: Dict[str, Any]
):

    try:

        question = str(
            request.get(
                "question",
                ""
            )
        )

        solution = str(
            request.get(
                "solution",
                ""
            )
        )

        doubt = str(
            request.get(
                "doubt",
                ""
            )
        )

        if not doubt.strip():

            return {

                "success": False,

                "error":
                    "Doubt cannot be empty."
            }

        prompt = f"""
You are SolveCast AI.

Original Question:
{question}

Previous Solution:
{solution}

Student's Doubt:
{doubt}

Answer the student's doubt clearly.

Rules:

1. Focus only on the student's doubt.
2. Explain the relevant step.
3. Use simple language.
4. For mathematics, prefer equations and calculations.
5. Do not invent information.
6. Do not unnecessarily repeat the entire solution.
7. Make the answer easy for a student to understand.

Return a normal text answer.
"""

        answer = ask_doubt_with_fallback(
            prompt
        )

        return {

            "success": True,

            "answer": answer.strip()
        }

    except Exception as e:

        print(
            "DOUBT ERROR:",
            repr(e)
        )

        return {

            "success": False,

            "error": str(e)
        }


# ============================================================
# GENERATE DIAGRAM DIRECTLY
# ============================================================

@app.post("/generate-diagram")
async def generate_diagram_endpoint(
    question: str = Form(...)
):

    try:

        question = question.strip()

        if not question:

            return {

                "success": False,

                "error":
                    "Question cannot be empty."
            }

        result = generate_diagram(
            question
        )

        return {

            "success": True,

            "diagram": result
        }

    except Exception as e:

        print(
            "DIAGRAM ENDPOINT ERROR:",
            repr(e)
        )

        return {

            "success": False,

            "error": str(e)
        }


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(

        "api:app",

        host="127.0.0.1",

        port=8000,

        reload=True
    )