# backend/diagram_agent.py

import os
import json

from dotenv import load_dotenv
from google import genai
from groq import Groq
from openai import OpenAI


# =========================================================
# ENV
# =========================================================

load_dotenv()

GEMINI_API_KEY = (
    os.getenv("GEMINI_API_KEY")
    or os.getenv("GOOGLE_API_KEY")
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")


# =========================================================
# MODELS
# =========================================================

GEMINI_MODEL = "gemini-3.6-flash"
GROQ_MODEL = "qwen/qwen3.6-27b"
OPENROUTER_MODEL = "openrouter/free"
HF_MODEL = "swiss-ai/Apertus-v1.5-8B:publicai"


# =========================================================
# CLIENTS
# =========================================================

gemini_client = (
    genai.Client(api_key=GEMINI_API_KEY)
    if GEMINI_API_KEY
    else None
)

groq_client = (
    Groq(api_key=GROQ_API_KEY)
    if GROQ_API_KEY
    else None
)

openrouter_client = (
    OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1"
    )
    if OPENROUTER_API_KEY
    else None
)

hf_client = (
    OpenAI(
        api_key=HF_TOKEN,
        base_url="https://router.huggingface.co/v1"
    )
    if HF_TOKEN
    else None
)


# =========================================================
# MAIN PROMPT
# =========================================================

DIAGRAM_AGENT_PROMPT = """
You are the Diagram Agent of SolveCast AI.

Your ONLY job is to analyze an academic question and decide
whether a diagram is required.

If a diagram is required, create a precise structured diagram plan.

Supported subjects:

- Mathematics
- Physics
- Chemistry
- Biology
- Computer Science
- Coding
- Technology
- Engineering
- General academic questions

IMPORTANT:

The diagram must represent the ACTUAL question.

Do NOT create random shapes.

Do NOT create a diagram when it is unnecessary.

Do NOT assume a diagram type without considering the question.

Identify:

1. subject
2. diagram_type
3. objects
4. labels
5. relationships
6. important visual properties

---------------------------------------------------------
PHYSICS
---------------------------------------------------------

Possible diagrams:

- free body diagram
- inclined plane
- circuit
- ray diagram
- projectile
- vector diagram
- electric field
- magnetic field
- wave
- pulley
- spring
- lens
- mirror
- motion diagram

For physics:
- force directions must be meaningful
- vectors must have directions
- physical relationships must be described
- angles should be identified when relevant

---------------------------------------------------------
MATHEMATICS
---------------------------------------------------------

Possible diagrams:

- triangle
- circle
- coordinate graph
- geometry construction
- function graph
- vector diagram
- parabola
- line graph
- 3D geometry

For mathematics:
- points and labels must correspond to the question
- geometric relationships must be preserved
- axes should be included for graphs
- important angles should be identified

---------------------------------------------------------
CHEMISTRY
---------------------------------------------------------

Possible diagrams:

- molecular structure
- Lewis structure
- atomic structure
- chemical reaction
- electrochemical cell
- laboratory apparatus
- orbital diagram
- energy diagram

For chemistry:
- atoms and bonds must be represented correctly
- labels must correspond to the question
- important bonds/reactions must be identified

---------------------------------------------------------
BIOLOGY
---------------------------------------------------------

Possible diagrams:

- cell
- plant cell
- animal cell
- neuron
- DNA
- heart
- digestive system
- respiratory system
- plant structure
- biological process

For biology:
- major structures should be identified
- labels must correspond to actual biological parts
- relationships between structures must be clear

---------------------------------------------------------
COMPUTER SCIENCE / CODING
---------------------------------------------------------

Possible diagrams:

- flowchart
- UML
- ER diagram
- binary tree
- graph
- linked list
- stack
- queue
- network
- system architecture
- database architecture
- algorithm visualization

For CS:
- nodes and relationships must represent the actual algorithm/system
- arrows must show meaningful direction
- labels must match the question

---------------------------------------------------------
TECHNOLOGY / ENGINEERING
---------------------------------------------------------

Possible diagrams:

- system architecture
- block diagram
- network diagram
- circuit
- process diagram
- component diagram
- mechanical diagram
- workflow

---------------------------------------------------------
JSON FORMAT
---------------------------------------------------------

Return ONLY valid JSON.

Use exactly:

{
  "required": true,
  "subject": "physics",
  "diagram_type": "free_body_diagram",

  "objects": [
    {
      "name": "inclined_plane",
      "description": "Inclined plane on which the block is placed"
    },
    {
      "name": "block",
      "description": "Block placed on the inclined plane"
    }
  ],

  "labels": [
    "N",
    "mg",
    "f",
    "theta"
  ],

  "relationships": [
    {
      "from": "N",
      "to": "block",
      "description": "Normal force acting perpendicular to the plane"
    },
    {
      "from": "mg",
      "to": "block",
      "description": "Gravitational force acting vertically downward"
    },
    {
      "from": "f",
      "to": "block",
      "description": "Friction force acting along the plane"
    }
  ],

  "properties": {
    "direction": "physically correct",
    "labels_required": true,
    "scale": "schematic",
    "accuracy": "question_specific"
  }
}

If no diagram is required:

{
  "required": false,
  "subject": "",
  "diagram_type": "",
  "objects": [],
  "labels": [],
  "relationships": [],
  "properties": {}
}
"""


