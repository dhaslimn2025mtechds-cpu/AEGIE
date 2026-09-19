# ============================================================
# AEGIE REUSABLE ROLE REFERENCE VALIDATOR
# ============================================================
#
# Validates semantic reference knowledge against the
# original AEGIE question banks.
#
# Supported roles:
# 1. Data Scientist
# 2. Software Developer
# 3. Data Analyst
# 4. Machine Learning Engineer
# 5. Cloud DevOps Engineer
# 6. Cybersecurity Analyst
#
# This script does NOT modify participant data.
# ============================================================

import os
import sys
import pandas as pd


# ============================================================
# LOCAL IMPORT PATH
# ============================================================

CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)


# ============================================================
# REFERENCE IMPORTS
# ============================================================

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
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)


# ============================================================
# ROLE CONFIGURATION
# ============================================================

ROLE_CONFIG = {

    "Data Scientist": {
        "file": "data_scientist.csv",
        "references": REFERENCE_ANSWERS,
        "prefix": "DS"
    },

    "Software Developer": {
        "file": "software_developer.csv",
        "references": SOFTWARE_DEVELOPER_REFERENCES,
        "prefix": "SD"
    },

    "Data Analyst": {
        "file": "data_analyst.csv",
        "references": DATA_ANALYST_REFERENCES,
        "prefix": "DA"
    },

    "Machine Learning Engineer": {
        "file": "ml_engineer.csv",
        "references": MACHINE_LEARNING_ENGINEER_REFERENCES,
        "prefix": "MLE"
    },

    "Cloud DevOps Engineer": {
        "file": "cloud_devops.csv",
        "references": CLOUD_DEVOPS_ENGINEER_REFERENCES,
        "prefix": "CD"
    },

    "Cybersecurity Analyst": {
        "file": "cybersecurity_analyst.csv",
        "references": CYBERSECURITY_ANALYST_REFERENCES,
        "prefix": "CS"
    }
}


# ============================================================
# VALIDATION SETTINGS
# ============================================================

VALID_DIFFICULTIES = {
    "Easy",
    "Medium",
    "Hard"
}

REQUIRED_COLUMNS = {
    "question_id",
    "job_role",
    "difficulty",
    "question_text"
}

EXPECTED_QUESTION_COUNT = 12


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(text):

    if text is None:
        return ""

    return " ".join(
        str(text).strip().split()
    )


# ============================================================
# VALIDATE ONE ROLE
# ============================================================

def validate_role(role_name):

    errors = []

    if role_name not in ROLE_CONFIG:

        return {
            "valid": False,
            "errors": [
                f"Unsupported role: {role_name}"
            ]
        }

    config = ROLE_CONFIG[role_name]

    question_bank_path = os.path.join(
        PROJECT_ROOT,
        "data",
        "question_bank",
        config["file"]
    )

    references = config["references"]
    prefix = config["prefix"]


    print()
    print("=" * 70)
    print(f"VALIDATING: {role_name}")
    print("=" * 70)

    print()
    print("Question bank:")
    print(question_bank_path)


    # --------------------------------------------------------
    # File check
    # --------------------------------------------------------

    if not os.path.exists(question_bank_path):

        errors.append(
            "Question bank file does not exist."
        )

        return {
            "valid": False,
            "errors": errors
        }


    # --------------------------------------------------------
    # Read CSV
    # --------------------------------------------------------

    try:

        df = pd.read_csv(
            question_bank_path
        )

    except Exception as error:

        errors.append(
            "Could not read question bank: "
            + str(error)
        )

        return {
            "valid": False,
            "errors": errors
        }


    # --------------------------------------------------------
    # Required columns
    # --------------------------------------------------------

    missing_columns = (
        REQUIRED_COLUMNS
        - set(df.columns)
    )

    if missing_columns:

        errors.append(
            "Missing columns: "
            + ", ".join(
                sorted(missing_columns)
            )
        )

        return {
            "valid": False,
            "errors": errors
        }


    # --------------------------------------------------------
    # Filter exact role
    # --------------------------------------------------------

    role_df = df[
        df["job_role"]
        .astype(str)
        .str.strip()
        == role_name
    ].copy()


    print()

    print(
        "Question-bank entries:",
        len(role_df)
    )

    print(
        "Reference entries:",
        len(references)
    )


    # --------------------------------------------------------
    # Expected counts
    # --------------------------------------------------------

    if len(role_df) != EXPECTED_QUESTION_COUNT:

        errors.append(
            f"Expected {EXPECTED_QUESTION_COUNT} "
            f"questions but found {len(role_df)}."
        )


    if len(references) != EXPECTED_QUESTION_COUNT:

        errors.append(
            f"Expected {EXPECTED_QUESTION_COUNT} "
            f"references but found {len(references)}."
        )


    # --------------------------------------------------------
    # Duplicate question IDs
    # --------------------------------------------------------

    duplicate_rows = role_df[
        role_df["question_id"].duplicated(
            keep=False
        )
    ]


    if not duplicate_rows.empty:

        duplicate_ids = sorted(
            duplicate_rows[
                "question_id"
            ]
            .astype(str)
            .unique()
        )

        errors.append(
            "Duplicate question IDs: "
            + ", ".join(duplicate_ids)
        )


    # --------------------------------------------------------
    # Compare question IDs
    # --------------------------------------------------------

    bank_ids = set(
        role_df[
            "question_id"
        ]
        .astype(str)
        .str.strip()
    )


    reference_ids = set(
        references.keys()
    )


    missing_references = (
        bank_ids
        - reference_ids
    )


    extra_references = (
        reference_ids
        - bank_ids
    )


    if missing_references:

        errors.append(
            "Missing reference IDs: "
            + ", ".join(
                sorted(missing_references)
            )
        )


    if extra_references:

        errors.append(
            "Unexpected reference IDs: "
            + ", ".join(
                sorted(extra_references)
            )
        )


    # --------------------------------------------------------
    # Validate every question/reference pair
    # --------------------------------------------------------

    for _, row in role_df.iterrows():

        question_id = str(
            row["question_id"]
        ).strip()


        difficulty = str(
            row["difficulty"]
        ).strip()


        bank_question = normalize_text(
            row["question_text"]
        )


        # ----------------------------------------------------
        # Prefix
        # ----------------------------------------------------

        if not question_id.startswith(
            prefix + "_"
        ):

            errors.append(
                f"{question_id}: expected "
                f"prefix {prefix}_"
            )


        # ----------------------------------------------------
        # Difficulty
        # ----------------------------------------------------

        if difficulty not in VALID_DIFFICULTIES:

            errors.append(
                f"{question_id}: invalid "
                f"difficulty '{difficulty}'."
            )


        # ----------------------------------------------------
        # Reference lookup
        # ----------------------------------------------------

        reference = references.get(
            question_id
        )


        if reference is None:
            continue


        reference_question = normalize_text(
            reference.get(
                "question"
            )
        )


        # ----------------------------------------------------
        # Question mapping
        # ----------------------------------------------------

        if bank_question != reference_question:

            errors.append(
                f"{question_id}: question text "
                "does not match reference."
            )

            print()

            print(
                f"[QUESTION MISMATCH] {question_id}"
            )

            print("Bank:")
            print(bank_question)

            print("Reference:")
            print(reference_question)


        # ----------------------------------------------------
        # Concepts
        # ----------------------------------------------------

        concepts = reference.get(
            "key_concepts"
        )


        if (
            not isinstance(concepts, list)
            or len(concepts) == 0
        ):

            errors.append(
                f"{question_id}: invalid "
                "key_concepts."
            )


        # ----------------------------------------------------
        # Examples
        # ----------------------------------------------------

        examples = reference.get(
            "acceptable_examples"
        )


        if not isinstance(
            examples,
            list
        ):

            errors.append(
                f"{question_id}: invalid "
                "acceptable_examples."
            )


    # --------------------------------------------------------
    # Difficulty distribution
    # --------------------------------------------------------

    print()
    print("-" * 70)
    print("DIFFICULTY DISTRIBUTION")
    print("-" * 70)


    counts = (
        role_df["difficulty"]
        .astype(str)
        .str.strip()
        .value_counts()
    )


    for difficulty in [
        "Easy",
        "Medium",
        "Hard"
    ]:

        count = int(
            counts.get(
                difficulty,
                0
            )
        )

        print(
            f"{difficulty}: {count}"
        )


        if count != 4:

            errors.append(
                f"Expected 4 {difficulty} "
                f"questions but found {count}."
            )


    # --------------------------------------------------------
    # Return
    # --------------------------------------------------------

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("AEGIE ROLE REFERENCE VALIDATOR")
    print("=" * 70)


    roles_to_validate = [

        "Data Scientist",
        "Software Developer",
        "Data Analyst",
        "Machine Learning Engineer",
        "Cloud DevOps Engineer",
        "Cybersecurity Analyst"

    ]


    overall_valid = True
    validated_reference_count = 0


    # --------------------------------------------------------
    # Validate every role
    # --------------------------------------------------------

    for role in roles_to_validate:

        result = validate_role(
            role
        )

        print()


        if result["valid"]:

            print(
                f"PASS: {role} reference "
                "mapping is valid."
            )

            validated_reference_count += (
                EXPECTED_QUESTION_COUNT
            )


        else:

            overall_valid = False

            print(
                f"FAIL: {role} reference "
                "mapping has errors."
            )


            for error in result["errors"]:

                print(
                    "-",
                    error
                )


    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print()
    print("=" * 70)
    print("FINAL VALIDATION RESULT")
    print("=" * 70)


    if overall_valid:

        print()

        print(
            "PASS: ALL SIX ROLE REFERENCE "
            "MAPPINGS ARE VALID."
        )

        print()

        print(
            "Validated roles:",
            len(roles_to_validate),
            "/ 6"
        )

        print(
            "Validated references:",
            validated_reference_count,
            "/ 72"
        )

        print()

        print(
            "AEGIE semantic reference coverage: 100%"
        )


    else:

        print()

        print(
            "FAIL: One or more role "
            "reference mappings contain errors."
        )


    print()

    print(
        "No participant data was modified."
    )

    print(
        "No participant-study samples were added."
    )

    print(
        "Semantic references require expert "
        "review before the final research experiment."
    )

    print("=" * 70)