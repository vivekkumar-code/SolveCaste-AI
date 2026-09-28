import math
import html


# =========================================================
# UNIVERSAL SVG DIAGRAM RENDERER
# =========================================================

SVG_WIDTH = 600
SVG_HEIGHT = 400


def esc(value):
    """Safely convert text for SVG."""
    if value is None:
        return ""
    return html.escape(str(value))


def num(value, default=0):
    """Safely convert coordinate/value to float."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def point_xy(element):
    return num(element.get("x")), num(element.get("y"))


def render_line(e):
    x1 = num(e.get("x1"))
    y1 = num(e.get("y1"))
    x2 = num(e.get("x2"))
    y2 = num(e.get("y2"))

    return f"""
    <line
        x1="{x1}" y1="{y1}"
        x2="{x2}" y2="{y2}"
        class="diagram-line"
    />
    """


def render_arrow(e):
    x1 = num(e.get("x1"))
    y1 = num(e.get("y1"))
    x2 = num(e.get("x2"))
    y2 = num(e.get("y2"))

    return f"""
    <line
        x1="{x1}" y1="{y1}"
        x2="{x2}" y2="{y2}"
        class="diagram-line"
        marker-end="url(#arrowhead)"
    />
    """


def render_circle(e):
    cx = num(e.get("cx", e.get("x")))
    cy = num(e.get("cy", e.get("y")))
    r = num(e.get("r", e.get("radius")), 50)

    return f"""
    <circle
        cx="{cx}"
        cy="{cy}"
        r="{r}"
        class="diagram-shape"
    />
    """


def render_rectangle(e):
    x = num(e.get("x"))
    y = num(e.get("y"))
    width = num(e.get("width"), 100)
    height = num(e.get("height"), 80)

    return f"""
    <rect
        x="{x}"
        y="{y}"
        width="{width}"
        height="{height}"
        class="diagram-shape"
    />
    """


def render_point(e):
    x = num(e.get("x"))
    y = num(e.get("y"))
    label = e.get("label", "")

    label_offset_x = num(e.get("label_offset_x"), 8)
    label_offset_y = num(e.get("label_offset_y"), -8)

    return f"""
    <circle
        cx="{x}"
        cy="{y}"
        r="4"
        class="diagram-point"
    />

    <text
        x="{x + label_offset_x}"
        y="{y + label_offset_y}"
        class="diagram-label"
    >
        {esc(label)}
    </text>
    """


def render_text(e):
    x = num(e.get("x"))
    y = num(e.get("y"))
    text = e.get("text", e.get("label", ""))

    return f"""
    <text
        x="{x}"
        y="{y}"
        class="diagram-label"
    >
        {esc(text)}
    </text>
    """


def render_polygon(e):
    points = e.get("points", [])

    if not points:
        return ""

    formatted_points = []

    for p in points:
        if isinstance(p, dict):
            x = num(p.get("x"))
            y = num(p.get("y"))
        elif isinstance(p, (list, tuple)) and len(p) >= 2:
            x = num(p[0])
            y = num(p[1])
        else:
            continue

        formatted_points.append(f"{x},{y}")

    if not formatted_points:
        return ""

    return f"""
    <polygon
        points="{' '.join(formatted_points)}"
        class="diagram-shape"
    />
    """


def render_arc(e):
    cx = num(e.get("cx"))
    cy = num(e.get("cy"))
    r = num(e.get("r"), 40)

    start_angle = num(e.get("start_angle"))
    end_angle = num(e.get("end_angle"))

    start_rad = math.radians(start_angle)
    end_rad = math.radians(end_angle)

    x1 = cx + r * math.cos(start_rad)
    y1 = cy + r * math.sin(start_rad)

    x2 = cx + r * math.cos(end_rad)
    y2 = cy + r * math.sin(end_rad)

    angle_difference = abs(end_angle - start_angle)
    large_arc = 1 if angle_difference > 180 else 0

    sweep = 1 if end_angle > start_angle else 0

    return f"""
    <path
        d="M {x1} {y1}
           A {r} {r} 0 {large_arc} {sweep} {x2} {y2}"
        class="diagram-line"
        fill="none"
    />
    """


def render_angle(e):
    """
    Draws an angle marker using vertex + two rays.
    """

    x = num(e.get("x"))
    y = num(e.get("y"))

    radius = num(e.get("radius"), 28)

    start_angle = num(e.get("start_angle"), 0)
    end_angle = num(e.get("end_angle"), 90)

    start_rad = math.radians(start_angle)
    end_rad = math.radians(end_angle)

    x1 = x + radius * math.cos(start_rad)
    y1 = y + radius * math.sin(start_rad)

    x2 = x + radius * math.cos(end_rad)
    y2 = y + radius * math.sin(end_rad)

    difference = abs(end_angle - start_angle)

    large_arc = 1 if difference > 180 else 0
    sweep = 1 if end_angle > start_angle else 0

    value = e.get("value", "")
    label = e.get("label", "")

    result = f"""
    <path
        d="M {x1} {y1}
           A {radius} {radius} 0 {large_arc} {sweep} {x2} {y2}"
        class="angle-marker"
        fill="none"
    />
    """

    if label or value:
        text = label

        if value:
            if text:
                text += f" = {value}"
            else:
                text = str(value)

        mid_angle = math.radians(
            (start_angle + end_angle) / 2
        )

        text_x = x + (radius + 15) * math.cos(mid_angle)
        text_y = y + (radius + 15) * math.sin(mid_angle)

        result += f"""
        <text
            x="{text_x}"
            y="{text_y}"
            class="diagram-angle-label"
        >
            {esc(text)}
        </text>
        """

    return result


def render_right_angle(e):
    """
    Draws a small square showing 90°.
    """

    x = num(e.get("x"))
    y = num(e.get("y"))
    size = num(e.get("size"), 18)

    return f"""
    <path
        d="
            M {x} {y - size}
            L {x + size} {y - size}
            L {x + size} {y}
        "
        class="right-angle"
        fill="none"
    />
    """


def render_element(element):
    """
    Universal element dispatcher.
    """

    if not isinstance(element, dict):
        return ""

    element_type = str(
        element.get("type", "")
    ).lower().strip()

    if element_type == "line":
        return render_line(element)

    if element_type == "arrow":
        return render_arrow(element)

    if element_type == "circle":
        return render_circle(element)

    if element_type in ["rectangle", "square"]:
        return render_rectangle(element)

    if element_type == "point":
        return render_point(element)

    if element_type == "text":
        return render_text(element)

    if element_type == "polygon":
        return render_polygon(element)

    if element_type == "arc":
        return render_arc(element)

    if element_type == "angle":
        return render_angle(element)

    if element_type in ["right_angle", "right-angle"]:
        return render_right_angle(element)

    return ""


# =========================================================
# SPECIAL STRUCTURED DIAGRAM HELPERS
# =========================================================

def create_triangle(
    A=(120, 300),
    B=(420, 300),
    C=(420, 100),
    labels=("A", "B", "C"),
    right_angle_at=None
):
    """
    Creates a triangle as generic diagram elements.
    """

    ax, ay = A
    bx, by = B
    cx, cy = C

    elements = [

        {
            "type": "line",
            "x1": ax,
            "y1": ay,
            "x2": bx,
            "y2": by
        },

        {
            "type": "line",
            "x1": bx,
            "y1": by,
            "x2": cx,
            "y2": cy
        },

        {
            "type": "line",
            "x1": cx,
            "y1": cy,
            "x2": ax,
            "y2": ay
        },

        {
            "type": "point",
            "x": ax,
            "y": ay,
            "label": labels[0]
        },

        {
            "type": "point",
            "x": bx,
            "y": by,
            "label": labels[1]
        },

        {
            "type": "point",
            "x": cx,
            "y": cy,
            "label": labels[2]
        }
    ]

    if right_angle_at == "B":
        elements.append({
            "type": "right_angle",
            "x": bx - 18,
            "y": by - 18,
            "size": 18
        })

    return elements


def create_right_triangle():
    """
    Standard right triangle.
    """

    return create_triangle(
        A=(120, 300),
        B=(420, 300),
        C=(420, 100),
        labels=("A", "B", "C"),
        right_angle_at="B"
    )


# =========================================================
# DIAGRAM TYPE NORMALIZATION
# =========================================================

def normalize_diagram_elements(
    diagram_type="",
    elements=None
):
    """
    Normalizes AI-generated diagram data.

    AI-generated elements are preserved.
    Special structured diagrams can also be supported.
    """

    elements = elements or []

    diagram_type = str(
        diagram_type or ""
    ).lower().strip()

    # If AI already generated valid elements,
    # keep them.
    if elements:
        return elements

    # Special fallback diagrams.
    if diagram_type in [
        "triangle",
        "right_triangle",
        "right-triangle"
    ]:
        if diagram_type in [
            "right_triangle",
            "right-triangle"
        ]:
            return create_right_triangle()

        return create_triangle()

    return []


# =========================================================
# MAIN SVG CREATOR
# =========================================================

def create_diagram(
    elements=None,
    diagram_type="",
    filename=None
):
    """
    Create a complete SVG diagram.

    Returns SVG string.

    If filename is supplied, SVG is also saved.
    """

    elements = normalize_diagram_elements(
        diagram_type=diagram_type,
        elements=elements
    )

    svg_elements = []

    for element in elements:
        svg_elements.append(
            render_element(element)
        )

    content = "\n".join(svg_elements)

    svg = f"""
