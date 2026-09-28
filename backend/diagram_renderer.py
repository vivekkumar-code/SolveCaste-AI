# backend/diagram_renderer.py

import html
import math


WIDTH = 800
HEIGHT = 500


# =========================================================
# HELPERS
# =========================================================

def esc(value):
    return html.escape(str(value))


def svg_start():
    return f"""
<svg xmlns="http://www.w3.org/2000/svg"
     width="{WIDTH}"
     height="{HEIGHT}"
     viewBox="0 0 {WIDTH} {HEIGHT}"
     role="img">

<defs>

    <marker id="arrow"
            markerWidth="10"
            markerHeight="10"
            refX="8"
            refY="5"
            orient="auto">
        <path d="M0,0 L10,5 L0,10 Z" fill="#172033"/>
    </marker>

    <marker id="blueArrow"
            markerWidth="10"
            markerHeight="10"
            refX="8"
            refY="5"
            orient="auto">
        <path d="M0,0 L10,5 L0,10 Z" fill="#2563eb"/>
    </marker>

</defs>

<rect width="100%" height="100%" fill="white"/>
"""


def svg_end():
    return "</svg>"


def line(x1, y1, x2, y2, arrow=False, color="#172033", width=3):
    marker = ' marker-end="url(#arrow)"' if arrow else ""

    return (
        f'<line x1="{x1}" y1="{y1}" '
        f'x2="{x2}" y2="{y2}" '
        f'stroke="{color}" '
        f'stroke-width="{width}" '
        f'stroke-linecap="round"{marker}/>'
    )


def text(x, y, value, size=20, bold=False):
    weight = "bold" if bold else "normal"

    return (
        f'<text x="{x}" y="{y}" '
        f'font-family="Arial, sans-serif" '
        f'font-size="{size}" '
        f'font-weight="{weight}" '
        f'fill="#172033">'
        f'{esc(value)}</text>'
    )


def circle(cx, cy, r, fill="white", stroke="#172033", width=3):
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" '
        f'fill="{fill}" stroke="{stroke}" '
        f'stroke-width="{width}"/>'
    )


def rectangle(
    x,
    y,
    width,
    height,
    fill="#e8f0ff",
    stroke="#172033"
):
    return (
        f'<rect x="{x}" y="{y}" '
        f'width="{width}" height="{height}" '
        f'rx="6" '
        f'fill="{fill}" '
        f'stroke="{stroke}" '
        f'stroke-width="3"/>'
    )


def polygon(points, fill="white", stroke="#172033", width=3):
    points_string = " ".join(
        f"{x},{y}" for x, y in points
    )

    return (
        f'<polygon points="{points_string}" '
        f'fill="{fill}" '
        f'stroke="{stroke}" '
        f'stroke-width="{width}" '
        f'stroke-linejoin="round"/>'
    )


# =========================================================
# PHYSICS
# =========================================================

def render_inclined_plane(plan):

    svg = svg_start()

    # Ground / inclined plane
    plane = [
        (120, 390),
        (650, 390),
        (650, 170)
    ]

    svg += polygon(
        plane,
        fill="#f3f4f6"
    )

    # Block
    block = [
        (390, 285),
        (450, 250),
        (485, 310),
        (425, 345)
    ]

    svg += polygon(
        block,
        fill="#dbeafe"
    )

    svg += text(
        420,
        305,
        "m",
        20,
        True
    )

    # Angle
    svg += text(
        155,
        370,
        "θ",
        24,
        True
    )

    # Gravity
    svg += line(
        438,
        300,
        438,
        420,
        arrow=True,
        color="#dc2626"
    )

    svg += text(
        450,
        415,
        "mg",
        20,
        True
    )

    # Normal force
    svg += line(
        438,
        285,
        390,
        205,
        arrow=True,
        color="#2563eb"
    )

    svg += text(
        350,
        195,
        "N",
        20,
        True
    )

    # Friction
    svg += line(
        445,
        280,
        535,
        225,
        arrow=True,
        color="#16a34a"
    )

    svg += text(
        535,
        220,
        "f",
        20,
        True
    )

    svg += text(
        300,
        75,
        "Free Body Diagram",
        28,
        True
    )

    return svg + svg_end()