# =========================================================
# JSON CLEANER
# =========================================================

def clean_json(text: str):

    text = text.strip()

    if "```json" in text:
        text = text.replace("```json", "")

    if "```" in text:
        text = text.replace("```", "")

    return text.strip()


# =========================================================
# PROVIDER FUNCTIONS
# =========================================================

def gemini_diagram_prompt(prompt: str):

    if not gemini_client:
        raise Exception(
            "Gemini API key not configured"
        )

    response = gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    return response.text


def groq_diagram_prompt(prompt: str):

    if not groq_client:
        raise Exception(
            "Groq API key not configured"
        )

    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content


def openrouter_diagram_prompt(prompt: str):

    if not openrouter_client:
        raise Exception(
            "OpenRouter API key not configured"
        )

    response = openrouter_client.chat.completions.create(
        model=OPENROUTER_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content


def hf_diagram_prompt(prompt: str):

    if not hf_client:
        raise Exception(
            "Hugging Face token not configured"
        )

    response = hf_client.chat.completions.create(
        model=HF_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content


# =========================================================
# PROVIDER FALLBACK
# =========================================================

def analyze_diagram_with_prompt(prompt: str):

    providers = [
        (
            "Gemini",
            gemini_diagram_prompt
        ),
        (
            "Groq",
            groq_diagram_prompt
        ),
        (
            "OpenRouter",
            openrouter_diagram_prompt
        ),
        (
            "Hugging Face",
            hf_diagram_prompt
        )
    ]

    errors = []

    for name, function in providers:

        try:

            print(
                f"Trying {name} for diagram..."
            )

            result = function(prompt)

            result = clean_json(result)

            parsed = json.loads(result)

            print(
                f"{name} diagram succeeded."
            )

            return parsed

        except Exception as e:

            print(
                f"{name} diagram failed: {e}"
            )

            errors.append(
                f"{name}: {str(e)}"
            )

    return {
        "required": False,
        "subject": "",
        "diagram_type": "",
        "objects": [],
        "labels": [],
        "relationships": [],
        "properties": {},
        "error": "All diagram providers failed",
        "provider_errors": errors
    }


# =========================================================
# FIRST DIAGRAM ANALYSIS
# =========================================================

def analyze_diagram(question: str):

    prompt = f"""
{DIAGRAM_AGENT_PROMPT}

QUESTION:

{question}
"""

    return analyze_diagram_with_prompt(
        prompt
    )


# =========================================================
# IMPROVE INVALID DIAGRAM
# =========================================================

def improve_diagram(
    question: str,
    previous_plan: dict,
    validation: dict
):

    errors = validation.get(
        "errors",
        []
    )

    warnings = validation.get(
        "warnings",
        []
    )

    repair_prompt = f"""
You are the Diagram Agent of SolveCast AI.

Your previous diagram plan was checked by a validator.

You must now create an improved diagram plan.

QUESTION:

{question}


PREVIOUS DIAGRAM PLAN:

{json.dumps(
    previous_plan,
    indent=2,
    ensure_ascii=False
)}


VALIDATOR ERRORS:

{json.dumps(
    errors,
    indent=2,
    ensure_ascii=False
)}


VALIDATOR WARNINGS:

{json.dumps(
    warnings,
    indent=2,
    ensure_ascii=False
)}


IMPORTANT:

1. Fix every validator error.
2. Consider validator warnings.
3. Keep the diagram specific to the question.
4. Do not add random objects.
5. Do not remove important objects.
6. Relationships must reference valid objects or labels.
7. Labels must match the question.
8. Physics directions must be meaningful.
9. Mathematical relationships must be correct.
10. Chemistry structures must be logically consistent.
11. Biology labels must represent actual structures.
12. CS arrows and relationships must represent the actual system.
13. Return ONLY valid JSON.

Use the same JSON structure as the original Diagram Agent.
"""

    return analyze_diagram_with_prompt(
        repair_prompt
    )


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("\n================================")
    print(" SolveCast AI - Diagram Agent")
    print("================================\n")

    question = input(
        "Enter question:\n"
    )

    result = analyze_diagram(
        question
    )

    print(
        "\nDIAGRAM AGENT OUTPUT:\n"
    )

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )