# ============================================================
# AEGIE EVALUATION FEATURE BUILDER
# ============================================================
#
# Purpose:
#
# Combine:
#   1. Whole-answer MiniLM semantic evidence
#   2. Sentence-level concept semantic evidence
#   3. Objective speech features
#
# into one research feature vector.
#
# IMPORTANT:
# - These values are FEATURES.
# - They are NOT final AEGIE 1-5 scores.
# - No adaptive threshold is applied here.
# - Human annotation labels are NOT read here.
# - Human annotations will later be used for calibration
#   and scientific validation.
#
# ============================================================

import math


# ============================================================
# SAFE NUMBER CONVERSION
# ============================================================

def _safe_float(value):

    if value is None:
        return None

    try:

        number = float(value)

        if not math.isfinite(number):
            return None

        return round(
            number,
            4
        )

    except (
        TypeError,
        ValueError
    ):

        return None


def _safe_int(value):

    if value is None:
        return None

    try:

        number = int(
            value
        )

        if number < 0:
            return None

        return number

    except (
        TypeError,
        ValueError
    ):

        return None


# ============================================================
# SAFE DERIVED SPEECH FEATURES
# ============================================================

def _filler_rate_per_100_words(
    filler_count,
    word_count
):

    if (
        filler_count is None
        or word_count is None
        or word_count <= 0
    ):

        return None

    return round(
        (
            filler_count
            / word_count
        ) * 100,
        4
    )


def _pause_rate_per_minute(
    pause_count,
    duration_sec
):

    if (
        pause_count is None
        or duration_sec is None
        or duration_sec <= 0
    ):

        return None

    minutes = (
        duration_sec
        / 60.0
    )

    if minutes <= 0:
        return None

    return round(
        pause_count
        / minutes,
        4
    )


# ============================================================
# EXTRACT SEMANTIC FEATURES
# ============================================================

def _extract_semantic_features(
    semantic_evidence
):

    if not isinstance(
        semantic_evidence,
        dict
    ):

        return {
            "success": False,
            "reason": (
                "Semantic evidence must "
                "be a dictionary."
            ),
            "features": None
        }


    # --------------------------------------------------------
    # Backward compatibility
    #
    # Older development evidence sometimes contained:
    #
    # success
    # concept_count
    # mean_best_similarity
    # max_best_similarity
    # min_best_similarity
    #
    # New evidence contains:
    #
    # whole_answer
    # sentence_level
    # feature_summary
    # --------------------------------------------------------

    if (
        "success"
        in semantic_evidence
        and semantic_evidence.get(
            "success"
        ) is False
    ):

        return {
            "success": False,
            "reason": (
                "Semantic evaluation "
                "was not successful."
            ),
            "features": None
        }


    feature_summary = (
        semantic_evidence.get(
            "feature_summary"
        )
        or {}
    )


    whole_answer = (
        semantic_evidence.get(
            "whole_answer"
        )
        or {}
    )


    sentence_level = (
        semantic_evidence.get(
            "sentence_level"
        )
        or {}
    )


    # --------------------------------------------------------
    # NEW structure
    # --------------------------------------------------------

    whole_mean = _safe_float(

        feature_summary.get(
            "whole_mean_similarity",
            whole_answer.get(
                "mean_similarity"
            )
        )
    )


    whole_max = _safe_float(

        feature_summary.get(
            "whole_max_similarity",
            whole_answer.get(
                "max_similarity"
            )
        )
    )


    whole_min = _safe_float(

        feature_summary.get(
            "whole_min_similarity",
            whole_answer.get(
                "min_similarity"
            )
        )
    )


    sentence_mean = _safe_float(

        feature_summary.get(
            "sentence_mean_best_similarity",
            sentence_level.get(
                "mean_best_similarity"
            )
        )
    )


    sentence_max = _safe_float(

        feature_summary.get(
            "sentence_max_best_similarity",
            sentence_level.get(
                "max_best_similarity"
            )
        )
    )


    sentence_min = _safe_float(

        feature_summary.get(
            "sentence_min_best_similarity",
            sentence_level.get(
                "min_best_similarity"
            )
        )
    )


    concept_count = _safe_int(

        feature_summary.get(
            "reference_concept_count",
            semantic_evidence.get(
                "reference_concept_count"
            )
        )
    )


    answer_sentence_count = _safe_int(

        feature_summary.get(
            "answer_sentence_count",
            sentence_level.get(
                "sentence_count"
            )
        )
    )


    # --------------------------------------------------------
    # OLD development fallback
    # --------------------------------------------------------

    if sentence_mean is None:

        sentence_mean = _safe_float(
            semantic_evidence.get(
                "mean_best_similarity"
            )
        )


    if sentence_max is None:

        sentence_max = _safe_float(
            semantic_evidence.get(
                "max_best_similarity"
            )
        )


    if sentence_min is None:

        sentence_min = _safe_float(
            semantic_evidence.get(
                "min_best_similarity"
            )
        )


    if concept_count is None:

        concept_count = _safe_int(
            semantic_evidence.get(
                "concept_count"
            )
        )


    # --------------------------------------------------------
    # At least one semantic measurement must exist
    # --------------------------------------------------------

    semantic_values = [

        whole_mean,
        whole_max,
        whole_min,

        sentence_mean,
        sentence_max,
        sentence_min
    ]


    if all(
        value is None
        for value in semantic_values
    ):

        return {
            "success": False,
            "reason": (
                "No usable semantic "
                "similarity features were found."
            ),
            "features": None
        }


    return {

        "success": True,

        "reason": None,

        "features": {

            "whole_mean_similarity":
                whole_mean,

            "whole_max_similarity":
                whole_max,

            "whole_min_similarity":
                whole_min,

            "sentence_mean_best_similarity":
                sentence_mean,

            "sentence_max_best_similarity":
                sentence_max,

            "sentence_min_best_similarity":
                sentence_min,

            "reference_concept_count":
                concept_count,

            "answer_sentence_count":
                answer_sentence_count
        }
    }


# ============================================================
# BUILD EVALUATION FEATURE VECTOR
# ============================================================

def build_evaluation_features(
    state
):

    # --------------------------------------------------------
    # Validate state
    # --------------------------------------------------------

    if not isinstance(
        state,
        dict
    ):

        return {
            "success": False,
            "status": "INVALID_STATE",
            "reason": (
                "State must be a dictionary."
            ),
            "features": None
        }


    # --------------------------------------------------------
    # Semantic evidence
    # --------------------------------------------------------

    semantic_evidence = state.get(
        "semantic_evidence"
    )


    if not isinstance(
        semantic_evidence,
        dict
    ):

        return {
            "success": False,
            "status":
                "SEMANTIC_EVIDENCE_MISSING",
            "reason": (
                "Semantic evidence "
                "is not available."
            ),
            "features": None
        }


    semantic_result = (
        _extract_semantic_features(
            semantic_evidence
        )
    )


    if not semantic_result[
        "success"
    ]:

        return {
            "success": False,
            "status":
                "SEMANTIC_EVIDENCE_NOT_READY",
            "reason":
                semantic_result[
                    "reason"
                ],
            "features": None
        }


    semantic_features = (
        semantic_result[
            "features"
        ]
    )


    # --------------------------------------------------------
    # Current question
    # --------------------------------------------------------

    current_question = (
        state.get(
            "current_question"
        )
        or {}
    )


    # --------------------------------------------------------
    # Objective speech features
    # --------------------------------------------------------

    duration_sec = _safe_float(
        state.get(
            "duration_sec"
        )
    )


    word_count = _safe_int(
        state.get(
            "word_count"
        )
    )


    wpm = _safe_float(
        state.get(
            "wpm"
        )
    )


    filler_count = _safe_int(
        state.get(
            "filler_count"
        )
    )


    pause_count = _safe_int(
        state.get(
            "pause_count"
        )
    )


    # --------------------------------------------------------
    # Derived speech features
    #
    # These are objective numeric features.
    # They are NOT scores and no thresholds are applied.
    # --------------------------------------------------------

    filler_rate = (
        _filler_rate_per_100_words(
            filler_count,
            word_count
        )
    )


    pause_rate = (
        _pause_rate_per_minute(
            pause_count,
            duration_sec
        )
    )


    # --------------------------------------------------------
    # Construct feature vector
    # --------------------------------------------------------

    features = {

        # ====================================================
        # RESEARCH METADATA
        #
        # participant_id is metadata only.
        # It must NOT be used as a predictive feature during
        # score calibration.
        # ====================================================

        "participant_id":
            state.get(
                "participant_id"
            ),

        "job_role":
            state.get(
                "job_role"
            ),

        "question_id":
            current_question.get(
                "question_id"
            ),

        "difficulty":
            current_question.get(
                "difficulty"
            ),


        # ====================================================
        # WHOLE-ANSWER MINILM FEATURES
        # ====================================================

        "whole_mean_similarity":
            semantic_features[
                "whole_mean_similarity"
            ],

        "whole_max_similarity":
            semantic_features[
                "whole_max_similarity"
            ],

        "whole_min_similarity":
            semantic_features[
                "whole_min_similarity"
            ],


        # ====================================================
        # SENTENCE-LEVEL CONCEPT FEATURES
        # ====================================================

        "sentence_mean_best_similarity":
            semantic_features[
                "sentence_mean_best_similarity"
            ],

        "sentence_max_best_similarity":
            semantic_features[
                "sentence_max_best_similarity"
            ],

        "sentence_min_best_similarity":
            semantic_features[
                "sentence_min_best_similarity"
            ],


        # ====================================================
        # SEMANTIC STRUCTURE FEATURES
        # ====================================================

        "reference_concept_count":
            semantic_features[
                "reference_concept_count"
            ],

        "answer_sentence_count":
            semantic_features[
                "answer_sentence_count"
            ],


        # ====================================================
        # OBJECTIVE SPEECH FEATURES
        # ====================================================

        "duration_sec":
            duration_sec,

        "word_count":
            word_count,

        "wpm":
            wpm,

        "filler_count":
            filler_count,

        "pause_count":
            pause_count,


        # ====================================================
        # DERIVED OBJECTIVE SPEECH FEATURES
        # ====================================================

        "filler_rate_per_100_words":
            filler_rate,

        "pause_rate_per_minute":
            pause_rate
    }


    # --------------------------------------------------------
    # Return
    # --------------------------------------------------------

    return {

        "success": True,

        "status":
            "EVALUATION_FEATURES_READY",

        "reason":
            None,

        "features":
            features
    }


# ============================================================
# DEVELOPMENT TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 70)

    print(
        "AEGIE EVALUATION FEATURE "
        "BUILDER TEST"
    )

    print("=" * 70)


    # --------------------------------------------------------
    # Development-only state.
    #
    # Mirrors the NEW semantic_evaluator.py structure.
    #
    # This is NOT:
    # - a genuine participant record
    # - a human annotation
    # - part of the final 3000-sample dataset
    # --------------------------------------------------------

    development_state = {

        "participant_id":
            "DEV_TEST",

        "job_role":
            "Cybersecurity Analyst",

        "current_question": {

            "question_id":
                "CS_E02",

            "difficulty":
                "Easy",

            "question_text":
                (
                    "What is the difference between "
                    "authentication and authorization?"
                )
        },


        # ----------------------------------------------------
        # Objective speech features
        # ----------------------------------------------------

        "duration_sec":
            20.0,

        "word_count":
            43,

        "wpm":
            129.0,

        "filler_count":
            1,

        "pause_count":
            2,


        # ----------------------------------------------------
        # NEW semantic evidence structure
        # ----------------------------------------------------

        "semantic_evidence": {

            "question_id":
                "CS_E02",

            "reference_role":
                "Cybersecurity Analyst",

            "reference_concept_count":
                4,


            "whole_answer": {

                "status":
                    "SEMANTIC_EVIDENCE_READY",

                "mean_similarity":
                    0.6576,

                "max_similarity":
                    0.7871,

                "min_similarity":
                    0.5261,

                "concept_results":
                    []
            },


            "sentence_level": {

                "status":
                    (
                        "SENTENCE_CONCEPT_"
                        "EVIDENCE_READY"
                    ),

                "sentence_count":
                    4,

                "mean_best_similarity":
                    0.8373,

                "max_best_similarity":
                    0.9262,

                "min_best_similarity":
                    0.7126,

                "concept_results":
                    []
            },


            "feature_summary": {

                "whole_mean_similarity":
                    0.6576,

                "whole_max_similarity":
                    0.7871,

                "whole_min_similarity":
                    0.5261,

                "sentence_mean_best_similarity":
                    0.8373,

                "sentence_max_best_similarity":
                    0.9262,

                "sentence_min_best_similarity":
                    0.7126,

                "reference_concept_count":
                    4,

                "answer_sentence_count":
                    4
            }
        }
    }


    # --------------------------------------------------------
    # Build feature vector
    # --------------------------------------------------------

    result = (
        build_evaluation_features(
            development_state
        )
    )


    print()

    print(
        "Success:",
        result[
            "success"
        ]
    )


    print(
        "Status:",
        result[
            "status"
        ]
    )


    print(
        "Reason:",
        result[
            "reason"
        ]
    )


    # --------------------------------------------------------
    # Print features
    # --------------------------------------------------------

    if result[
        "success"
    ]:

        print()

        print("-" * 70)

        print(
            "AEGIE RESEARCH FEATURE VECTOR"
        )

        print("-" * 70)


        for key, value in (
            result[
                "features"
            ].items()
        ):

            print(
                f"{key}: {value}"
            )


    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    print()

    print("=" * 70)


    if result[
        "success"
    ]:

        print(
            "PASS: Evaluation feature "
            "vector generated."
        )

    else:

        print(
            "FAIL: Evaluation feature "
            "vector was not generated."
        )


    print("=" * 70)


    print()

    print(
        "Whole-answer semantic "
        "features included: YES"
    )

    print(
        "Sentence-level semantic "
        "features included: YES"
    )

    print(
        "Objective speech "
        "features included: YES"
    )

    print(
        "Derived speech "
        "features included: YES"
    )

    print(
        "Human annotation labels used: NO"
    )

    print(
        "Final AEGIE 1-5 scores "
        "generated: NO"
    )

    print(
        "Adaptive difficulty "
        "threshold applied: NO"
    )

    print()

    print(
        "NOTE: participant_id is research "
        "metadata only and must not be used "
        "as a predictive calibration feature."
    )

    print(
        "No development record was added "
        "to the 3000-sample dataset."
    )