# =========================================================
# MATHS
# =========================================================

def render_triangle(plan):

    svg = svg_start()

    points = [
        (180, 380),
        (620, 380),
        (400, 110)
    ]

    svg += polygon(
        points,
        fill="#f8fafc"
    )

    svg += text(
        160,
        405,
        "A",
        22,
        True
    )

    svg += text(
        625,
        405,
        "B",
        22,
        True
    )

    svg += text(
        395,
        90,
        "C",
        22,
        True
    )

    labels = plan.get("labels", [])

    positions = [
        (260, 360),
        (500, 360),
        (420, 230)
    ]

    for i, label in enumerate(labels[:3]):

        x, y = positions[i]

        svg += text(
            x,
            y,
            label,
            18
        )

    svg += text(
        300,
        60,
        "Geometry Diagram",
        28,
        True
    )

    return svg + svg_end()


def render_circle_diagram(plan):

    svg = svg_start()

    svg += circle(
        400,
        260,
        140
    )

    svg += line(
        260,
        260,
        540,
        260
    )

    svg += text(
        390,
        250,
        "O",
        20,
        True
    )

    svg += text(
        400,
        235,
        "r",
        18
    )

    svg += text(
        280,
        60,
        "Circle",
        28,
        True
    )

    return svg + svg_end()


# =========================================================
# CHEMISTRY
# =========================================================

def render_molecule(plan):

    svg = svg_start()

    labels = plan.get(
        "labels",
        []
    )

    # Default CH4-like layout
    center_x = 400
    center_y = 270

    positions = [
        (400, 150),
        (530, 270),
        (400, 390),
        (270, 270)
    ]

    center_label = "C"

    if labels:
        center_label = labels[0]

    # Bonds
    for x, y in positions:

        svg += line(
            center_x,
            center_y,
            x,
            y,
            color="#172033",
            width=4
        )

    # Central atom
    svg += circle(
        center_x,
        center_y,
        42,
        fill="#dbeafe"
    )

    svg += text(
        center_x - 8,
        center_y + 8,
        center_label,
        24,
        True
    )

    # Outer atoms
    for i, (x, y) in enumerate(positions):

        label = "H"

        if i + 1 < len(labels):
            label = labels[i + 1]

        svg += circle(
            x,
            y,
            32,
            fill="#f3f4f6"
        )

        svg += text(
            x - 8,
            y + 8,
            label,
            20,
            True
        )

    svg += text(
        315,
        65,
        "Molecular Structure",
        28,
        True
    )

    return svg + svg_end()


# =========================================================
# BIOLOGY
# =========================================================

def render_neuron(plan):

    svg = svg_start()

    # Cell body
    svg += circle(
        400,
        260,
        65,
        fill="#fef3c7"
    )

    svg += text(
        375,
        265,
        "Cell body",
        16,
        True
    )

    # Dendrites
    dendrites = [
        (340, 230, 180, 170),
        (340, 260, 150, 260),
        (340, 290, 180, 350),
    ]

    for x1, y1, x2, y2 in dendrites:

        svg += line(
            x1,
            y1,
            x2,
            y2,
            width=4
        )

    # Axon
    svg += line(
        465,
        260,
        680,
        260,
        width=8
    )

    svg += text(
        560,
        240,
        "Axon",
        18,
        True
    )

    # Axon terminal
    svg += line(
        680,
        260,
        735,
        220,
        width=4
    )

    svg += line(
        680,
        260,
        735,
        300,
        width=4
    )

    svg += text(
        285,
        70,
        "Neuron",
        28,
        True
    )

    return svg + svg_end()


# =========================================================
# COMPUTER SCIENCE
# =========================================================

