# ============================================================
# AEGIE FOUR-AGENT PIPELINE INTEGRATION TEST
# ============================================================

from aegie_state import create_aegie_state
from aegie_agents import AEGIEAgentPipeline


def main():

    print("=" * 60)
    print("AEGIE FOUR-AGENT INTEGRATION TEST")
    print("=" * 60)

    # --------------------------------------------------------
    # STEP 1: CREATE SHARED STATE
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

    print()
    print("Shared state created successfully.")

    # --------------------------------------------------------
    # STEP 2: CREATE AGENT PIPELINE
    # --------------------------------------------------------

    pipeline = AEGIEAgentPipeline()

    # --------------------------------------------------------
    # STEP 3: RUN FOUR AGENTS
    # --------------------------------------------------------

    final_state = pipeline.run(state)

    # --------------------------------------------------------
    # STEP 4: DISPLAY FINAL STATE
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("AEGIE FINAL PIPELINE STATE")
    print("=" * 60)

    print(
        "Participant:",
        final_state["participant_id"]
    )

    print(
        "Role:",
        final_state["job_role"]
    )

    print(
        "Question:",
        final_state[
            "current_question"
        ]["question_id"]
    )

    print(
        "Current Difficulty:",
        final_state[
            "current_difficulty"
        ]
    )

    print()

    print(
        "Interview Agent:",
        final_state.get(
            "interview_agent_status"
        )
    )

    print(
        "Transcription:",
        final_state.get(
            "transcription_status"
        )
    )

    print(
        "Evaluation Agent:",
        final_state.get(
            "evaluation_status"
        )
    )

    print(
        "AEGIE Scores:",
        final_state.get(
            "aegie_scores"
        )
    )

    print(
        "Adaptive Agent:",
        final_state.get(
            "adaptive_status"
        )
    )

    print(
        "Next Difficulty:",
        final_state.get(
            "next_difficulty"
        )
    )

    print(
        "Feedback Agent:",
        final_state.get(
            "feedback_status"
        )
    )

    print()

    print("=" * 60)
    print("INTEGRATION TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()