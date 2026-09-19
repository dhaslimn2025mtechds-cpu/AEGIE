# ============================================================
# AEGIE CENTRAL SEMANTIC REFERENCE REGISTRY
# ============================================================
#
# Combines semantic reference knowledge for all six
# interview roles into one lookup registry.
#
# IMPORTANT:
# - These are NOT participant responses.
# - These are NOT human annotation labels.
# - These are NOT primary dataset samples.
# - They are reference concepts used by the AEGIE
#   semantic evaluation pipeline.
# ============================================================


# ============================================================
# PACKAGE-SAFE IMPORTS
# ============================================================

try:

    from .reference_answers import (
        REFERENCE_ANSWERS
    )

    from .software_developer_references import (
        SOFTWARE_DEVELOPER_REFERENCES
    )

    from .data_analyst_references import (
        DATA_ANALYST_REFERENCES
    )

    from .ml_engineer_references import (
        MACHINE_LEARNING_ENGINEER_REFERENCES
    )

    from .cloud_devops_references import (
        CLOUD_DEVOPS_ENGINEER_REFERENCES
    )

    from .cybersecurity_analyst_references import (
        CYBERSECURITY_ANALYST_REFERENCES
    )

except ImportError:

    from reference_answers import (
        REFERENCE_ANSWERS
    )

    from software_developer_references import (
        SOFTWARE_DEVELOPER_REFERENCES
    )

    from data_analyst_references import (
        DATA_ANALYST_REFERENCES
    )

    from ml_engineer_references import (
        MACHINE_LEARNING_ENGINEER_REFERENCES
    )

    from cloud_devops_references import (
        CLOUD_DEVOPS_ENGINEER_REFERENCES
    )

    from cybersecurity_analyst_references import (
        CYBERSECURITY_ANALYST_REFERENCES
    )


# ============================================================
# ROLE REFERENCE COLLECTIONS
# ============================================================

ROLE_REFERENCE_COLLECTIONS = {

    "Data Scientist":
        REFERENCE_ANSWERS,

    "Software Developer":
        SOFTWARE_DEVELOPER_REFERENCES,

    "Data Analyst":
        DATA_ANALYST_REFERENCES,

    "Machine Learning Engineer":
        MACHINE_LEARNING_ENGINEER_REFERENCES,

    "Cloud DevOps Engineer":
        CLOUD_DEVOPS_ENGINEER_REFERENCES,

    "Cybersecurity Analyst":
        CYBERSECURITY_ANALYST_REFERENCES
}


# ============================================================
# BUILD CENTRAL REGISTRY
# ============================================================

ALL_REFERENCES = {}

DUPLICATE_IDS = []


for role_name, references in (
    ROLE_REFERENCE_COLLECTIONS.items()
):

    for question_id, reference in references.items():

        if question_id in ALL_REFERENCES:

            DUPLICATE_IDS.append(
                question_id
            )

            continue

        # Copy reference so original dictionaries
        # are not modified.
        reference_copy = dict(
            reference
        )

        # Add metadata for central lookup.
        reference_copy["job_role"] = (
            role_name
        )

        reference_copy["question_id"] = (
            question_id
        )

        ALL_REFERENCES[
            question_id
        ] = reference_copy


# ============================================================
# LOOKUP FUNCTIONS
# ============================================================

def get_reference_answer(question_id):
    """
    Return the semantic reference for a question ID.

    Returns:
        dict if found
        None if question ID is unknown
    """

    if not question_id:
        return None

    clean_id = str(
        question_id
    ).strip()

    return ALL_REFERENCES.get(
        clean_id
    )


def get_reference_by_role(
    job_role
):
    """
    Return all references belonging to one role.
    """

    if not job_role:
        return {}

    clean_role = str(
        job_role
    ).strip()

    references = (
        ROLE_REFERENCE_COLLECTIONS.get(
            clean_role
        )
    )

    if references is None:
        return {}

    return references


def get_all_references():
    """
    Return the complete 72-question reference registry.
    """

    return ALL_REFERENCES


def has_reference(question_id):
    """
    Check whether a reference exists for a question ID.
    """

    if not question_id:
        return False

    return (
        str(question_id).strip()
        in ALL_REFERENCES
    )


def get_reference_count():
    """
    Return total number of central references.
    """

    return len(
        ALL_REFERENCES
    )


# ============================================================
# VALIDATION
# ============================================================

