# ============================================================
# AEGIE SHARED AGENT STATE
# ============================================================
#
# Research Framework:
# Adaptive Agentic AI-Based Voice Interview Evaluation
#
# Shared state used by:
#
# 1. Interview Agent
# 2. Evaluation Agent
# 3. Adaptive Decision Agent
# 4. Feedback & Reporting Agent
#
# IMPORTANT:
# Human reference scores are NOT included in the live state.
# They are stored separately for research evaluation.
# ============================================================


def create_aegie_state(
    participant_id,
    job_role,
    question_number=1,
    question_id=None,
    question_text=None,
    difficulty=None,
    asked_question_ids=None
):

    # --------------------------------------------------------
    # ASKED QUESTIONS
    # --------------------------------------------------------

    if asked_question_ids is None:
        asked_question_ids = []


    # --------------------------------------------------------
    # CURRENT QUESTION
    #
    # If question information is not supplied, the Interview
    # Agent can select the question using question_selector.py.
    # --------------------------------------------------------

    if (
        question_id is not None
        and question_text is not None
        and difficulty is not None
    ):

        current_question = {

            "question_id":
                question_id,

            "question_text":
                question_text,

            "difficulty":
                difficulty
        }

    else:

        current_question = None


    # ========================================================
    # SHARED STATE
    # ========================================================

    state = {

        # ----------------------------------------------------
        # PARTICIPANT INFORMATION
        # ----------------------------------------------------

        "participant_id":
            participant_id,

        "job_role":
            job_role,


        # ----------------------------------------------------
        # INTERVIEW INFORMATION
        # ----------------------------------------------------

        "question_number":
            question_number,

        "asked_question_ids":
            list(asked_question_ids),

        "current_question":
            current_question,


        # ----------------------------------------------------
        # AUDIO INFORMATION
        # ----------------------------------------------------

        "audio_path":
            None,

        "duration_sec":
            None,

        "pause_count":
            None,

        "quality_status":
            None,


        # ----------------------------------------------------
        # TRANSCRIPTION INFORMATION
        # ----------------------------------------------------

        "transcript":
            None,

        "transcription_engine":
            None,

        "transcription_status":
            "NOT_STARTED",


        # ----------------------------------------------------
        # OBJECTIVE SPEECH FEATURES
        # ----------------------------------------------------

        "word_count":
            None,

        "wpm":
            None,

        "filler_count":
            None,


        # ----------------------------------------------------
        # AEGIE SYSTEM PREDICTIONS
        #
        # These are system predictions.
        # They are NOT human reference labels.
        # ----------------------------------------------------

        "aegie_scores":
            None,


        # ----------------------------------------------------
        # DIFFICULTY INFORMATION
        # ----------------------------------------------------

        "current_difficulty":
            difficulty,

        "next_difficulty":
            None,


        # ----------------------------------------------------
        # AGENT STATUS
        # ----------------------------------------------------

        "interview_agent_status":
            "NOT_STARTED",

        "evaluation_status":
            "NOT_STARTED",

        "adaptive_status":
            "NOT_STARTED",

        "feedback_status":
            "NOT_STARTED",


        # ----------------------------------------------------
        # FEEDBACK / REPORT
        # ----------------------------------------------------

        "feedback":
            None
    }


    return state


# ============================================================
# DEVELOPMENT TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 65)
    print("AEGIE SHARED STATE TEST")
    print("=" * 65)


    # --------------------------------------------------------
    # TEST 1
    #
    # Create state WITHOUT manually providing a question.
    # The Interview Agent will later select Question 1.
    # --------------------------------------------------------

    state = create_aegie_state(

        participant_id="P001",

        job_role="Data Scientist",

        question_number=1
    )


    print()
    print("Participant:")
    print(
        state["participant_id"]
    )


    print()
    print("Job Role:")
    print(
        state["job_role"]
    )


    print()
    print("Question Number:")
    print(
        state["question_number"]
    )


    print()
    print("Asked Question IDs:")
    print(
        state["asked_question_ids"]
    )


    print()
    print("Current Question:")
    print(
        state["current_question"]
    )


    print()
    print("Current Difficulty:")
    print(
        state["current_difficulty"]
    )


    print()
    print("Transcript:")
    print(
        state["transcript"]
    )


    print()
    print("AEGIE Scores:")
    print(
        state["aegie_scores"]
    )


    print()
    print("Next Difficulty:")
    print(
        state["next_difficulty"]
    )


    print()
    print("Interview Agent Status:")
    print(
        state["interview_agent_status"]
    )


    print()
    print("Evaluation Status:")
    print(
        state["evaluation_status"]
    )


    print()
    print("Adaptive Status:")
    print(
        state["adaptive_status"]
    )


    print()
    print("Feedback Status:")
    print(
        state["feedback_status"]
    )


    print()
    print("=" * 65)
    print("SHARED STATE CREATED SUCCESSFULLY")
    print("=" * 65)