<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{SVG_WIDTH}"
    height="{SVG_HEIGHT}"
    viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}"
>

    <defs>

        <marker
            id="arrowhead"
            markerWidth="10"
            markerHeight="10"
            refX="8"
            refY="3"
            orient="auto"
            markerUnits="strokeWidth"
        >
            <path
                d="M0,0 L0,6 L9,3 z"
                fill="currentColor"
            />
        </marker>

        <style>

            .diagram-line {{
                stroke: currentColor;
                stroke-width: 2.5;
                fill: none;
                stroke-linecap: round;
                stroke-linejoin: round;
            }}

            .diagram-shape {{
                stroke: currentColor;
                stroke-width: 2.5;
                fill: none;
                stroke-linejoin: round;
            }}

            .diagram-point {{
                fill: currentColor;
            }}

            .diagram-label {{
                fill: currentColor;
                font-size: 17px;
                font-family: Arial, sans-serif;
                font-weight: 500;
            }}

            .diagram-angle-label {{
                fill: currentColor;
                font-size: 15px;
                font-family: Arial, sans-serif;
            }}

            .angle-marker {{
                stroke: currentColor;
                stroke-width: 2;
            }}

            .right-angle {{
                stroke: currentColor;
                stroke-width: 2;
            }}

        </style>

    </defs>

    {content}

</svg>
"""

    if filename:
        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as f:
            f.write(svg)

    return svg