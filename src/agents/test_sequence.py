# ============================================================
# AEGIE SEQUENTIAL QUESTION TEST
# ============================================================

from aegie_state import create_aegie_state
from aegie_agents import InterviewAgent


def main():

    print("=" * 65)
    print("AEGIE SEQUENTIAL QUESTION TEST")
    print("=" * 65)

    participant_id = "P001"
    job_role = "Data Scientist"

    asked_question_ids = []

    agent = InterviewAgent()

    # ========================================================
    # TEST 4 EASY QUESTIONS
    #
    # Question 1 is naturally Easy.
    # For Questions 2-4, Easy is supplied ONLY for testing.
    # This is not the final adaptive decision.
    # ========================================================

    for question_number in range(1, 5):

        state = create_aegie_state(
            participant_id=participant_id,
            job_role=job_role,
            question_number=question_number,
            asked_question_ids=asked_question_ids
        )

        if question_number > 1:
            state["next_difficulty"] = "Easy"

        # ----------------------------------------------------
        # RUN INTERVIEW AGENT
        # ----------------------------------------------------

        state = agent.process(state)

        question = state.get(
            "current_question"
        )

        print()
        print(
            f"QUESTION {question_number}"
        )
        print("-" * 65)

        if question is None:

            print(
                "FAIL: No question selected."
            )

            return

        question_id = question[
            "question_id"
        ]

        print(
            "Question ID:",
            question_id
        )

        print(
            "Difficulty:",
            question["difficulty"]
        )

        print(
            "Question:",
            question["question_text"]
        )

        # ----------------------------------------------------
        # CHECK REPETITION
        # ----------------------------------------------------

        if question_id in asked_question_ids:

            print()
            print(
                "FAIL: Repeated question detected."
            )

            return

        # Mark question as asked only AFTER successful selection.
        asked_question_ids.append(
            question_id
        )

    # ========================================================
    # FINAL CHECK
    # ========================================================

    print()
    print("=" * 65)
    print("FINAL SEQUENCE CHECK")
    print("=" * 65)

    print(
        "Questions asked:",
        asked_question_ids
    )

    print(
        "Total questions:",
        len(asked_question_ids)
    )

    unique_count = len(
        set(asked_question_ids)
    )

    print(
        "Unique questions:",
        unique_count
    )

    if (
        len(asked_question_ids) == 4
        and unique_count == 4
    ):

        print()
        print(
            "PASS: All 4 questions are unique."
        )

        print(
            "PASS: No repeated questions."
        )

    else:

        print()
        print(
            "FAIL: Sequence contains repetition."
        )

    print()
    print("=" * 65)
    print("SEQUENTIAL TEST COMPLETE")
    print("=" * 65)


if __name__ == "__main__":
    main()