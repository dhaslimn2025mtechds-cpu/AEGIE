# ============================================================
# AEGIE INTERVIEW AGENT - AUTOMATIC QUESTION SELECTION TEST
# ============================================================

from aegie_state import create_aegie_state
from aegie_agents import InterviewAgent


def main():

    print("=" * 65)
    print("AEGIE INTERVIEW AGENT TEST")
    print("=" * 65)

    # --------------------------------------------------------
    # CREATE STATE
    #
    # Notice:
    # We are NOT manually giving question_id,
    # question_text or difficulty.
    # --------------------------------------------------------

    state = create_aegie_state(

        participant_id="P001",

        job_role="Data Scientist",

        question_number=1
    )

    print()
    print("BEFORE INTERVIEW AGENT")
    print("-" * 65)

    print(
        "Participant:",
        state["participant_id"]
    )

    print(
        "Role:",
        state["job_role"]
    )

    print(
        "Question Number:",
        state["question_number"]
    )

    print(
        "Current Question:",
        state["current_question"]
    )

    # --------------------------------------------------------
    # RUN INTERVIEW AGENT
    # --------------------------------------------------------

    agent = InterviewAgent()

    state = agent.process(state)

    # --------------------------------------------------------
    # DISPLAY RESULT
    # --------------------------------------------------------

    print()
    print("AFTER INTERVIEW AGENT")
    print("-" * 65)

    question = state.get(
        "current_question"
    )

    print(
        "Agent Status:",
        state.get(
            "interview_agent_status"
        )
    )

    if question:

        print(
            "Question ID:",
            question["question_id"]
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
        # VERIFY QUESTION 1 IS EASY
        # ----------------------------------------------------

        if question["difficulty"] == "Easy":

            print()
            print(
                "PASS: Question 1 is Easy."
            )

        else:

            print()
            print(
                "FAIL: Question 1 should be Easy."
            )

    else:

        print()
        print(
            "FAIL: Interview Agent did not "
            "select a question."
        )

    print()
    print("=" * 65)
    print("TEST COMPLETE")
    print("=" * 65)


if __name__ == "__main__":
    main()