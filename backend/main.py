from google import genai
from dotenv import load_dotenv
import os
import json
import mimetypes

from pydantic import BaseModel

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

from diagram import create_diagram


load_dotenv()


# ==========================================
# PYDANTIC MODELS
# ==========================================

class DiagramElement(BaseModel):

    type: str

    # Line / Arrow
    x1: float = 0
    y1: float = 0
    x2: float = 0
    y2: float = 0

    # Circle
    cx: float = 0
    cy: float = 0
    r: float = 50

    # Point / Text / Rectangle / Angle
    x: float = 0
    y: float = 0

    # Rectangle
    width: float = 100
    height: float = 100

    # Text / Angle value
    value: str = ""

    # Polygon
    points: str = ""

    # Arc / Custom SVG path
    path: str = ""


class Solution(BaseModel):

    question: str

    steps: list[str]

    final_answer: str

    diagram_required: bool

    diagram_type: str

    diagram_elements: list[DiagramElement]


# ==========================================
# GEMINI
# ==========================================

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# ==========================================
# GEMINI STRUCTURED FUNCTION
# ==========================================

def ask_gemini(prompt):

    response = client.models.generate_content(

        model="gemini-3.6-flash",

        contents=prompt,

        config={
            "response_mime_type": "application/json",
            "response_schema": Solution.model_json_schema()
        }
    )

    return response.text


# ==========================================
# GEMINI NORMAL TEXT FUNCTION
# ==========================================

def ask_gemini_text(prompt):

    response = client.models.generate_content(

        model="gemini-3.6-flash",

        contents=prompt

    )

    return response.text


# ==========================================
# PYDANTIC PARSER
# ==========================================

def parse_solution(response):

    data = json.loads(response)

    solution = Solution.model_validate(data)

    return solution


# ==========================================
# SOLUTION PROMPT
# ==========================================

solution_prompt = PromptTemplate(

    template="""

You are SolveCast AI, an AI tutor.

Solve the question exactly like a student
writing in a notebook.


==========================================
SOLUTION RULES
==========================================

- Minimum English
- Step-by-step
- Show mathematical operations line by line
- Do not skip important steps
- No unnecessary explanation
- Do not use **, $$ or LaTeX
- Use simple mathematical notation


==========================================
DIAGRAM DECISION
==========================================

First decide whether the question requires
a diagram.

If NO diagram is required:

diagram_required = false

diagram_type = "none"

diagram_elements = []

If a diagram IS required:

diagram_required = true

diagram_type must describe the actual diagram.

diagram_elements MUST NOT be empty.


Possible diagram types include:

right_triangle
triangle
circle
geometry
coordinate_graph
bar_chart
line_graph
flowchart
venn_diagram
tree
graph_theory
circuit
physics_diagram
number_line
3d_geometry
custom


IMPORTANT:

These are only examples.

You are NOT limited to these types.

Choose any suitable diagram_type when needed.


==========================================
DIAGRAM ELEMENTS
==========================================

Create the diagram using these elements:

line
arrow
circle
rectangle
point
text
polygon
arc
angle


Use multiple elements whenever necessary.


==========================================
LINE
==========================================

Use line for:

- sides
- boundaries
- axes
- connections
- wires


==========================================
ARROW
==========================================

Use arrow for:

- directions
- vectors
- flowcharts
- directed graphs
- axes


==========================================
CIRCLE
==========================================

Use circle for:

- circles
- nodes
- circular objects


==========================================
RECTANGLE
==========================================

Use rectangle for:

- boxes
- flowchart blocks
- rectangular objects


==========================================
POINT
==========================================

Use point for:

- important points
- graph points
- vertices


==========================================
TEXT
==========================================

Use text for:

- A, B, C labels
- measurements
- names
- units
- equations
- descriptions


==========================================
POLYGON
==========================================

Use polygon for:

- triangles
- quadrilaterals
- polygons
- irregular shapes


Use a coordinate string such as:

100,300 250,100 400,300


==========================================
ARC
==========================================

Use arc for:

- curves
- circular arcs
- curved boundaries


==========================================
ANGLE
==========================================

ANGLE ELEMENT IS REQUIRED WHENEVER
THE QUESTION ASKS TO MARK AN ANGLE.


If the question says:

mark angle B

you MUST create an angle element.

For that angle:

type = angle

value = empty


The angle marker must be positioned
near vertex B.


If the question gives an angle value:

angle B = 60 degrees

you MUST create an angle element.

The value should be:

60°


IMPORTANT:

NEVER invent an angle value.

If the question does not provide
the angle measurement:

value MUST be empty.


==========================================
TRIANGLE RULE
==========================================

For a triangle create enough elements
to clearly represent it.

Include:

- triangle shape
- vertex labels
- side measurements
- angle markers when requested


For example:

Question:

Draw triangle ABC with AB = 5 cm,
BC = 4 cm, AC = 6 cm and mark angle B.


The diagram should contain:

triangle

A label

B label

C label

5 cm

4 cm

6 cm

angle marker at B


If no angle value is provided:

Do NOT write any angle value.


==========================================
CIRCLE RULE
==========================================

For a circle create:

circle

and appropriate text elements for:

- center
- radius
- diameter
- measurements

when provided.


==========================================
COORDINATE GRAPH RULE
==========================================

For coordinate graphs create:

- x-axis
- y-axis
- arrows
- points
- coordinate labels

when required.


==========================================
FLOWCHART RULE
==========================================

For flowcharts use:

rectangle

arrow

text


Each important block should have
its own rectangle and text.


==========================================
ACCURACY RULES
==========================================

NEVER invent information.

If the question does not provide:

- angle value
- side value
- point name
- measurement

do not invent it.


Only show information available
from the question.


Create enough elements to reproduce
the required diagram.


Use coordinates approximately between:

x = 50 to 750

y = 50 to 550


==========================================
FINAL CHECK
==========================================

Before returning the answer check:

1. Is a diagram required?

2. If yes, is diagram_required true?

3. Is diagram_type correct?

4. Is diagram_elements not empty?

5. Are all important labels included?

6. Are all given measurements included?

7. If an angle was requested,
   is an angle element present?

8. If angle value was not given,
   is its value empty?

9. Did you avoid inventing information?


==========================================
OUTPUT
==========================================

Return the answer in the required
structured format.

Question:

{question}

""",

    input_variables=["question"]
)


