# ============================================================
# AEGIE EVALUATION SCHEMA
# ============================================================
#
# Defines the input/output contract for the Evaluation Agent.
#
# IMPORTANT:
# - AEGIE scores are SYSTEM PREDICTIONS.
# - Human annotations are separate reference labels.
# - This module does NOT generate scores.
# ============================================================


VALID_SCORE_MIN = 1
VALID_SCORE_MAX = 5


# ============================================================
# CREATE EVALUATION INPUT
# ============================================================

def create_evaluation_input(state):

    question = state.get(
        "current_question"
    )

    if not question:

        return {
            "ready": False,
            "reason": "Question unavailable.",
            "data": None
        }


    transcript = state.get(
        "transcript"
    )


    if not transcript:

        return {
            "ready": False,
            "reason": "Transcript unavailable.",
            "data": None
        }


    evaluation_input = {

        "participant_id":
            state.get("participant_id"),

        "job_role":
            state.get("job_role"),

        "question_id":
            question.get("question_id"),

        "question_text":
            question.get("question_text"),

        "difficulty":
            question.get("difficulty"),

        "transcript":
            transcript,

        "duration_sec":
            state.get("duration_sec"),

        "word_count":
            state.get("word_count"),

        "wpm":
            state.get("wpm"),

        "filler_count":
            state.get("filler_count"),

        "pause_count":
            state.get("pause_count")
    }


    return {
        "ready": True,
        "reason": None,
        "data": evaluation_input
    }


# ============================================================
# VALIDATE AEGIE PREDICTIONS
# ============================================================

def validate_aegie_scores(scores):

    required_scores = [

        "relevance_score",

        "technical_score",

        "clarity_score",

        "communication_score",

        "overall_score"
    ]


    if not isinstance(
        scores,
        dict
    ):

        return {
            "valid": False,
            "reason": (
                "Evaluation output "
                "must be a dictionary."
            )
        }


    for score_name in required_scores:

        if score_name not in scores:

            return {
                "valid": False,
                "reason": (
                    f"Missing score: "
                    f"{score_name}"
                )
            }


        value = scores[
            score_name
        ]


        # Do not accept Boolean because
        # bool is a subclass of int in Python.

        if isinstance(value, bool):

            return {
                "valid": False,
                "reason": (
                    f"{score_name} "
                    f"cannot be Boolean."
                )
            }


        if not isinstance(
            value,
            (int, float)
        ):

            return {
                "valid": False,
                "reason": (
                    f"{score_name} "
                    f"must be numeric."
                )
            }


        if not (
            VALID_SCORE_MIN
            <= value
            <= VALID_SCORE_MAX
        ):

            return {
                "valid": False,
                "reason": (
                    f"{score_name} must "
                    f"be between 1 and 5."
                )
            }


    return {
        "valid": True,
        "reason": None
    }


# ============================================================
# MAP SYSTEM SCORES TO DATASET COLUMNS
# ============================================================

def map_scores_to_dataset(scores):

    validation = validate_aegie_scores(
        scores
    )


    if not validation["valid"]:

        raise ValueError(
            validation["reason"]
        )


    return {

        "aegie_relevance_score":
            scores["relevance_score"],

        "aegie_technical_score":
            scores["technical_score"],

        "aegie_clarity_score":
            scores["clarity_score"],

        "aegie_communication_score":
            scores["communication_score"],

        "aegie_overall_score":
            scores["overall_score"]
    }


# ============================================================
# DEVELOPMENT TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 65)
    print("AEGIE EVALUATION SCHEMA TEST")
    print("=" * 65)


    # --------------------------------------------------------
    # Test state intentionally has no transcript.
    # --------------------------------------------------------

    test_state = {

        "participant_id":
            "P001",

        "job_role":
            "Data Scientist",

        "current_question": {

            "question_id":
                "DS_E02",

            "question_text":
                "What is overfitting in machine learning?",

            "difficulty":
                "Easy"
        },

        "transcript":
            None,

        "duration_sec":
            15.37,

        "word_count":
            None,

        "wpm":
            None,

        "filler_count":
            None,

        "pause_count":
            1
    }


    result = create_evaluation_input(
        test_state
    )


    print()
    print(
        "Evaluation Ready:",
        result["ready"]
    )

    print(
        "Reason:",
        result["reason"]
    )


    # --------------------------------------------------------
    # Validate deliberately invalid test scores.
    #
    # These values are ONLY validator test inputs.
    # They are NOT participant evaluation results.
    # --------------------------------------------------------

    test_scores = {

        "relevance_score": 4,

        "technical_score": 6,

        "clarity_score": 4,

        "communication_score": 4,

        "overall_score": 4
    }


    validation = validate_aegie_scores(
        test_scores
    )


    print()
    print("SCORE VALIDATION TEST")

    print(
        "Valid:",
        validation["valid"]
    )

    print(
        "Reason:",
        validation["reason"]
    )


    print()
    print("=" * 65)
    print("SCHEMA TEST COMPLETE")
    print("=" * 65)