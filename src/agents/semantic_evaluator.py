# ============================================================
# AEGIE SEMANTIC EVALUATION AGENT
# ============================================================
#
# Purpose:
# Prepare semantic evaluation evidence for the AEGIE
# Evaluation Agent.
#
# Current pipeline:
#
# Question + Transcript
#        ↓
# Central 72-Question Reference Registry
#        ↓
# Whole-Answer Concept Similarity
#        +
# Sentence-Level Concept Similarity
#        ↓
# Semantic Evidence
#
# IMPORTANT:
# - Human annotation labels are NEVER read here.
# - Semantic similarity is NOT a final 1-5 score.
# - No arbitrary adaptive threshold is applied here.
# - Final score calibration must later use genuine
#   human-annotated research data.
# ============================================================


# ============================================================
# PACKAGE-SAFE IMPORTS
# ============================================================

try:

    from .reference_registry import (
        get_reference_answer
    )

    from .evaluation_schema import (
        create_evaluation_input,
        validate_aegie_scores
    )

    from .evaluation_rubric import (
        get_evaluation_rubric
    )

    from .concept_evaluator import (
        ConceptEvaluator
    )

    from .sentence_concept_evaluator import (
        SentenceConceptEvaluator
    )

except ImportError:

    from reference_registry import (
        get_reference_answer
    )

    from evaluation_schema import (
        create_evaluation_input,
        validate_aegie_scores
    )

    from evaluation_rubric import (
        get_evaluation_rubric
    )

    from concept_evaluator import (
        ConceptEvaluator
    )

    from sentence_concept_evaluator import (
        SentenceConceptEvaluator
    )


# ============================================================
# LAZY EVALUATOR CACHE
# ============================================================
#
# MiniLM is loaded only when semantic evidence is actually
# required.
#
# These evaluator objects are then reused during the process.
# ============================================================

_CONCEPT_EVALUATOR = None
_SENTENCE_CONCEPT_EVALUATOR = None


def get_concept_evaluator():

    global _CONCEPT_EVALUATOR

    if _CONCEPT_EVALUATOR is None:

        _CONCEPT_EVALUATOR = (
            ConceptEvaluator()
        )

    return _CONCEPT_EVALUATOR


def get_sentence_concept_evaluator():

    global _SENTENCE_CONCEPT_EVALUATOR

    if _SENTENCE_CONCEPT_EVALUATOR is None:

        _SENTENCE_CONCEPT_EVALUATOR = (
            SentenceConceptEvaluator()
        )

    return _SENTENCE_CONCEPT_EVALUATOR


# ============================================================
# EMPTY FAILURE RESPONSE
# ============================================================

def build_failure_response(
    status,
    reason
):

    return {
        "ready": False,
        "status": status,
        "reason": reason,
        "evaluation_context": None,
        "semantic_evidence": None,
        "scores": None
    }


# ============================================================
# PREPARE SEMANTIC EVALUATION
# ============================================================

def prepare_semantic_evaluation(
    state,
    generate_semantic_evidence=True
):

    # --------------------------------------------------------
    # 1. Validate basic evaluation input
    # --------------------------------------------------------

    input_result = (
        create_evaluation_input(
            state
        )
    )


    if not input_result["ready"]:

        return build_failure_response(
            status="WAITING_FOR_INPUT",
            reason=input_result["reason"]
        )


    evaluation_data = input_result[
        "data"
    ]


    # --------------------------------------------------------
    # 2. Question ID
    # --------------------------------------------------------

    question_id = evaluation_data[
        "question_id"
    ]


    if question_id is None:

        return build_failure_response(
            status="QUESTION_ID_MISSING",
            reason="Question ID is unavailable."
        )


    question_id = str(
        question_id
    ).strip()


    if not question_id:

        return build_failure_response(
            status="QUESTION_ID_EMPTY",
            reason="Question ID is empty."
        )


    # --------------------------------------------------------
    # 3. Retrieve reference from CENTRAL REGISTRY
    #
    # Covers:
    # - Data Scientist
    # - Software Developer
    # - Data Analyst
    # - Machine Learning Engineer
    # - Cloud DevOps Engineer
    # - Cybersecurity Analyst
    #
    # Total: 72 references
    # --------------------------------------------------------

    reference = get_reference_answer(
        question_id
    )


    if reference is None:

        return build_failure_response(
            status="REFERENCE_NOT_FOUND",
            reason=(
                f"No semantic reference "
                f"found for {question_id}."
            )
        )


    # --------------------------------------------------------
    # 4. Evaluation rubric
    # --------------------------------------------------------

    rubric = (
        get_evaluation_rubric()
    )


    # --------------------------------------------------------
    # 5. Speech features
    # --------------------------------------------------------

    speech_features = {

        "duration_sec":
            evaluation_data.get(
                "duration_sec"
            ),

        "word_count":
            evaluation_data.get(
                "word_count"
            ),

        "wpm":
            evaluation_data.get(
                "wpm"
            ),

        "filler_count":
            evaluation_data.get(
                "filler_count"
            ),

        "pause_count":
            evaluation_data.get(
                "pause_count"
            )
    }


    # --------------------------------------------------------
    # 6. Build evaluation context
    # --------------------------------------------------------

    context = {

        "question_id":
            question_id,

        "job_role":
            reference.get(
                "job_role"
            ),

        "question_text":
            evaluation_data[
                "question_text"
            ],

        "difficulty":
            evaluation_data[
                "difficulty"
            ],

        "participant_transcript":
            evaluation_data[
                "transcript"
            ],

        "reference_question":
            reference.get(
                "question"
            ),

        "reference_key_concepts":
            reference.get(
                "key_concepts",
                []
            ),

        "acceptable_examples":
            reference.get(
                "acceptable_examples",
                []
            ),

        "speech_features":
            speech_features,

        "rubric":
            rubric
    }


    # --------------------------------------------------------
    # 7. Context-only mode
    #
    # Useful later if another component needs the prepared
    # context without running MiniLM.
    # --------------------------------------------------------

    if not generate_semantic_evidence:

        return {

            "ready": True,

            "status":
                "READY_FOR_SEMANTIC_MODEL",

            "reason":
                None,

            "evaluation_context":
                context,

            "semantic_evidence":
                None,

            "scores":
                None
        }


    # --------------------------------------------------------
    # 8. Whole-answer semantic evidence
    # --------------------------------------------------------

    try:

        concept_evaluator = (
            get_concept_evaluator()
        )

        whole_answer_result = (
            concept_evaluator.evaluate(
                question_id=
                    question_id,

                transcript=
                    evaluation_data[
                        "transcript"
                    ]
            )
        )

    except Exception as error:

        return build_failure_response(
            status=(
                "WHOLE_ANSWER_EVALUATION_ERROR"
            ),
            reason=str(error)
        )


    if not whole_answer_result.get(
        "success"
    ):

        return build_failure_response(
            status=whole_answer_result.get(
                "status",
                "WHOLE_ANSWER_EVALUATION_FAILED"
            ),
            reason=whole_answer_result.get(
                "reason",
                "Whole-answer semantic evaluation failed."
            )
        )


    # --------------------------------------------------------
    # 9. Sentence-level concept evidence
    # --------------------------------------------------------

    try:

        sentence_evaluator = (
            get_sentence_concept_evaluator()
        )

        sentence_result = (
            sentence_evaluator.evaluate(
                question_id=
                    question_id,

                transcript=
                    evaluation_data[
                        "transcript"
                    ]
            )
        )

    except Exception as error:

        return build_failure_response(
            status=(
                "SENTENCE_EVALUATION_ERROR"
            ),
            reason=str(error)
        )


    if not sentence_result.get(
        "success"
    ):

        return build_failure_response(
            status=sentence_result.get(
                "status",
                "SENTENCE_EVALUATION_FAILED"
            ),
            reason=(
                "Sentence-level semantic "
                "evaluation failed."
            )
        )


    # --------------------------------------------------------
    # 10. Combine semantic evidence
    #
    # These values are MODEL FEATURES.
    # They are NOT final scores.
    # --------------------------------------------------------

    semantic_evidence = {

        "question_id":
            question_id,

        "reference_role":
            reference.get(
                "job_role"
            ),

        "reference_concept_count":
            len(
                reference.get(
                    "key_concepts",
                    []
                )
            ),


        # ====================================================
        # Whole-answer evidence
        # ====================================================

        "whole_answer": {

            "status":
                whole_answer_result.get(
                    "status"
                ),

            "mean_similarity":
                whole_answer_result.get(
                    "mean_similarity"
                ),

            "max_similarity":
                whole_answer_result.get(
                    "max_similarity"
                ),

            "min_similarity":
                whole_answer_result.get(
                    "min_similarity"
                ),

            "concept_results":
                whole_answer_result.get(
                    "concept_results",
                    []
                )
        },


        # ====================================================
        # Sentence-level evidence
        # ====================================================

        "sentence_level": {

            "status":
                sentence_result.get(
                    "status"
                ),

            "sentence_count":
                sentence_result.get(
                    "sentence_count"
                ),

            "mean_best_similarity":
                sentence_result.get(
                    "mean_best_similarity"
                ),

            "max_best_similarity":
                sentence_result.get(
                    "max_best_similarity"
                ),

            "min_best_similarity":
                sentence_result.get(
                    "min_best_similarity"
                ),

            "concept_results":
                sentence_result.get(
                    "concept_results",
                    []
                )
        }
    }


    # --------------------------------------------------------
    # 11. Semantic feature summary
    #
    # Threshold-free numeric evidence only.
    #
    # This is intentionally NOT converted into 1-5 scores.
    # --------------------------------------------------------

    semantic_feature_summary = {

        "whole_mean_similarity":
            whole_answer_result.get(
                "mean_similarity"
            ),

        "whole_max_similarity":
            whole_answer_result.get(
                "max_similarity"
            ),

        "whole_min_similarity":
            whole_answer_result.get(
                "min_similarity"
            ),

        "sentence_mean_best_similarity":
            sentence_result.get(
                "mean_best_similarity"
            ),

        "sentence_max_best_similarity":
            sentence_result.get(
                "max_best_similarity"
            ),

        "sentence_min_best_similarity":
            sentence_result.get(
                "min_best_similarity"
            ),

        "reference_concept_count":
            len(
                reference.get(
                    "key_concepts",
                    []
                )
            ),

        "answer_sentence_count":
            sentence_result.get(
                "sentence_count"
            )
    }


    semantic_evidence[
        "feature_summary"
    ] = semantic_feature_summary


    # --------------------------------------------------------
    # 12. Successful result
    # --------------------------------------------------------

    return {

        "ready": True,

        "status":
            "SEMANTIC_EVIDENCE_READY",

        "reason":
            None,

        "evaluation_context":
            context,

        "semantic_evidence":
            semantic_evidence,

        # IMPORTANT:
        # No calibrated 1-5 scoring model exists yet.
        "scores":
            None
    }


# ============================================================
# STORE MODEL OUTPUT SAFELY
# ============================================================

def accept_model_scores(scores):

    validation = (
        validate_aegie_scores(
            scores
        )
    )


    if not validation[
        "valid"
    ]:

        return {
            "accepted": False,
            "reason": validation[
                "reason"
            ],
            "scores": None
        }


    return {
        "accepted": True,
        "reason": None,
        "scores": scores
    }


# ============================================================
# DEVELOPMENT TEST
# ============================================================

def main():

    print("=" * 70)

    print(
        "AEGIE SEMANTIC EVALUATION "
        "AGENT TEST"
    )

    print("=" * 70)


    # ========================================================
    # TEST 1
    # Missing transcript.
    # Evaluator must refuse to continue.
    # ========================================================

    state_without_transcript = {

        "participant_id":
            "DEV_TEST",

        "job_role":
            "Cybersecurity Analyst",

        "current_question": {

            "question_id":
                "CS_E02",

            "question_text":
                (
                    "What is the difference between "
                    "authentication and authorization?"
                ),

            "difficulty":
                "Easy"
        },

        "transcript":
            None,

        "duration_sec":
            15.0,

        "word_count":
            None,

        "wpm":
            None,

        "filler_count":
            None,

        "pause_count":
            1
    }


    result = (
        prepare_semantic_evaluation(
            state_without_transcript
        )
    )


    print()

    print("-" * 70)

    print(
        "TEST 1 - NO TRANSCRIPT"
    )

    print("-" * 70)


    print(
        "Ready:",
        result[
            "ready"
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


    # ========================================================
    # TEST 2
    # Non-Data-Scientist development transcript.
    #
    # This is NOT genuine participant research data.
    # ========================================================

    state_with_test_transcript = {

        "participant_id":
            "DEV_TEST",

        "job_role":
            "Cybersecurity Analyst",

        "current_question": {

            "question_id":
                "CS_E02",

            "question_text":
                (
                    "What is the difference between "
                    "authentication and authorization?"
                ),

            "difficulty":
                "Easy"
        },

        "transcript": (

            "Authentication verifies the identity "
            "of a user. "

            "A password or another authentication "
            "factor can help verify who the user is. "

            "Authorization determines what an "
            "authenticated user is permitted to "
            "access or perform. "

            "For example, an administrator can have "
            "permissions that a normal user does not."
        ),

        "duration_sec":
            20.0,

        "word_count":
            43,

        "wpm":
            129.0,

        "filler_count":
            0,

        "pause_count":
            2
    }


    result = (
        prepare_semantic_evaluation(
            state_with_test_transcript
        )
    )


    print()

    print("-" * 70)

    print(
        "TEST 2 - MULTI-ROLE "
        "SEMANTIC EVIDENCE"
    )

    print("-" * 70)


    print(
        "Ready:",
        result[
            "ready"
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


    if not result[
        "ready"
    ]:

        print()

        print(
            "FAIL: Semantic evaluation "
            "did not complete."
        )

        return


    # --------------------------------------------------------
    # Context
    # --------------------------------------------------------

    context = result[
        "evaluation_context"
    ]


    print()

    print(
        "Question ID:",
        context[
            "question_id"
        ]
    )


    print(
        "Reference role:",
        context[
            "job_role"
        ]
    )


    print(
        "Question:",
        context[
            "question_text"
        ]
    )


    print(
        "Reference concepts:",
        len(
            context[
                "reference_key_concepts"
            ]
        )
    )


    # --------------------------------------------------------
    # Semantic evidence
    # --------------------------------------------------------

    evidence = result[
        "semantic_evidence"
    ]


    whole = evidence[
        "whole_answer"
    ]


    sentence = evidence[
        "sentence_level"
    ]


    print()

    print("-" * 70)

    print(
        "WHOLE-ANSWER SEMANTIC EVIDENCE"
    )

    print("-" * 70)


    print(
        "Mean similarity:",
        whole[
            "mean_similarity"
        ]
    )


    print(
        "Maximum similarity:",
        whole[
            "max_similarity"
        ]
    )


    print(
        "Minimum similarity:",
        whole[
            "min_similarity"
        ]
    )


    print()

    print("-" * 70)

    print(
        "SENTENCE-LEVEL SEMANTIC EVIDENCE"
    )

    print("-" * 70)


    print(
        "Answer sentences:",
        sentence[
            "sentence_count"
        ]
    )


    print(
        "Mean best similarity:",
        sentence[
            "mean_best_similarity"
        ]
    )


    print(
        "Maximum best similarity:",
        sentence[
            "max_best_similarity"
        ]
    )


    print(
        "Minimum best similarity:",
        sentence[
            "min_best_similarity"
        ]
    )


    # --------------------------------------------------------
    # Feature summary
    # --------------------------------------------------------

    print()

    print("-" * 70)

    print(
        "THRESHOLD-FREE FEATURE SUMMARY"
    )

    print("-" * 70)


    for key, value in evidence[
        "feature_summary"
    ].items():

        print(
            f"{key}: {value}"
        )


    # --------------------------------------------------------
    # Scores
    # --------------------------------------------------------

    print()

    print(
        "AEGIE 1-5 scores:",
        result[
            "scores"
        ]
    )


    print()

    print("=" * 70)

    print(
        "PASS: SEMANTIC EVALUATION "
        "AGENT GENERATED EVIDENCE"
    )

    print("=" * 70)


    print()

    print(
        "Central 72-question registry: PASS"
    )

    print(
        "Whole-answer evidence: PASS"
    )

    print(
        "Sentence-level evidence: PASS"
    )

    print(
        "Human labels used: NO"
    )

    print(
        "Arbitrary score thresholds used: NO"
    )

    print(
        "Final AEGIE scores generated: NO"
    )


# ============================================================
# RUN DEVELOPMENT TEST
# ============================================================

if __name__ == "__main__":

    main()