# ==========================================
# SOLUTION CHAIN
# ==========================================

solution_chain = (

    solution_prompt

    | RunnableLambda(ask_gemini)

    | RunnableLambda(parse_solution)

)


# ==========================================
# MAIN
# ==========================================

print("\n================================")
print("        SOLVECAST AI")
print("================================\n")

print("1. Type Question")
print("2. Upload Image")

choice = input("\nChoose option (1/2): ")


# ==========================================
# TYPE QUESTION
# ==========================================

if choice == "1":

    question = input("\nQuestion: ")

    solution = solution_chain.invoke({

        "question": question

    })


# ==========================================
# IMAGE QUESTION
# ==========================================

elif choice == "2":

    image_path = input("\nImage path: ")


    # --------------------------------------
    # OPEN IMAGE
    # --------------------------------------

    try:

        with open(image_path, "rb") as f:

            image_bytes = f.read()

    except FileNotFoundError:

        print("\nImage file nahi mili.")

        exit()


    # --------------------------------------
    # DETECT IMAGE TYPE
    # --------------------------------------

    mime_type, _ = mimetypes.guess_type(
        image_path
    )


    if mime_type is None:

        mime_type = "image/jpeg"


    # --------------------------------------
    # READ QUESTION FROM IMAGE
    # --------------------------------------

    extraction_prompt = """

Look at this image carefully.

Extract ONLY the complete question written
in the image.

Do not solve it.

Do not add explanation.

If the image is unclear, write:

Image clear nahi hai.

"""


    extraction_response = client.models.generate_content(

        model="gemini-3.6-flash",

        contents=[

            extraction_prompt,

            {
                "inline_data": {

                    "mime_type": mime_type,

                    "data": image_bytes

                }

            }

        ]

    )


    question = extraction_response.text.strip()


    # --------------------------------------
    # CHECK IMAGE
    # --------------------------------------

    if "Image clear nahi hai" in question:

        print("\nImage clear nahi hai.")

        exit()


    # --------------------------------------
    # SOLVE QUESTION
    # --------------------------------------

    solution = solution_chain.invoke({

        "question": question

    })


# ==========================================
# INVALID OPTION
# ==========================================

else:

    print("\nInvalid choice.")

    exit()


# ==========================================
# SHOW QUESTION
# ==========================================

print("\n================================")
print("        QUESTION")
print("================================\n")

print(solution.question)


# ==========================================
# SHOW SOLUTION
# ==========================================

print("\n================================")
print("        SOLUTION")
print("================================\n")

for i, step in enumerate(
    solution.steps,
    start=1
):

    print(f"Step {i}: {step}")


print(
    "\n∴ Final Answer:",
    solution.final_answer
)


# ==========================================
# DIAGRAM INFORMATION
# ==========================================

print("\n================================")
print("        DIAGRAM INFO")
print("================================\n")

print(
    "Diagram Required:",
    solution.diagram_required
)

print(
    "Diagram Type:",
    solution.diagram_type
)

print(
    "Diagram Elements:",
    len(solution.diagram_elements)
)


# ==========================================
# CREATE DIAGRAM
# ==========================================

if solution.diagram_required:

    try:

        elements = [

            element.model_dump()

            for element in solution.diagram_elements

        ]


        create_diagram(

            elements,

            filename="diagram.svg"

        )


    except Exception as e:

        print(
            "\nDiagram create nahi ho saka:"
        )

        print(e)


# ==========================================
# DOUBT SECTION
# ==========================================

while True:

    doubt = input(
        "\nYour doubt "
        "(type 'exit' to stop): "
    )


    if doubt.lower() == "exit":

        print("\nSolveCast AI closed.")

        break


    # --------------------------------------
    # DOUBT PROMPT
    # --------------------------------------

    doubt_prompt = f"""

You are SolveCast AI, an AI tutor.

Original Question:

{solution.question}


Previous Solution:

{solution.steps}


Final Answer:

{solution.final_answer}


Student's Doubt:

{doubt}


Answer ONLY the student's doubt.

RULES:

- Explain simply.
- Minimum English.
- Use mathematical steps where required.
- If the doubt is about a particular step,
  explain why that step was done.
- Do not unnecessarily repeat the complete
  solution.

"""


    # --------------------------------------
    # DOUBT CHAIN
    # --------------------------------------

    doubt_chain = (

        RunnableLambda(ask_gemini_text)

        | StrOutputParser()

    )


    doubt_result = doubt_chain.invoke(

        doubt_prompt

    )


    # --------------------------------------
    # SHOW DOUBT ANSWER
    # --------------------------------------

    print("\n================================")
    print("      SOLVECAST AI")
    print("================================\n")

    print(doubt_result)
    