def render_flowchart(plan):

    svg = svg_start()

    # Start
    svg += circle(
        400,
        80,
        45,
        fill="#dcfce7"
    )

    svg += text(
        370,
        87,
        "Start",
        18,
        True
    )

    # Process
    svg += rectangle(
        310,
        160,
        180,
        65
    )

    svg += text(
        350,
        200,
        "Process",
        18,
        True
    )

    # Decision
    decision = [
        (400, 275),
        (500, 335),
        (400, 395),
        (300, 335)
    ]

    svg += polygon(
        decision,
        fill="#fef3c7"
    )

    svg += text(
        370,
        342,
        "Condition?",
        16,
        True
    )

    # End
    svg += circle(
        400,
        450,
        35,
        fill="#fee2e2"
    )

    svg += text(
        378,
        457,
        "End",
        17,
        True
    )

    # Arrows
    svg += line(
        400,
        125,
        400,
        160,
        arrow=True
    )

    svg += line(
        400,
        225,
        400,
        275,
        arrow=True
    )

    svg += line(
        400,
        395,
        400,
        415,
        arrow=True
    )

    svg += text(
        325,
        35,
        "Flowchart",
        28,
        True
    )

    return svg + svg_end()


# =========================================================
# GENERIC FALLBACK
# =========================================================

def render_generic(plan):

    svg = svg_start()

    objects = plan.get(
        "objects",
        []
    )

    labels = plan.get(
        "labels",
        []
    )

    relationships = plan.get(
        "relationships",
        []
    )

    # Create nodes automatically
    count = max(
        len(objects),
        1
    )

    spacing = WIDTH / (count + 1)

    positions = {}

    for i, obj in enumerate(objects):

        if not isinstance(obj, dict):
            continue

        name = obj.get(
            "name",
            f"Object {i + 1}"
        )

        x = spacing * (i + 1)
        y = 250

        positions[name] = (x, y)

        svg += rectangle(
            x - 70,
            y - 35,
            140,
            70,
            fill="#eef2ff"
        )

        svg += text(
            x - 50,
            y + 7,
            name,
            16,
            True
        )

    # Relationships
    for relation in relationships:

        if not isinstance(
            relation,
            dict
        ):
            continue

        source = relation.get("from")
        target = relation.get("to")

        if source not in positions:
            continue

        if target not in positions:
            continue

        x1, y1 = positions[source]
        x2, y2 = positions[target]

        svg += line(
            x1,
            y1,
            x2,
            y2,
            arrow=True
        )

    # Extra labels
    for i, label in enumerate(labels):

        svg += text(
            40,
            420 + (i * 25),
            str(label),
            16
        )

    svg += text(
        300,
        60,
        plan.get(
            "diagram_type",
            "Diagram"
        ),
        28,
        True
    )

    return svg + svg_end()


# =========================================================
# ROUTER
# =========================================================

def render_diagram(plan):

    if not plan:
        return render_generic({})

    if not plan.get("required", False):
        return None

    diagram_type = (
        plan.get(
            "diagram_type",
            ""
        )
        .lower()
        .strip()
    )

    # Physics
    if diagram_type in [
        "free_body_diagram",
        "inclined_plane",
        "inclined_plane_diagram"
    ]:
        return render_inclined_plane(plan)

    # Maths
    if diagram_type in [
        "triangle",
        "triangle_diagram",
        "geometry"
    ]:
        return render_triangle(plan)

    if diagram_type in [
        "circle",
        "circle_diagram"
    ]:
        return render_circle_diagram(plan)

    # Chemistry
    if diagram_type in [
        "molecule",
        "molecular_structure",
        "lewis_structure"
    ]:
        return render_molecule(plan)

    # Biology
    if diagram_type in [
        "neuron",
        "neuron_diagram"
    ]:
        return render_neuron(plan)

    # Computer Science
    if diagram_type in [
        "flowchart",
        "algorithm_flowchart"
    ]:
        return render_flowchart(plan)

    # Anything else
    return render_generic(plan)


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    test_plan = {
        "required": True,

        "subject": "physics",

        "diagram_type": "free_body_diagram",

        "objects": [
            {
                "name": "inclined_plane",
                "description":
                    "Inclined plane"
            },
            {
                "name": "block",
                "description":
                    "Block on plane"
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
                "description":
                    "Normal force"
            }
        ],

        "properties": {
            "direction":
                "physically correct"
        }
    }

    svg = render_diagram(
        test_plan
    )

    with open(
        "test_diagram.svg",
        "w",
        encoding="utf-8"
    ) as file:

        file.write(svg)

    print(
        "\nDiagram generated successfully!"
    )

    print(
        "File: test_diagram.svg"
    )