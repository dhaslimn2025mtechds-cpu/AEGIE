# ============================================================
# AEGIE SEMANTIC ORDERING TEST
# ============================================================
#
# Purpose:
# Test whether concept-level MiniLM evidence behaves sensibly
# for controlled development answers.
#
# Expected general behaviour:
#
# Strong answer
#      >
# Partial answer
#      >
# Unrelated answer
#
# IMPORTANT:
# These are development examples only.
# They are NOT research participant samples.
# No 1-5 scoring thresholds are defined here.
# ============================================================

from concept_evaluator import ConceptEvaluator


def print_result(label, result):

    print()
    print("=" * 70)
    print(label)
    print("=" * 70)

    print(
        "Status:",
        result["status"]
    )

    if not result["success"]:

        print(
            "Reason:",
            result["reason"]
        )

        return

    print(
        "Mean similarity:",
        result["mean_similarity"]
    )

    print(
        "Maximum similarity:",
        result["max_similarity"]
    )

    print(
        "Minimum similarity:",
        result["min_similarity"]
    )

    print()
    print("Concept similarities:")

    for item in result[
        "concept_results"
    ]:

        print(
            f"  Concept "
            f"{item['concept_number']}: "
            f"{item['similarity']}"
        )


def main():

    print("=" * 70)
    print("AEGIE CONTROLLED SEMANTIC ORDERING TEST")
    print("=" * 70)

    evaluator = ConceptEvaluator()

    question_id = "DS_E02"


    # ========================================================
    # STRONG DEVELOPMENT ANSWER
    # ========================================================

    strong_answer = (
        "Overfitting occurs when a machine learning model "
        "learns the training data too closely, including "
        "noise or irrelevant patterns. It can achieve very "
        "high performance on the training data but performs "
        "poorly on new unseen data because it does not "
        "generalize well."
    )


    # ========================================================
    # PARTIAL DEVELOPMENT ANSWER
    # ========================================================

    partial_answer = (
        "Overfitting means the model learns the training "
        "data too closely."
    )


    # ========================================================
    # UNRELATED DEVELOPMENT ANSWER
    # ========================================================

    unrelated_answer = (
        "A firewall monitors network traffic and can block "
        "unauthorized connections based on security rules."
    )


    strong_result = evaluator.evaluate(
        question_id,
        strong_answer
    )

    partial_result = evaluator.evaluate(
        question_id,
        partial_answer
    )

    unrelated_result = evaluator.evaluate(
        question_id,
        unrelated_answer
    )


    print_result(
        "STRONG DEVELOPMENT ANSWER",
        strong_result
    )

    print_result(
        "PARTIAL DEVELOPMENT ANSWER",
        partial_result
    )

    print_result(
        "UNRELATED DEVELOPMENT ANSWER",
        unrelated_result
    )


    # ========================================================
    # ORDERING CHECK
    # ========================================================

    print()
    print("=" * 70)
    print("SEMANTIC ORDERING CHECK")
    print("=" * 70)


    if not (
        strong_result["success"]
        and partial_result["success"]
        and unrelated_result["success"]
    ):

        print(
            "CHECK FAILED: One or more "
            "evaluations did not complete."
        )

        return


    strong_mean = (
        strong_result[
            "mean_similarity"
        ]
    )

    partial_mean = (
        partial_result[
            "mean_similarity"
        ]
    )

    unrelated_mean = (
        unrelated_result[
            "mean_similarity"
        ]
    )


    print()
    print(
        "Strong mean:",
        strong_mean
    )

    print(
        "Partial mean:",
        partial_mean
    )

    print(
        "Unrelated mean:",
        unrelated_mean
    )


    print()
    print(
        "Expected development ordering:"
    )

    print(
        "Strong > Partial > Unrelated"
    )


    print()
    print(
        "Observed:"
    )


    if (
        strong_mean
        > partial_mean
        > unrelated_mean
    ):

        print(
            "PASS: Strong > Partial > Unrelated"
        )

    else:

        print(
            "CHECK: Expected ordering was "
            "not fully observed."
        )

        print(
            "This does NOT automatically mean "
            "the model is unusable."
        )

        print(
            "The semantic feature design may "
            "need refinement and validation."
        )


    # ========================================================
    # IMPORTANT RESEARCH NOTE
    # ========================================================

    print()
    print("=" * 70)
    print("RESEARCH NOTE")
    print("=" * 70)

    print(
        "This is a software sanity test only."
    )

    print(
        "It does not establish evaluation "
        "accuracy or scientific validity."
    )

    print(
        "Final validation must use genuine "
        "participant responses and independent "
        "human reference annotations."
    )

    print(
        "No similarity-to-score thresholds "
        "have been defined."
    )


if __name__ == "__main__":

    main()