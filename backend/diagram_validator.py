# backend/diagram_validator.py

import json


# =========================
# VALIDATE DIAGRAM PLAN
# =========================

def validate_diagram_plan(plan):
    """
    Validate structured output generated
    by the Diagram Agent.
    """

    errors = []
    warnings = []

    # -------------------------
    # Check main object
    # -------------------------

    if not isinstance(plan, dict):
        return {
            "valid": False,
            "errors": [
                "Diagram plan must be a JSON object"
            ],
            "warnings": []
        }

    # -------------------------
    # Required
    # -------------------------

    required = plan.get("required")

    if required not in [True, False]:
        errors.append(
            "'required' must be true or false"
        )

    # -------------------------
    # No diagram required
    # -------------------------

    if required is False:

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    # -------------------------
    # Subject
    # -------------------------

    subject = plan.get("subject", "")

    if not isinstance(subject, str):
        errors.append(
            "'subject' must be a string"
        )

    elif not subject.strip():
        errors.append(
            "Subject is missing"
        )

    # -------------------------
    # Diagram Type
    # -------------------------

    diagram_type = plan.get(
        "diagram_type",
        ""
    )

    if not isinstance(diagram_type, str):
        errors.append(
            "'diagram_type' must be a string"
        )

    elif not diagram_type.strip():
        errors.append(
            "Diagram type is missing"
        )

    # -------------------------
    # Objects
    # -------------------------

    objects = plan.get(
        "objects",
        []
    )

    if not isinstance(objects, list):

        errors.append(
            "'objects' must be a list"
        )

    elif len(objects) == 0:

        errors.append(
            "No diagram objects found"
        )

    else:

        for i, obj in enumerate(objects):

            if not isinstance(
                obj,
                dict
            ):

                errors.append(
                    f"Object {i + 1} "
                    f"must be an object"
                )

                continue

            name = obj.get("name")

            if not name:

                errors.append(
                    f"Object {i + 1} "
                    f"has no name"
                )

            description = obj.get(
                "description"
            )

            if not description:

                warnings.append(
                    f"Object {i + 1} "
                    f"has no description"
                )

    # -------------------------
    # Labels
    # -------------------------

    labels = plan.get(
        "labels",
        []
    )

    if not isinstance(labels, list):

        errors.append(
            "'labels' must be a list"
        )

    else:

        for i, label in enumerate(labels):

            if not isinstance(
                label,
                str
            ):

                errors.append(
                    f"Label {i + 1} "
                    f"must be a string"
                )

    # -------------------------
    # Relationships
    # -------------------------

    relationships = plan.get(
        "relationships",
        []
    )

    if not isinstance(
        relationships,
        list
    ):

        errors.append(
            "'relationships' must be a list"
        )

    else:

        for i, relation in enumerate(
            relationships
        ):

            if not isinstance(
                relation,
                dict
            ):

                errors.append(
                    f"Relationship {i + 1} "
                    f"must be an object"
                )

                continue

            source = relation.get(
                "from"
            )

            target = relation.get(
                "to"
            )

            description = relation.get(
                "description"
            )

            if not source:

                errors.append(
                    f"Relationship {i + 1} "
                    f"missing 'from'"
                )

            if not target:

                errors.append(
                    f"Relationship {i + 1} "
                    f"missing 'to'"
                )

            if not description:

                warnings.append(
                    f"Relationship {i + 1} "
                    f"has no description"
                )

    # -------------------------
    # Properties
    # -------------------------

    properties = plan.get(
        "properties",
        {}
    )

    if not isinstance(
        properties,
        dict
    ):

        errors.append(
            "'properties' must be an object"
        )

    # -------------------------
    # Known names
    # -------------------------

    object_names = set()

    for obj in objects:

        if isinstance(
            obj,
            dict
        ):

            name = obj.get(
                "name"
            )

            if name:
                object_names.add(
                    name
                )

    # Labels can also be used
    # as relationship endpoints.
    #
    # Example:
    # N → block
    # mg → block
    # f → block

    label_names = set()

    for label in labels:

        if isinstance(
            label,
            str
        ):

            label_names.add(
                label
            )

    # Objects + labels
    known_names = (
        object_names |
        label_names
    )

    # -------------------------
    # Validate relationships
    # -------------------------

    for relation in relationships:

        if not isinstance(
            relation,
            dict
        ):
            continue

        source = relation.get(
            "from"
        )

        target = relation.get(
            "to"
        )

        # Source can be object OR label
        if (
            source
            and source not in known_names
        ):

            warnings.append(
                f"Relationship source "
                f"'{source}' is not listed "
                f"as an object or label"
            )

        # Target can be object OR label
        if (
            target
            and target not in known_names
        ):

            warnings.append(
                f"Relationship target "
                f"'{target}' is not listed "
                f"as an object or label"
            )

    # -------------------------
    # Final result
    # -------------------------

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


# =========================
# VALIDATE JSON STRING
# =========================

def validate_diagram_json(
    json_text
):
    """
    Validate a JSON string
    returned by Diagram Agent.
    """

    try:

        plan = json.loads(
            json_text
        )

    except json.JSONDecodeError:

        return {
            "valid": False,
            "errors": [
                "Invalid JSON"
            ],
            "warnings": []
        }

    return validate_diagram_plan(
        plan
    )


# =========================
# TEST
# =========================

if __name__ == "__main__":

    test_plan = {

        "required": True,

        "subject": "physics",

        "diagram_type":
            "free_body_diagram",

        "objects": [

            {
                "name":
                    "inclined_plane",

                "description":
                    "A wedge-shaped ramp"
            },

            {
                "name":
                    "block",

                "description":
                    "A block placed "
                    "on the plane"
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
                    "Normal force "
                    "perpendicular "
                    "to plane"
            },

            {
                "from": "mg",

                "to": "block",

                "description":
                    "Gravity acts "
                    "vertically downward"
            },

            {
                "from": "f",

                "to": "block",

                "description":
                    "Friction acts "
                    "along the plane"
            }
        ],

        "properties": {

            "direction":
                "physically correct",

            "labels_required":
                True,

            "scale":
                "schematic"
        }
    }

    result = validate_diagram_plan(
        test_plan
    )

    print(
        "\nDIAGRAM VALIDATOR OUTPUT:\n"
    )

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )