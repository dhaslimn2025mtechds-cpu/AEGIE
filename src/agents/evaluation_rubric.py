# ============================================================
# AEGIE MACHINE EVALUATION RUBRIC
# ============================================================
#
# Scale: 1 to 5
#
# This rubric defines how the AEGIE Evaluation Agent should
# interpret each evaluation dimension.
#
# IMPORTANT:
# These are SYSTEM evaluation criteria.
# Human reference annotations remain separately stored.
# ============================================================


EVALUATION_RUBRIC = {

    # ========================================================
    # 1. RELEVANCE
    # ========================================================

    "relevance": {

        1: (
            "The response is unrelated to the question "
            "or does not answer it."
        ),

        2: (
            "The response has limited connection to the "
            "question and misses most important points."
        ),

        3: (
            "The response partially answers the question "
            "but important information is missing."
        ),

        4: (
            "The response directly addresses the question "
            "and covers most important points."
        ),

        5: (
            "The response directly and completely answers "
            "the question with highly relevant information."
        )
    },


    # ========================================================
    # 2. TECHNICAL CORRECTNESS
    # ========================================================

    "technical": {

        1: (
            "The response is technically incorrect or "
            "contains fundamental errors."
        ),

        2: (
            "The response contains major technical errors "
            "with only limited correct information."
        ),

        3: (
            "The response is partially correct but contains "
            "missing or inaccurate technical details."
        ),

        4: (
            "The response is mostly technically correct "
            "with only minor omissions or inaccuracies."
        ),

        5: (
            "The response is technically correct, complete, "
            "and appropriately explained."
        )
    },


    # ========================================================
    # 3. CLARITY
    # ========================================================

    "clarity": {

        1: (
            "The response is very difficult to understand "
            "and lacks a clear structure."
        ),

        2: (
            "The response is frequently unclear or "
            "poorly organized."
        ),

        3: (
            "The response is understandable but has "
            "noticeable structural or clarity problems."
        ),

        4: (
            "The response is clear and reasonably "
            "well structured."
        ),

        5: (
            "The response is very clear, concise, "
            "well organized, and easy to follow."
        )
    },


    # ========================================================
    # 4. COMMUNICATION QUALITY
    # ========================================================

    "communication": {

        1: (
            "Communication problems seriously interfere "
            "with understanding the response."
        ),

        2: (
            "Frequent communication difficulties reduce "
            "the effectiveness of the response."
        ),

        3: (
            "Communication is adequate and the response "
            "can generally be understood."
        ),

        4: (
            "Communication is effective, understandable, "
            "and appropriate for an interview response."
        ),

        5: (
            "Communication is highly effective, clear, "
            "professional, and easy to understand."
        )
    },


    # ========================================================
    # 5. OVERALL ANSWER QUALITY
    # ========================================================

    "overall": {

        1: "Very poor response.",

        2: "Weak response.",

        3: "Acceptable response.",

        4: "Good response.",

        5: "Excellent response."
    }
}


# ============================================================
# RETURN RUBRIC
# ============================================================

def get_evaluation_rubric():

    return EVALUATION_RUBRIC


# ============================================================
# GET ONE DIMENSION
# ============================================================

def get_dimension(dimension):

    return EVALUATION_RUBRIC.get(
        dimension
    )


# ============================================================
# VALIDATE RUBRIC
# ============================================================

def validate_rubric():

    required_dimensions = [

        "relevance",
        "technical",
        "clarity",
        "communication",
        "overall"
    ]

    required_scores = {
        1, 2, 3, 4, 5
    }


    for dimension in required_dimensions:

        if dimension not in EVALUATION_RUBRIC:

            return False, (
                f"Missing dimension: "
                f"{dimension}"
            )


        scores = set(
            EVALUATION_RUBRIC[
                dimension
            ].keys()
        )


        if scores != required_scores:

            return False, (
                f"Invalid score levels "
                f"for {dimension}"
            )


    return True, "Rubric structure is valid."


# ============================================================
# DEVELOPMENT TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 65)
    print("AEGIE EVALUATION RUBRIC")
    print("=" * 65)


    valid, message = validate_rubric()


    print()
    print(
        "Rubric Valid:",
        valid
    )

    print(
        "Status:",
        message
    )


    print()
    print("=" * 65)


    for dimension, levels in (
        EVALUATION_RUBRIC.items()
    ):

        print()
        print(
            dimension.upper()
        )

        print("-" * 65)


        for score, description in (
            levels.items()
        ):

            print(
                f"{score}: {description}"
            )


    print()
    print("=" * 65)
    print("RUBRIC TEST COMPLETE")
    print("=" * 65)