# ============================================================
# AEGIE CONNECTED EVALUATION PIPELINE TEST
# ============================================================

from aegie_state import (
    create_aegie_state
)

from aegie_agents import (
    EvaluationAgent,
    AdaptiveDecisionAgent,
    FeedbackReportingAgent
)


def main():

    print("=" * 65)
    print("AEGIE CONNECTED EVALUATION TEST")
    print("=" * 65)


    # --------------------------------------------------------
    # Development-only state.
    #
    # This transcript is NOT research participant data.
    # --------------------------------------------------------

    state = create_aegie_state(

        participant_id="P001",

        job_role="Data Scientist",

        question_number=1,

        question_id="DS_E02",

        question_text=(
            "What is overfitting in machine learning?"
        ),

        difficulty="Easy"
    )


    # Development transcript only.
    state["transcript"] = (
        "Overfitting happens when a model learns "
        "the training data too closely and then "
        "performs poorly on unseen data."
    )


    state["duration_sec"] = 12.0
    state["word_count"] = 20
    state["wpm"] = 100.0
    state["filler_count"] = 0
    state["pause_count"] = 1


    # ========================================================
    # EVALUATION AGENT
    # ========================================================

    evaluator = EvaluationAgent()

    state = evaluator.process(
        state
    )


    # ========================================================
    # ADAPTIVE AGENT
    # ========================================================

    adaptive = AdaptiveDecisionAgent()

    state = adaptive.process(
        state
    )


    # ========================================================
    # FEEDBACK AGENT
    # ========================================================

    feedback = FeedbackReportingAgent()

    state = feedback.process(
        state
    )


    # ========================================================
    # RESULT
    # ========================================================

    print()
    print("=" * 65)
    print("FINAL STATE")
    print("=" * 65)


    print(
        "Evaluation Status:",
        state.get(
            "evaluation_status"
        )
    )

    print(
        "Evaluation Model:",
        state.get(
            "evaluation_model"
        )
    )

    print(
        "AEGIE Scores:",
        state.get(
            "aegie_scores"
        )
    )

    print(
        "Adaptive Status:",
        state.get(
            "adaptive_status"
        )
    )

    print(
        "Next Difficulty:",
        state.get(
            "next_difficulty"
        )
    )

    print(
        "Feedback Status:",
        state.get(
            "feedback_status"
        )
    )

    print(
        "Feedback:",
        state.get(
            "feedback"
        )
    )


    print()
    print("=" * 65)
    print("CONNECTED PIPELINE TEST COMPLETE")
    print("=" * 65)


if __name__ == "__main__":

    main()