def validate_reference_registry():

    errors = []

    expected_total = 72

    expected_role_count = 6

    expected_per_role = 12


    # --------------------------------------------------------
    # Duplicate IDs
    # --------------------------------------------------------

    if DUPLICATE_IDS:

        errors.append(
            "Duplicate question IDs found: "
            + ", ".join(
                sorted(
                    set(DUPLICATE_IDS)
                )
            )
        )


    # --------------------------------------------------------
    # Total role count
    # --------------------------------------------------------

    if (
        len(ROLE_REFERENCE_COLLECTIONS)
        != expected_role_count
    ):

        errors.append(
            "Expected "
            f"{expected_role_count} roles "
            "but found "
            f"{len(ROLE_REFERENCE_COLLECTIONS)}."
        )


    # --------------------------------------------------------
    # Per-role count
    # --------------------------------------------------------

    for role_name, references in (
        ROLE_REFERENCE_COLLECTIONS.items()
    ):

        if (
            len(references)
            != expected_per_role
        ):

            errors.append(
                f"{role_name}: expected "
                f"{expected_per_role} references "
                f"but found {len(references)}."
            )


    # --------------------------------------------------------
    # Total references
    # --------------------------------------------------------

    if len(ALL_REFERENCES) != expected_total:

        errors.append(
            f"Expected {expected_total} unique "
            f"references but found "
            f"{len(ALL_REFERENCES)}."
        )


    # --------------------------------------------------------
    # Required fields
    # --------------------------------------------------------

    for question_id, reference in (
        ALL_REFERENCES.items()
    ):

        if not reference.get(
            "question"
        ):

            errors.append(
                f"{question_id}: "
                "question is missing."
            )


        concepts = reference.get(
            "key_concepts"
        )

        if (
            not isinstance(
                concepts,
                list
            )
            or len(concepts) == 0
        ):

            errors.append(
                f"{question_id}: "
                "key_concepts are invalid."
            )


        examples = reference.get(
            "acceptable_examples"
        )

        if not isinstance(
            examples,
            list
        ):

            errors.append(
                f"{question_id}: "
                "acceptable_examples "
                "must be a list."
            )


        if not reference.get(
            "job_role"
        ):

            errors.append(
                f"{question_id}: "
                "job_role metadata missing."
            )


        if (
            reference.get(
                "question_id"
            )
            != question_id
        ):

            errors.append(
                f"{question_id}: "
                "question_id metadata mismatch."
            )


    return {
        "valid": (
            len(errors) == 0
        ),
        "role_count": len(
            ROLE_REFERENCE_COLLECTIONS
        ),
        "reference_count": len(
            ALL_REFERENCES
        ),
        "errors": errors
    }


# ============================================================
# DEVELOPMENT TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 70)

    print(
        "AEGIE CENTRAL REFERENCE REGISTRY"
    )

    print("=" * 70)


    result = (
        validate_reference_registry()
    )


    print()

    print(
        "Registered roles:",
        result["role_count"]
    )

    print(
        "Registered references:",
        result["reference_count"]
    )

    print(
        "Valid:",
        result["valid"]
    )


    print()
    print("-" * 70)
    print("ROLE COUNTS")
    print("-" * 70)


    for role_name, references in (
        ROLE_REFERENCE_COLLECTIONS.items()
    ):

        print(
            f"{role_name}: "
            f"{len(references)}"
        )


    print()
    print("-" * 70)
    print("LOOKUP TESTS")
    print("-" * 70)


    test_question_ids = [
        "DS_E01",
        "SD_E01",
        "DA_E01",
        "MLE_E01",
        "CD_E01",
        "CS_E01"
    ]


    for question_id in (
        test_question_ids
    ):

        reference = (
            get_reference_answer(
                question_id
            )
        )

        if reference:

            print(
                f"[PASS] {question_id}"
                f" -> "
                f"{reference['job_role']}"
            )

        else:

            print(
                f"[FAIL] {question_id}"
            )


    print()
    print("-" * 70)
    print("FINAL RESULT")
    print("-" * 70)


    if result["valid"]:

        print(
            "PASS: Central reference "
            "registry is valid."
        )

        print(
            "PASS: All 72 semantic "
            "references are accessible."
        )

    else:

        print(
            "FAIL: Reference registry "
            "contains errors."
        )

        for error in result["errors"]:

            print(
                "-",
                error
            )


    print()

    print(
        "No participant data was modified."
    )

    print(
        "No human annotation labels "
        "were modified."
    )

    print(
        "No samples were added to the "
        "3000-sample research dataset."
    )

    print("=" * 70)