# ============================================================
# AEGIE SENTENCE-LEVEL SEMANTIC ORDERING TEST
# ============================================================
#
# Development sanity test only.
#
# Tests:
# Strong answer
# Partial answer
# Unrelated answer
#
# No participant data is used.
# No 1-5 scoring thresholds are defined.
# ============================================================

from sentence_concept_evaluator import SentenceConceptEvaluator


def show_result(label, result):

    print()
    print("=" * 70)
    print(label)
    print("=" * 70)

    print("Status:", result["status"])

    if not result["success"]:
        return

    print(
        "Mean best similarity:",
        result["mean_best_similarity"]
    )

    print(
        "Maximum best similarity:",
        result["max_best_similarity"]
    )

    print(
        "Minimum best similarity:",
        result["min_best_similarity"]
    )

    print()

    for item in result["concept_results"]:

        print(
            f"Concept {item['concept_number']}: "
            f"{item['best_similarity']}"
        )


def main():

    print("=" * 70)
    print("AEGIE IMPROVED SEMANTIC ORDERING TEST")
    print("=" * 70)

    evaluator = SentenceConceptEvaluator()

    question_id = "DS_E02"


    # --------------------------------------------------------
    # STRONG ANSWER
    # --------------------------------------------------------

    strong_answer = (
        "Overfitting occurs when a machine learning model "
        "learns the training data too closely. "
        "The model can also learn noise or irrelevant patterns. "
        "It may achieve very high performance on the training data. "
        "However, its performance on new unseen data can be poor."
    )


    # --------------------------------------------------------
    # PARTIAL ANSWER
    # --------------------------------------------------------

    partial_answer = (
        "Overfitting means the model learns "
        "the training data too closely."
    )


    # --------------------------------------------------------
    # UNRELATED ANSWER
    # --------------------------------------------------------

    unrelated_answer = (
        "A firewall monitors network traffic and blocks "
        "unauthorized connections using security rules."
    )


    strong = evaluator.evaluate(
        question_id,
        strong_answer
    )

    partial = evaluator.evaluate(
        question_id,
        partial_answer
    )

    unrelated = evaluator.evaluate(
        question_id,
        unrelated_answer
    )


    show_result(
        "STRONG DEVELOPMENT ANSWER",
        strong
    )

    show_result(
        "PARTIAL DEVELOPMENT ANSWER",
        partial
    )

    show_result(
        "UNRELATED DEVELOPMENT ANSWER",
        unrelated
    )


    print()
    print("=" * 70)
    print("ORDERING CHECK")
    print("=" * 70)


    if not (
        strong["success"]
        and partial["success"]
        and unrelated["success"]
    ):

        print(
            "CHECK FAILED: Evaluation error."
        )

        return


    strong_mean = (
        strong["mean_best_similarity"]
    )

    partial_mean = (
        partial["mean_best_similarity"]
    )

    unrelated_mean = (
        unrelated["mean_best_similarity"]
    )


    print()
    print("Strong:", strong_mean)
    print("Partial:", partial_mean)
    print("Unrelated:", unrelated_mean)

    print()
    print(
        "Expected:"
    )

    print(
        "Strong > Partial > Unrelated"
    )

    print()


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
            "CHECK: Expected ordering "
            "was not fully observed."
        )

        print(
            "Do not create thresholds "
            "to force the expected result."
        )


    print()
    print("=" * 70)
    print("RESEARCH INTERPRETATION")
    print("=" * 70)

    print(
        "Sentence-level concept matching is "
        "being tested as a semantic feature."
    )

    print(
        "This test does not establish "
        "scientific validity."
    )

    print(
        "Human annotations will later be "
        "required for validation and calibration."
    )

    print(
        "No development answer is added "
        "to the 3000-sample dataset."
    )


if __name__ == "__main__":
    main()