import os
import pandas as pd


# ============================================================
# AEGIE QUESTION SELECTOR
# ============================================================

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".."
    )
)


QUESTION_BANK_DIR = os.path.join(
    PROJECT_ROOT,
    "data",
    "question_bank"
)


QUESTION_FILES = {

    "Software Developer":
        "software_developer.csv",

    "Data Analyst":
        "data_analyst.csv",

    "Data Scientist":
        "data_scientist.csv",

    "Machine Learning Engineer":
        "ml_engineer.csv",

    "Cloud DevOps Engineer":
        "cloud_devops.csv",

    "Cybersecurity Analyst":
        "cybersecurity_analyst.csv"
}


VALID_DIFFICULTIES = {
    "Easy",
    "Medium",
    "Hard"
}


# ============================================================
# LOAD QUESTION BANK
# ============================================================

def load_question_bank(job_role):

    if job_role not in QUESTION_FILES:

        raise ValueError(
            f"Invalid job role: {job_role}"
        )


    filename = QUESTION_FILES[
        job_role
    ]


    path = os.path.join(
        QUESTION_BANK_DIR,
        filename
    )


    if not os.path.exists(path):

        raise FileNotFoundError(
            f"Question bank not found: {path}"
        )


    df = pd.read_csv(path)


    required_columns = {
        "question_id",
        "job_role",
        "difficulty",
        "question_text"
    }


    missing = (
        required_columns
        - set(df.columns)
    )


    if missing:

        raise ValueError(
            f"Missing columns in {filename}: "
            f"{sorted(missing)}"
        )


    # Ensure this file contains only
    # questions for the selected role.

    df = df[
        df["job_role"] == job_role
    ].copy()


    if df.empty:

        raise ValueError(
            f"No questions available for "
            f"{job_role}."
        )


    return df


# ============================================================
# SELECT NEXT QUESTION
# ============================================================

def select_question(
    job_role,
    question_number,
    asked_question_ids=None,
    target_difficulty=None
):

    if asked_question_ids is None:

        asked_question_ids = []


    df = load_question_bank(
        job_role
    )


    # --------------------------------------------------------
    # REMOVE QUESTIONS ALREADY ASKED
    # --------------------------------------------------------

    available = df[
        ~df["question_id"].isin(
            asked_question_ids
        )
    ].copy()


    if available.empty:

        return None


    # --------------------------------------------------------
    # QUESTION 1 MUST ALWAYS BE EASY
    # --------------------------------------------------------

    if question_number == 1:

        required_difficulty = "Easy"


    # --------------------------------------------------------
    # QUESTIONS 2-10
    #
    # Later the Adaptive Decision Agent supplies:
    # Easy / Medium / Hard
    #
    # We do NOT invent an adaptive decision here.
    # --------------------------------------------------------

    else:

        if (
            target_difficulty
            in VALID_DIFFICULTIES
        ):

            required_difficulty = (
                target_difficulty
            )

        else:

            # Adaptive evaluator is not ready yet.
            return None


    # --------------------------------------------------------
    # FILTER BY REQUIRED DIFFICULTY
    # --------------------------------------------------------

    candidates = available[
        available["difficulty"]
        == required_difficulty
    ]


    if candidates.empty:

        return None


    # --------------------------------------------------------
    # RANDOM SELECTION WITHIN VALID CANDIDATES
    # --------------------------------------------------------

    selected = candidates.sample(
        n=1
    ).iloc[0]


    return {

        "question_id":
            selected["question_id"],

        "job_role":
            selected["job_role"],

        "difficulty":
            selected["difficulty"],

        "question_text":
            selected["question_text"]
    }


# ============================================================
# DEVELOPMENT TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 65)
    print("AEGIE QUESTION SELECTOR TEST")
    print("=" * 65)


    # --------------------------------------------------------
    # TEST QUESTION 1
    # --------------------------------------------------------

    q1 = select_question(

        job_role="Data Scientist",

        question_number=1,

        asked_question_ids=[],

        target_difficulty=None
    )


    print()
    print("QUESTION 1")
    print("-" * 65)

    if q1:

        print(
            "Question ID:",
            q1["question_id"]
        )

        print(
            "Difficulty:",
            q1["difficulty"]
        )

        print(
            "Question:",
            q1["question_text"]
        )

    else:

        print(
            "No question selected."
        )


    # --------------------------------------------------------
    # TEST QUESTION 2 WITHOUT ADAPTIVE DECISION
    # --------------------------------------------------------

    asked = []

    if q1:

        asked.append(
            q1["question_id"]
        )


    q2_without_decision = select_question(

        job_role="Data Scientist",

        question_number=2,

        asked_question_ids=asked,

        target_difficulty=None
    )


    print()
    print("QUESTION 2 - NO ADAPTIVE DECISION")
    print("-" * 65)

    print(
        "Result:",
        q2_without_decision
    )


    # --------------------------------------------------------
    # SIMULATE ADAPTIVE AGENT REQUEST
    #
    # This does NOT mean Medium is the real adaptive decision.
    # It only tests whether the selector obeys an input.
    # --------------------------------------------------------

    q2_test = select_question(

        job_role="Data Scientist",

        question_number=2,

        asked_question_ids=asked,

        target_difficulty="Medium"
    )


    print()
    print("QUESTION 2 - MODULE TEST")
    print("-" * 65)

    if q2_test:

        print(
            "Question ID:",
            q2_test["question_id"]
        )

        print(
            "Difficulty:",
            q2_test["difficulty"]
        )

        print(
            "Question:",
            q2_test["question_text"]
        )


    print()
    print("=" * 65)
    print("QUESTION SELECTOR TEST COMPLETE")
    print("=" * 65)