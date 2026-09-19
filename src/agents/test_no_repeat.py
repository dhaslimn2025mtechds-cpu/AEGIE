# ============================================================
# AEGIE NO-REPEATED-QUESTION TEST
# ============================================================

from aegie_state import create_aegie_state
from aegie_agents import InterviewAgent


def main():

    print("=" * 65)
    print("AEGIE NO-REPEAT QUESTION TEST")
    print("=" * 65)

    agent = InterviewAgent()

    # ========================================================
    # QUESTION 1
    # ========================================================

    state = create_aegie_state(
        participant_id="P001",
        job_role="Data Scientist",
        question_number=1
    )

    state = agent.process(state)

    q1 = state.get("current_question")

    if q1 is None:
        print()
        print("FAIL: Question 1 was not selected.")
        return

    q1_id = q1["question_id"]

    print()
    print("QUESTION 1")
    print("-" * 65)

    print(
        "Question ID:",
        q1_id
    )

    print(
        "Difficulty:",
        q1["difficulty"]
    )

    print(
        "Question:",
        q1["question_text"]
    )

    # ========================================================
    # MARK QUESTION 1 AS ALREADY ASKED
    # ========================================================

    asked_question_ids = [
        q1_id
    ]

    # ========================================================
    # QUESTION 2 TEST
    #
    # We use "Easy" only to test the selector's no-repeat rule.
    #
    # This is NOT the final adaptive decision.
    # ========================================================

    state2 = create_aegie_state(
        participant_id="P001",
        job_role="Data Scientist",
        question_number=2,
        asked_question_ids=asked_question_ids
    )

    # Temporary test input only.
    state2["next_difficulty"] = "Easy"

    state2 = agent.process(state2)

    q2 = state2.get("current_question")

    print()
    print("QUESTION 2")
    print("-" * 65)

    if q2 is None:

        print(
            "FAIL: Question 2 was not selected."
        )

        return

    q2_id = q2["question_id"]

    print(
        "Question ID:",
        q2_id
    )

    print(
        "Difficulty:",
        q2["difficulty"]
    )

    print(
        "Question:",
        q2["question_text"]
    )

    # ========================================================
    # CHECK FOR REPETITION
    # ========================================================

    print()
    print("NO-REPEAT CHECK")
    print("-" * 65)

    print(
        "Question 1 ID:",
        q1_id
    )

    print(
        "Question 2 ID:",
        q2_id
    )

    if q1_id != q2_id:

        print()
        print(
            "PASS: Question was not repeated."
        )

    else:

        print()
        print(
            "FAIL: Same question was repeated."
        )

    # ========================================================
    # CHECK ROLE
    # ========================================================

    if q2["job_role"] == "Data Scientist":

        print(
            "PASS: Question remained within "
            "the selected job role."
        )

    else:

        print(
            "FAIL: Job role changed."
        )

    print()
    print("=" * 65)
    print("NO-REPEAT TEST COMPLETE")
    print("=" * 65)


if __name__ == "__main__":
    main()