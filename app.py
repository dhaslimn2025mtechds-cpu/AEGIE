from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    session,
    redirect,
    url_for
)

import pandas as pd
import os
import re
import time
from datetime import datetime

from src.audio_features import (
    get_audio_duration,
    get_pause_count
)

from src.quality_check import (
    check_audio_quality
)

from src.transcription import (
    transcribe_audio
)

from src.speech_features import (
    extract_speech_features
)

from src.evaluation_feature_store import (
    save_evaluation_features
)

from src.calibrated_score_store import (
    update_primary_row_with_calibrated_scores
)

from src.agents.aegie_agents import (
    AEGIEAgentPipeline
)


# ============================================================
# AEGIE
# Adaptive Agentic AI-Based Voice Interview Evaluation
# ============================================================

app = Flask(__name__)

# Prototype only.
# Move to an environment variable before deployment.
app.secret_key = "aegie-research-session-2026"


# ============================================================
# AGENT PIPELINE
# ============================================================
#
# MiniLM is not loaded here at startup.
# The Evaluation Agent loads semantic models only when a valid
# transcript is available.
#
# The STT software layer is connected. If the approved Parakeet
# model is unavailable, genuine audio is still preserved and no
# transcript is fabricated. When the model becomes available,
# the same Flask route will automatically generate transcripts.
# ============================================================

AGENT_PIPELINE = AEGIEAgentPipeline()


# ============================================================
# JOB ROLES
# ============================================================

VALID_JOB_ROLES = [
    "Software Developer",
    "Data Analyst",
    "Data Scientist",
    "Machine Learning Engineer",
    "Cloud DevOps Engineer",
    "Cybersecurity Analyst"
]


# ============================================================
# COLLECTION MODE + DATASET PROTECTION
# ============================================================
#
# Three physically separate collection modes are used:
#
# DEVELOPMENT
#     Software/UI testing only.
#     data/development_dataset.csv
#     audio/development/<participant_id>/
#
# PILOT
#     Genuine pilot/calibration participants only.
#     data/pilot_dataset.csv
#     audio/pilot/<participant_id>/
#
# FINAL
#     Final 3,000-sample research collection only.
#     data/dataset.csv
#     audio/final/<participant_id>/
#
# DEVELOPMENT is the safe default.
#
# PILOT must be selected explicitly with:
#     AEGIE_COLLECTION_MODE=PILOT
#
# FINAL requires TWO explicit environment variables:
#     AEGIE_COLLECTION_MODE=FINAL
#     AEGIE_FINAL_COLLECTION_CONFIRM=YES
#
# Do not enable FINAL mode until the research protocol, consent,
# annotation process, STT plan, calibration, and adaptive rule are
# ready for genuine participant collection.
# ============================================================

COLLECTION_MODE = os.getenv(
    "AEGIE_COLLECTION_MODE",
    "DEVELOPMENT"
).strip().upper()

if COLLECTION_MODE not in {
    "DEVELOPMENT",
    "PILOT",
    "FINAL"
}:
    raise RuntimeError(
        "AEGIE_COLLECTION_MODE must be DEVELOPMENT, PILOT, or FINAL."
    )

FINAL_COLLECTION_CONFIRMED = (
    os.getenv(
        "AEGIE_FINAL_COLLECTION_CONFIRM",
        ""
    ).strip().upper()
    == "YES"
)

if (
    COLLECTION_MODE == "FINAL"
    and not FINAL_COLLECTION_CONFIRMED
):
    raise RuntimeError(
        "FINAL collection mode is locked. "
        "Set AEGIE_FINAL_COLLECTION_CONFIRM=YES only when "
        "you intentionally begin approved final research collection."
    )

DEVELOPMENT_DATASET_PATH = os.path.join(
    "data",
    "development_dataset.csv"
)

PILOT_DATASET_PATH = os.path.join(
    "data",
    "pilot_dataset.csv"
)

FINAL_DATASET_PATH = os.path.join(
    "data",
    "dataset.csv"
)

if COLLECTION_MODE == "FINAL":
    DATASET_PATH = FINAL_DATASET_PATH
    AUDIO_ROOT = os.path.join(
        "audio",
        "final"
    )
    DATASET_LABEL = "final research dataset"

elif COLLECTION_MODE == "PILOT":
    DATASET_PATH = PILOT_DATASET_PATH
    AUDIO_ROOT = os.path.join(
        "audio",
        "pilot"
    )
    DATASET_LABEL = "pilot calibration dataset"

else:
    DATASET_PATH = DEVELOPMENT_DATASET_PATH
    AUDIO_ROOT = os.path.join(
        "audio",
        "development"
    )
    DATASET_LABEL = "development dataset"


DATASET_COLUMNS = [

    "sample_id",
    "participant_id",
    "job_role",

    "question_id",
    "question_text",
    "difficulty",

    "audio_path",
    "transcript",

    "duration_sec",
    "word_count",
    "wpm",
    "filler_count",
    "pause_count",

    # Human reference labels
    "relevance_score",
    "technical_score",
    "clarity_score",
    "communication_score",
    "overall_score",
    "annotator_id",

    # AEGIE predictions
    "aegie_relevance_score",
    "aegie_technical_score",
    "aegie_clarity_score",
    "aegie_communication_score",
    "aegie_overall_score",
    "aegie_next_difficulty"
]


# ============================================================
# PARTICIPANT VALIDATION
# ============================================================
#
# DEVELOPMENT / FINAL:
#     P001 ... P300
#
# PILOT:
#     PL001 ... PL300
#
# Keeping pilot IDs separate prevents pilot/calibration records
# from being confused with the final 300-participant study.
# ============================================================

def valid_participant_id(participant_id):

    if COLLECTION_MODE == "PILOT":

        match = re.fullmatch(
            r"PL(\d{3})",
            participant_id
        )

    else:

        match = re.fullmatch(
            r"P(\d{3})",
            participant_id
        )


    if not match:

        return False


    number = int(
        match.group(1)
    )


    return 1 <= number <= 300


def participant_id_requirement():

    if COLLECTION_MODE == "PILOT":

        return "Enter a pilot ID between PL001 and PL300."

    return "Enter an ID between P001 and P300."


# ============================================================
# CREATE / UPGRADE DATASET
# ============================================================

def ensure_dataset_file(path):

    os.makedirs(
        "data",
        exist_ok=True
    )

    if not os.path.exists(path):

        pd.DataFrame(
            columns=DATASET_COLUMNS
        ).to_csv(
            path,
            index=False
        )

        print(
            "Dataset created:",
            path
        )

        return


    df = pd.read_csv(path)

    changed = False

    for column in DATASET_COLUMNS:

        if column not in df.columns:

            df[column] = ""
            changed = True

            print(
                "Dataset column added:",
                column,
                "->",
                path
            )


    if changed:

        df = df.reindex(
            columns=DATASET_COLUMNS
        )

        df.to_csv(
            path,
            index=False
        )

        print(
            "Dataset schema upgraded:",
            path
        )


def ensure_datasets():
    """
    Keep development, pilot, and final datasets schema-compatible.
    Only DATASET_PATH is writable for the active collection mode.
    """

    ensure_dataset_file(
        DEVELOPMENT_DATASET_PATH
    )

    ensure_dataset_file(
        PILOT_DATASET_PATH
    )

    ensure_dataset_file(
        FINAL_DATASET_PATH
    )


# ============================================================
# FLASK SESSION STATUS HELPERS
# ============================================================

def reset_agent_session_status():

    session[
        "last_stt_status"
    ] = "NOT_RUN"

    session[
        "last_stt_error"
    ] = None

    session[
        "last_evaluation_status"
    ] = "NOT_RUN"

    session[
        "last_adaptive_status"
    ] = "NOT_RUN"

    session[
        "last_feedback_status"
    ] = "NOT_RUN"

    session[
        "target_difficulty"
    ] = None


# ============================================================
# PILOT QUESTION SCHEDULE
# ============================================================
#
# Pilot/calibration collection must NOT depend on the uncalibrated
# adaptive model. Each pilot participant therefore receives a
# pre-specified difficulty schedule.
#
# Questions 1-9:
#     Easy, Medium, Hard repeated three times
#
# Question 10:
#     Rotates by pilot participant ID so groups of three pilot
#     participants are balanced:
#
#     PL001 -> extra Easy
#     PL002 -> extra Medium
#     PL003 -> extra Hard
#     PL004 -> extra Easy
#     ...
#
# This gives each participant 10 questions and never requests more
# than four questions from one difficulty level. Each role bank has
# four Easy, four Medium, and four Hard questions.
# ============================================================

def get_pilot_difficulty_schedule(
    participant_id
):

    match = re.fullmatch(
        r"PL(\d{3})",
        str(
            participant_id
        ).strip().upper()
    )


    if not match:

        raise ValueError(
            "Pilot participant ID must use PL001-PL300."
        )


    participant_number = int(
        match.group(1)
    )


    schedule = [
        "Easy",
        "Medium",
        "Hard",
        "Easy",
        "Medium",
        "Hard",
        "Easy",
        "Medium",
        "Hard"
    ]


    remainder = (
        participant_number
        % 3
    )


    if remainder == 1:

        extra_difficulty = "Easy"

    elif remainder == 2:

        extra_difficulty = "Medium"

    else:

        extra_difficulty = "Hard"


    schedule.append(
        extra_difficulty
    )


    return schedule


def get_pilot_target_difficulty(
    participant_id,
    question_number
):

    schedule = (
        get_pilot_difficulty_schedule(
            participant_id
        )
    )


    if not (
        1
        <= question_number
        <= len(schedule)
    ):

        return None


    return schedule[
        question_number - 1
    ]


def get_development_target_difficulty(
    question_number
):

    # --------------------------------------------------------
    # DEVELOPMENT MODE ONLY
    #
    # Fixed deterministic schedule for software testing.
    # This is NOT an adaptive research decision.
    #
    # Five-question DEVELOPMENT test schedule:
    #
    # Q1 -> Easy
    # Q2 -> Medium
    # Q3 -> Hard
    # Q4 -> Easy
    # Q5 -> Medium
    #
    # This is only for software testing.
    # PILOT and FINAL research collection remain unchanged.
    # --------------------------------------------------------

    schedule = [
        "Easy",
        "Medium",
        "Hard",
        "Easy",
        "Medium"
    ]


    if not (
        1
        <= question_number
        <= len(schedule)
    ):

        return None


    return schedule[
        question_number - 1
    ]


# ============================================================
# INTERVIEW AGENT QUESTION SELECTION
# ============================================================

def get_next_question():

    question_number = session.get(
        "question_number",
        1
    )

    participant_id = session.get(
        "participant_id"
    )

    target_difficulty = session.get(
        "target_difficulty"
    )


    # --------------------------------------------------------
    # PILOT MODE
    #
    # Use the pre-specified, non-adaptive pilot schedule.
    # Human labels and AEGIE predictions do not influence which
    # pilot question difficulty comes next.
    # --------------------------------------------------------

    if COLLECTION_MODE == "PILOT":

        try:

            target_difficulty = (
                get_pilot_target_difficulty(
                    participant_id,
                    question_number
                )
            )

        except Exception as error:

            print(
                "Pilot schedule error:",
                error
            )

            return None


        if target_difficulty not in {
            "Easy",
            "Medium",
            "Hard"
        }:

            return None


        print(
            "Pilot static difficulty:",
            target_difficulty
        )


    # --------------------------------------------------------
    # DEVELOPMENT MODE
    #
    # Use a fixed deterministic five-question schedule so the
    # software pipeline can be tested quickly from Q1 to Q5.
    #
    # This is explicitly NOT an adaptive research decision.
    # --------------------------------------------------------

    elif COLLECTION_MODE == "DEVELOPMENT":

        target_difficulty = (
            get_development_target_difficulty(
                question_number
            )
        )


        if target_difficulty not in {
            "Easy",
            "Medium",
            "Hard"
        }:

            return None


        print(
            "Development static test difficulty:",
            target_difficulty
        )


    # --------------------------------------------------------
    # FINAL MODE
    #
    # Question 1 may begin without a previous decision.
    # Questions 2-10 require a legitimate calibrated adaptive
    # decision. No fallback difficulty is fabricated.
    # --------------------------------------------------------

    else:

        if question_number == 1:

            target_difficulty = None

        elif target_difficulty not in {
            "Easy",
            "Medium",
            "Hard"
        }:

            return None


    # --------------------------------------------------------
    # Use the actual Interview Agent from aegie_agents.py.
    # --------------------------------------------------------

    state = {

        "participant_id":
            participant_id,

        "job_role":
            session.get(
                "job_role"
            ),

        "question_number":
            question_number,

        "asked_question_ids":
            session.get(
                "asked_question_ids",
                []
            ),

        "next_difficulty":
            target_difficulty,

        "current_question":
            None
    }


    try:

        state = (
            AGENT_PIPELINE
            .interview_agent
            .process(state)
        )

    except Exception as error:

        print(
            "Interview Agent error:",
            error
        )

        return None


    return state.get(
        "current_question"
    )


# ============================================================
# POST-RESPONSE AGENT PROCESSING
# ============================================================
#
# Current collection behavior:
# - genuine audio is saved
# - duration/pause features are available
# - transcript is blank because STT model is unavailable
# - Evaluation Agent therefore waits for transcript
# - Adaptive Agent does not invent a difficulty decision
# - Feedback Agent does not invent final feedback
#
# When STT becomes available, the same function can receive a
# genuine transcript and the existing semantic pipeline will run.
# ============================================================

def run_post_response_agents(
    participant_id,
    job_role,
    question_number,
    asked_question_ids,
    current_question,
    transcript,
    duration_sec,
    word_count,
    wpm,
    filler_count,
    pause_count
):

    state = {

        "participant_id":
            participant_id,

        "job_role":
            job_role,

        "question_number":
            question_number,

        "asked_question_ids":
            list(
                asked_question_ids
            ),

        "next_difficulty":
            None,

        "current_question":
            current_question,

        "current_difficulty":
            current_question.get(
                "difficulty"
            ),

        "transcript":
            transcript,

        "duration_sec":
            duration_sec,

        "word_count":
            word_count,

        "wpm":
            wpm,

        "filler_count":
            filler_count,

        "pause_count":
            pause_count,

        "evaluation_context":
            None,

        "semantic_evidence":
            None,

        "evaluation_features":
            None,

        "aegie_scores":
            None,

        "feedback":
            None
    }


    # --------------------------------------------------------
    # The question has already been asked and answered, so the
    # post-response flow begins with Evaluation Agent.
    # --------------------------------------------------------

    state = (
        AGENT_PIPELINE
        .evaluation_agent
        .process(state)
    )

    state = (
        AGENT_PIPELINE
        .adaptive_agent
        .process(state)
    )

    state = (
        AGENT_PIPELINE
        .feedback_agent
        .process(state)
    )


    return state


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    session.clear()

    return render_template(
        "index.html"
    )


# ============================================================
# SERVER TEST
# ============================================================

@app.route("/ping")
def ping():

    return "AEGIE SERVER OK"


# ============================================================
# START INTERVIEW
# ============================================================

@app.route(
    "/start",
    methods=["POST"]
)
def start_interview():

    participant_id = (
        request.form[
            "participant_id"
        ]
        .strip()
        .upper()
    )

    job_role = request.form[
        "job_role"
    ]


    # --------------------------------------------------------
    # PARTICIPANT VALIDATION
    # --------------------------------------------------------

    if not valid_participant_id(
        participant_id
    ):

        requirement = (
            participant_id_requirement()
        )

        return f"""
        <h2>Invalid Participant ID</h2>

        <p>
        {requirement}
        </p>

        <a href="/">
        Return Home
        </a>
        """, 400


    # --------------------------------------------------------
    # ROLE VALIDATION
    # --------------------------------------------------------

    if job_role not in VALID_JOB_ROLES:

        return (
            "Invalid job role",
            400
        )


    # --------------------------------------------------------
    # CLEAN SESSION
    # --------------------------------------------------------

    session.clear()

    session[
        "participant_id"
    ] = participant_id

    session[
        "job_role"
    ] = job_role

    session[
        "asked_question_ids"
    ] = []

    # Track only the samples created in this interview session.
    # This lets the final research dashboard show the current
    # 5-question DEVELOPMENT interview instead of older rows
    # from the same participant ID.
    session[
        "current_interview_sample_ids"
    ] = []

    session[
        "question_number"
    ] = 1

    session.pop(
        "current_question",
        None
    )


    reset_agent_session_status()


    print()
    print("=" * 55)
    print("NEW AEGIE INTERVIEW")
    print("=" * 55)

    print(
        "Participant:",
        participant_id
    )

    print(
        "Job Role:",
        job_role
    )

    print(
        "Collection Mode:",
        COLLECTION_MODE
    )

    print(
        "Active Dataset:",
        DATASET_PATH
    )

    if COLLECTION_MODE == "PILOT":

        pilot_schedule = (
            get_pilot_difficulty_schedule(
                participant_id
            )
        )

        print(
            "Pilot Question Mode: STATIC / NON-ADAPTIVE"
        )

        print(
            "Pilot Difficulty Schedule:",
            " -> ".join(
                pilot_schedule
            )
        )

        print(
            "AEGIE adaptive decisions will NOT "
            "control pilot question selection."
        )

    elif COLLECTION_MODE == "DEVELOPMENT":

        print(
            "Development Question Mode: STATIC / 5 QUESTIONS"
        )

        print(
            "Development Difficulty Schedule: "
            "Easy -> Medium -> Hard -> Easy -> Medium"
        )

        print(
            "This DEVELOPMENT schedule is for software testing only."
        )

    else:

        print(
            "Question 1 will be selected "
            "by the Interview Agent."
        )

    print("=" * 55)


    return redirect(
        url_for("interview")
    )


# ============================================================
# INTERVIEW LENGTH
# ============================================================

def get_interview_question_limit():

    # DEVELOPMENT is shortened to five questions for testing.
    # PILOT and FINAL remain at ten because the research design
    # currently uses 10 genuine responses per participant.

    if COLLECTION_MODE == "DEVELOPMENT":
        return 5

    return 10



# ============================================================
# INTERVIEW
# ============================================================

@app.route("/interview")
def interview():

    if "participant_id" not in session:

        return redirect(
            url_for("home")
        )


    question_number = session.get(
        "question_number",
        1
    )


    # --------------------------------------------------------
    # INTERVIEW COMPLETE
    # --------------------------------------------------------

    question_limit = (
        get_interview_question_limit()
    )


    if question_number > question_limit:

        return redirect(
            url_for(
                "results"
            )
        )


    # --------------------------------------------------------
    # Prevent question changing on page refresh.
    # --------------------------------------------------------

    question = session.get(
        "current_question"
    )


    if question is None:

        question = get_next_question()


        # ----------------------------------------------------
        # No scientifically valid adaptive decision yet.
        # ----------------------------------------------------

        if question is None:

            if question_number > 1:

                stt_status = session.get(
                    "last_stt_status",
                    "NOT_RUN"
                )

                stt_error = session.get(
                    "last_stt_error"
                )

                evaluation_status = session.get(
                    "last_evaluation_status",
                    "NOT_RUN"
                )

                adaptive_status = session.get(
                    "last_adaptive_status",
                    "NOT_RUN"
                )

                feedback_status = session.get(
                    "last_feedback_status",
                    "NOT_RUN"
                )

                stt_error_html = ""

                if stt_error:

                    stt_error_html = (
                        "<br><b>STT Detail:</b> "
                        + str(stt_error)
                    )

                return f"""
                <h2>
                Response Saved Successfully
                </h2>

                <p>
                Your genuine voice recording has already
                been saved to the {DATASET_LABEL}.
                </p>

                <p>
                The AEGIE agents are connected, but the next
                adaptive question cannot yet be selected.
                </p>

                <p>
                <b>Collection Mode:</b>
                {COLLECTION_MODE}
                <br>
                <b>Dataset:</b>
                {DATASET_PATH}
                </p>

                <p>
                <b>STT:</b>
                {stt_status}
                {stt_error_html}
                <br>
                <b>Evaluation Agent:</b>
                {evaluation_status}
                <br>
                <b>Adaptive Agent:</b>
                {adaptive_status}
                <br>
                <b>Feedback Agent:</b>
                {feedback_status}
                </p>

                <p>
                If the approved Parakeet model is unavailable,
                no transcript is fabricated and the original
                audio remains preserved for later processing.
                Final AEGIE scoring and adaptive decisions also
                require calibration using genuine human-annotated
                research data.
                </p>

                <p>
                No random Easy / Medium / Hard decision will
                be substituted.
                </p>

                <a href="/">
                Return Home
                </a>
                """


            return """
            <h2>
            No suitable question available.
            </h2>

            <p>
            Please check the question bank.
            </p>

            <a href="/">
            Return Home
            </a>
            """


        session[
            "current_question"
        ] = question


    print()
    print("-" * 55)
    print("AEGIE INTERVIEW AGENT")

    print(
        "Question Number:",
        question_number
    )

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

    print("-" * 55)


    return render_template(

        "interview.html",

        participant_id=
            session["participant_id"],

        job_role=
            session["job_role"],

        question_number=
            question_number,

        question_id=
            question["question_id"],

        question_text=
            question["question_text"],

        difficulty=
            question["difficulty"],

        total_questions=
            (
                5
                if COLLECTION_MODE == "DEVELOPMENT"
                else 10
            )
    )


# ============================================================
# RESEARCH RESULTS DASHBOARD
# ============================================================

@app.route(
    "/results"
)
def results():
    """
    Show only the responses created in the current interview session.

    The dashboard uses:
    - genuine primary response rows from the active dataset
    - stored MiniLM/speech evaluation features when available
    - genuine human labels only when they actually exist
    - genuine calibrated AEGIE scores only when they actually exist

    Missing research values remain visibly pending.
    Nothing is fabricated for display.
    """

    if "participant_id" not in session:

        return redirect(
            url_for(
                "home"
            )
        )


    sample_ids = session.get(
        "current_interview_sample_ids",
        []
    )


    if not sample_ids:

        return (
            """
            <h2>No current interview results are available.</h2>
            <p>
            Start and save at least one interview response first.
            </p>
            <a href="/">Return Home</a>
            """,
            400
        )


    # --------------------------------------------------------
    # ACTIVE FEATURE STORE PATH
    # --------------------------------------------------------

    if COLLECTION_MODE == "FINAL":

        feature_store_path = os.path.join(
            "data",
            "evaluation_features.csv"
        )

    elif COLLECTION_MODE == "PILOT":

        feature_store_path = os.path.join(
            "data",
            "pilot_evaluation_features.csv"
        )

    else:

        feature_store_path = os.path.join(
            "data",
            "development_evaluation_features.csv"
        )


    # --------------------------------------------------------
    # LOAD CURRENT PRIMARY RESPONSE ROWS
    # --------------------------------------------------------

    if not os.path.isfile(
        DATASET_PATH
    ):

        return (
            "Active dataset file is missing.",
            500
        )


    try:

        dataset_df = pd.read_csv(
            DATASET_PATH
        )

    except Exception as error:

        return (
            "Unable to read active dataset: "
            + str(
                error
            ),
            500
        )


    if "sample_id" not in dataset_df.columns:

        return (
            "Active dataset has no sample_id column.",
            500
        )


    dataset_df[
        "sample_id"
    ] = dataset_df[
        "sample_id"
    ].astype(
        str
    )


    sample_ids = [
        str(
            sample_id
        )
        for sample_id in sample_ids
    ]


    order_map = {
        sample_id:
            index
        for index, sample_id
        in enumerate(
            sample_ids,
            start=1
        )
    }


    current_df = dataset_df[
        dataset_df[
            "sample_id"
        ].isin(
            sample_ids
        )
    ].copy()


    if current_df.empty:

        return (
            "The current interview sample IDs were not found "
            "in the active dataset.",
            500
        )


    if current_df[
        "sample_id"
    ].duplicated(
        keep=False
    ).any():

        return (
            "Duplicate sample_id detected in the active dataset. "
            "Results dashboard blocked for research integrity.",
            500
        )


    current_df[
        "_question_order"
    ] = current_df[
        "sample_id"
    ].map(
        order_map
    )


    current_df = (
        current_df
        .sort_values(
            "_question_order"
        )
        .reset_index(
            drop=True
        )
    )


    # --------------------------------------------------------
    # MERGE STORED SEMANTIC FEATURE EVIDENCE
    # --------------------------------------------------------

    feature_columns_needed = [
        "sample_id",
        "whole_mean_similarity",
        "sentence_mean_best_similarity",
    ]


    if os.path.isfile(
        feature_store_path
    ):

        try:

            feature_df = pd.read_csv(
                feature_store_path
            )


            available_feature_columns = [
                column
                for column in feature_columns_needed
                if column in feature_df.columns
            ]


            if "sample_id" in available_feature_columns:

                feature_subset = feature_df[
                    available_feature_columns
                ].copy()


                feature_subset[
                    "sample_id"
                ] = feature_subset[
                    "sample_id"
                ].astype(
                    str
                )


                feature_subset = (
                    feature_subset
                    .drop_duplicates(
                        subset=[
                            "sample_id"
                        ],
                        keep="last"
                    )
                )


                current_df = current_df.merge(
                    feature_subset,
                    on="sample_id",
                    how="left",
                    validate="one_to_one"
                )


        except Exception as error:

            print(
                "Results dashboard feature merge warning:",
                str(
                    error
                )
            )


    for semantic_column in [
        "whole_mean_similarity",
        "sentence_mean_best_similarity",
    ]:

        if semantic_column not in current_df.columns:

            current_df[
                semantic_column
            ] = None


    # --------------------------------------------------------
    # DISPLAY HELPERS
    # --------------------------------------------------------

    def _numeric_series(
        dataframe,
        column_name,
    ):

        if column_name not in dataframe.columns:

            return pd.Series(
                dtype=float
            )


        return pd.to_numeric(
            dataframe[
                column_name
            ],
            errors="coerce"
        )


    def _mean_or_none(
        dataframe,
        column_name,
        digits=2,
    ):

        values = _numeric_series(
            dataframe,
            column_name
        ).dropna()


        if values.empty:

            return None


        return round(
            float(
                values.mean()
            ),
            digits
        )


    def _sum_or_zero(
        dataframe,
        column_name,
    ):

        values = _numeric_series(
            dataframe,
            column_name
        ).dropna()


        if values.empty:

            return 0


        return int(
            round(
                float(
                    values.sum()
                )
            )
        )


    def _value_or_none(
        raw_value,
        digits=None,
    ):

        if pd.isna(
            raw_value
        ):

            return None


        if digits is None:

            return raw_value


        try:

            return round(
                float(
                    raw_value
                ),
                digits
            )

        except (
            TypeError,
            ValueError,
        ):

            return raw_value


    # --------------------------------------------------------
    # CURRENT INTERVIEW SUMMARY
    # --------------------------------------------------------

    avg_wpm = _mean_or_none(
        current_df,
        "wpm",
        2
    )


    total_fillers = _sum_or_zero(
        current_df,
        "filler_count"
    )


    total_pauses = _sum_or_zero(
        current_df,
        "pause_count"
    )


    avg_semantic_mean = _mean_or_none(
        current_df,
        "whole_mean_similarity",
        4
    )


    # --------------------------------------------------------
    # HUMAN VS AEGIE COMPARISON
    # --------------------------------------------------------
    #
    # These are current-interview means only.
    # If human labels or calibrated AEGIE scores do not exist,
    # the template displays a transparent pending state.
    # --------------------------------------------------------

    comparison_spec = [
        (
            "Relevance",
            "relevance_score",
            "aegie_relevance_score"
        ),
        (
            "Technical",
            "technical_score",
            "aegie_technical_score"
        ),
        (
            "Clarity",
            "clarity_score",
            "aegie_clarity_score"
        ),
        (
            "Communication",
            "communication_score",
            "aegie_communication_score"
        ),
        (
            "Overall",
            "overall_score",
            "aegie_overall_score"
        ),
    ]


    comparison_rows = []


    for (
        label,
        human_column,
        aegie_column,
    ) in comparison_spec:

        comparison_rows.append({
            "label":
                label,

            "human_value":
                _mean_or_none(
                    current_df,
                    human_column,
                    2
                ),

            "aegie_value":
                _mean_or_none(
                    current_df,
                    aegie_column,
                    2
                ),
        })


    # --------------------------------------------------------
    # RESPONSE-BY-RESPONSE EVIDENCE
    # --------------------------------------------------------

    responses = []


    for row_index, row in current_df.iterrows():

        responses.append({
            "question_number":
                int(
                    row[
                        "_question_order"
                    ]
                ),

            "sample_id":
                str(
                    row[
                        "sample_id"
                    ]
                ),

            "question_id":
                str(
                    row.get(
                        "question_id",
                        ""
                    )
                ),

            "question_text":
                str(
                    row.get(
                        "question_text",
                        ""
                    )
                ),

            "difficulty":
                str(
                    row.get(
                        "difficulty",
                        ""
                    )
                ),

            "transcript":
                (
                    ""
                    if pd.isna(
                        row.get(
                            "transcript"
                        )
                    )
                    else str(
                        row.get(
                            "transcript",
                            ""
                        )
                    )
                ),

            "duration_sec":
                _value_or_none(
                    row.get(
                        "duration_sec"
                    ),
                    2
                ),

            "word_count":
                _value_or_none(
                    row.get(
                        "word_count"
                    )
                ),

            "wpm":
                _value_or_none(
                    row.get(
                        "wpm"
                    ),
                    2
                ),

            "filler_count":
                _value_or_none(
                    row.get(
                        "filler_count"
                    )
                ),

            "pause_count":
                _value_or_none(
                    row.get(
                        "pause_count"
                    )
                ),

            "whole_mean_similarity":
                _value_or_none(
                    row.get(
                        "whole_mean_similarity"
                    ),
                    4
                ),

            "sentence_mean_best_similarity":
                _value_or_none(
                    row.get(
                        "sentence_mean_best_similarity"
                    ),
                    4
                ),
        })


    return render_template(
        "results.html",

        participant_id=
            session.get(
                "participant_id"
            ),

        job_role=
            session.get(
                "job_role"
            ),

        collection_mode=
            COLLECTION_MODE,

        response_count=
            len(
                responses
            ),

        expected_count=
            get_interview_question_limit(),

        avg_wpm=
            avg_wpm,

        total_fillers=
            total_fillers,

        total_pauses=
            total_pauses,

        avg_semantic_mean=
            avg_semantic_mean,

        stt_status=
            session.get(
                "last_stt_status",
                "NOT_RUN"
            ),

        evaluation_status=
            session.get(
                "last_evaluation_status",
                "NOT_RUN"
            ),

        adaptive_status=
            session.get(
                "last_adaptive_status",
                "NOT_RUN"
            ),

        feedback_status=
            session.get(
                "last_feedback_status",
                "NOT_RUN"
            ),

        comparison_rows=
            comparison_rows,

        responses=
            responses,
    )


# ============================================================
# SAVE AUDIO
# ============================================================

@app.route(
    "/save_audio",
    methods=["POST"]
)
def save_audio():

    # --------------------------------------------------------
    # DEVELOPMENT PERFORMANCE TIMER
    # --------------------------------------------------------
    # Diagnostic only. It does not change research features,
    # transcripts, scores, question selection, or stored data.

    save_start_time = time.perf_counter()

    timing_audio_save = None
    timing_audio_analysis = None
    timing_stt = None
    timing_speech_features = None
    timing_dataset_save = None
    timing_agent_pipeline = None
    timing_feature_store = None

    # --------------------------------------------------------
    # SESSION CHECK
    # --------------------------------------------------------

    if "participant_id" not in session:

        return jsonify({

            "success":
                False,

            "message":
                "Interview session expired."

        }), 400


    # --------------------------------------------------------
    # AUDIO CHECK
    # --------------------------------------------------------

    if "audio" not in request.files:

        return jsonify({

            "success":
                False,

            "message":
                "No audio received."

        }), 400


    participant_id = session[
        "participant_id"
    ]

    job_role = session[
        "job_role"
    ]

    current_question = session.get(
        "current_question"
    )


    if not current_question:

        return jsonify({

            "success":
                False,

            "message":
                "No active question."

        }), 400


    question_number = session.get(
        "question_number",
        1
    )

    question_id = current_question[
        "question_id"
    ]

    question_text = current_question[
        "question_text"
    ]

    difficulty = current_question[
        "difficulty"
    ]


    # ========================================================
    # AUDIO DIRECTORY
    # ========================================================

    participant_folder = os.path.join(
        AUDIO_ROOT,
        participant_id
    )

    os.makedirs(
        participant_folder,
        exist_ok=True
    )


    # ========================================================
    # SAMPLE ID
    # ========================================================

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    sample_id = (
        f"AEGIE_"
        f"{participant_id}_"
        f"{question_id}_"
        f"{timestamp}"
    )


    filepath = os.path.join(
        participant_folder,
        sample_id + ".webm"
    )


    # ========================================================
    # SAVE AUDIO
    # ========================================================

    audio_file = request.files[
        "audio"
    ]


    audio_save_start = time.perf_counter()

    try:

        audio_file.save(
            filepath
        )

        timing_audio_save = (
            time.perf_counter()
            - audio_save_start
        )

    except Exception as e:

        print(
            "Audio save error:",
            e
        )

        return jsonify({

            "success":
                False,

            "message":
                "Audio could not be saved."

        }), 500


    # ========================================================
    # OBJECTIVE AUDIO FEATURES
    # ========================================================

    audio_analysis_start = time.perf_counter()

    duration_sec = get_audio_duration(
        filepath
    )

    pause_count = get_pause_count(
        filepath
    )

    timing_audio_analysis = (
        time.perf_counter()
        - audio_analysis_start
    )


    # ========================================================
    # QUALITY CHECK
    # ========================================================

    quality_result = check_audio_quality(
        duration_sec,
        pause_count
    )


    print()
    print("-" * 55)
    print("AEGIE AUDIO QUALITY CHECK")

    print(
        "Status:",
        quality_result["status"]
    )

    print(
        "Usable:",
        quality_result["usable"]
    )

    print(
        "Reason:",
        quality_result["reason"]
    )

    print("-" * 55)


    # ========================================================
    # REJECT BAD RECORDING
    # ========================================================

    if not quality_result["usable"]:

        try:

            if os.path.exists(
                filepath
            ):

                os.remove(
                    filepath
                )

        except Exception as e:

            print(
                "Audio cleanup error:",
                e
            )


        # Do not advance interview.
        # Participant can answer the same question again.

        return jsonify({

            "success":
                False,

            "message":
                quality_result["reason"],

            "quality_status":
                quality_result["status"]

        }), 400


    # --------------------------------------------------------
    # Preserve numeric values for agent state, while using
    # blank strings in CSV when a value is unavailable.
    # --------------------------------------------------------

    agent_duration_sec = duration_sec
    agent_pause_count = pause_count

    csv_duration_sec = (
        duration_sec
        if duration_sec is not None
        else ""
    )

    csv_pause_count = (
        pause_count
        if pause_count is not None
        else ""
    )


    # ========================================================
    # ACCEPTED AUDIO
    # ========================================================

    print()
    print("-" * 55)
    print("AEGIE AUDIO ACCEPTED")

    print(
        "Sample ID:",
        sample_id
    )

    print(
        "Audio:",
        filepath
    )

    print(
        "Duration:",
        csv_duration_sec
    )

    print(
        "Pause Count:",
        csv_pause_count
    )

    print("-" * 55)


    # ========================================================
    # SPEECH-TO-TEXT
    # ========================================================
    #
    # The STT layer is now connected to Flask.
    #
    # If the approved Parakeet model exists:
    #     audio -> transcript -> speech features -> agents
    #
    # If the model is unavailable or STT fails:
    #     raw audio remains saved
    #     transcript stays blank
    #     no transcript-derived feature is fabricated
    # ========================================================

    print()
    print("-" * 55)
    print("AEGIE SPEECH-TO-TEXT")


    stt_start = time.perf_counter()

    try:

        stt_result = transcribe_audio(
            filepath
        )

    except Exception as error:

        stt_result = {
            "success": False,
            "status": "TRANSCRIPTION_EXCEPTION",
            "transcript": None,
            "engine": "parakeet-tdt-0.6b-v2-int8",
            "error": str(error)
        }

    timing_stt = (
        time.perf_counter()
        - stt_start
    )


    stt_status = stt_result.get(
        "status",
        "TRANSCRIPTION_FAILED"
    )

    stt_error = stt_result.get(
        "error"
    )


    session[
        "last_stt_status"
    ] = stt_status

    session[
        "last_stt_error"
    ] = stt_error


    print(
        "Status:",
        stt_status
    )

    print(
        "Engine:",
        stt_result.get(
            "engine"
        )
    )


    if stt_result.get(
        "success",
        False
    ):

        transcript = str(
            stt_result.get(
                "transcript",
                ""
            )
        ).strip()


        speech_features_start = time.perf_counter()

        speech_result = (
            extract_speech_features(
                transcript,
                agent_duration_sec
            )
        )

        timing_speech_features = (
            time.perf_counter()
            - speech_features_start
        )


        word_count = speech_result.get(
            "word_count"
        )

        wpm = speech_result.get(
            "wpm"
        )

        filler_count = speech_result.get(
            "filler_count"
        )


        print(
            "Transcript:",
            transcript
        )

        print(
            "Word Count:",
            word_count
        )

        print(
            "WPM:",
            wpm
        )

        print(
            "Filler Count:",
            filler_count
        )

    else:

        transcript = ""
        word_count = None
        wpm = None
        filler_count = None
        timing_speech_features = 0.0


        print(
            "Transcript: NOT GENERATED"
        )

        print(
            "Reason:",
            stt_error
        )

        print(
            "Original audio preserved for later processing."
        )

        print(
            "No transcript was fabricated."
        )


    print("-" * 55)


    # ========================================================
    # DATASET ROW
    # ========================================================

    new_row = {

        "sample_id":
            sample_id,

        "participant_id":
            participant_id,

        "job_role":
            job_role,

        "question_id":
            question_id,

        "question_text":
            question_text,

        "difficulty":
            difficulty,

        "audio_path":
            filepath,


        # Genuine STT transcript when available.
        # Blank when STT is unavailable or fails.
        "transcript":
            transcript,


        "duration_sec":
            csv_duration_sec,

        "word_count":
            (
                word_count
                if word_count is not None
                else ""
            ),

        "wpm":
            (
                wpm
                if wpm is not None
                else ""
            ),

        "filler_count":
            (
                filler_count
                if filler_count is not None
                else ""
            ),

        "pause_count":
            csv_pause_count,


        # ----------------------------------------------------
        # HUMAN REFERENCE LABELS
        # ----------------------------------------------------

        "relevance_score":
            "",

        "technical_score":
            "",

        "clarity_score":
            "",

        "communication_score":
            "",

        "overall_score":
            "",

        "annotator_id":
            "",


        # ----------------------------------------------------
        # AEGIE PREDICTIONS
        # ----------------------------------------------------
        #
        # Final scores remain blank until a scientifically
        # calibrated scoring model exists.
        # ----------------------------------------------------

        "aegie_relevance_score":
            "",

        "aegie_technical_score":
            "",

        "aegie_clarity_score":
            "",

        "aegie_communication_score":
            "",

        "aegie_overall_score":
            "",

        "aegie_next_difficulty":
            ""
    }


    # ========================================================
    # WRITE DATASET
    # ========================================================

    dataset_save_start = time.perf_counter()

    try:

        row_df = pd.DataFrame(
            [new_row],
            columns=DATASET_COLUMNS
        )

        row_df.to_csv(
            DATASET_PATH,
            mode="a",
            header=False,
            index=False
        )

        timing_dataset_save = (
            time.perf_counter()
            - dataset_save_start
        )

    except Exception as e:

        print(
            "Dataset save error:",
            e
        )

        # Keep audio and dataset consistent.

        try:

            if os.path.exists(
                filepath
            ):

                os.remove(
                    filepath
                )

        except Exception:
            pass


        return jsonify({

            "success":
                False,

            "message":
                "Dataset row could not be saved."

        }), 500


    print(
        "Dataset row saved successfully."
    )


    # ========================================================
    # RUN CONNECTED AEGIE AGENTS
    # ========================================================
    #
    # IMPORTANT:
    # Saving genuine primary data does NOT depend on model
    # availability. The recording is already safely stored.
    # If an AI component is unavailable, the raw sample remains
    # preserved and can be processed later.
    # ========================================================

    asked_before_advance = session.get(
        "asked_question_ids",
        []
    )


    try:

        agent_pipeline_start = time.perf_counter()

        agent_state = run_post_response_agents(

            participant_id=
                participant_id,

            job_role=
                job_role,

            question_number=
                question_number,

            asked_question_ids=
                asked_before_advance,

            current_question=
                current_question,

            transcript=
                transcript,

            duration_sec=
                agent_duration_sec,

            word_count=
                word_count,

            wpm=
                wpm,

            filler_count=
                filler_count,

            pause_count=
                agent_pause_count
        )

        timing_agent_pipeline = (
            time.perf_counter()
            - agent_pipeline_start
        )


        # ----------------------------------------------------
        # SAVE RESEARCH EVALUATION FEATURES
        # ----------------------------------------------------
        #
        # Feature persistence is separate from:
        # - primary response dataset
        # - human ground-truth annotations
        # - final calibrated AEGIE scores
        #
        # A feature-store failure must NOT delete genuine
        # participant audio or the already-saved response row.
        # ----------------------------------------------------

        evaluation_features = agent_state.get(
            "evaluation_features"
        )

        evaluation_status = agent_state.get(
            "evaluation_status"
        )


        if (
            evaluation_status
            == "EVALUATION_FEATURES_READY"
            and isinstance(
                evaluation_features,
                dict
            )
        ):

            feature_store_start = time.perf_counter()

            feature_save_result = (
                save_evaluation_features(

                    sample_id=
                        sample_id,

                    collection_mode=
                        COLLECTION_MODE,

                    features=
                        evaluation_features
                )
            )

            timing_feature_store = (
                time.perf_counter()
                - feature_store_start
            )


            print()

            print("-" * 55)

            print(
                "AEGIE FEATURE STORE"
            )

            print(
                "Status:",
                feature_save_result.get(
                    "status"
                )
            )

            print(
                "Path:",
                feature_save_result.get(
                    "path"
                )
            )


            if not feature_save_result.get(
                "success",
                False
            ):

                print(
                    "Feature Save Error:",
                    feature_save_result.get(
                        "error"
                    )
                )


            print("-" * 55)


        else:

            timing_feature_store = 0.0

            print()

            print("-" * 55)

            print(
                "AEGIE FEATURE STORE"
            )

            print(
                "Feature record not saved."
            )

            print(
                "Evaluation Status:",
                evaluation_status
            )

            print(
                "Reason: evaluation features "
                "are not ready."
            )

            print("-" * 55)


        # ----------------------------------------------------
        # SAVE CALIBRATED AEGIE SCORES TO PRIMARY ROW
        # ----------------------------------------------------
        #
        # The primary response row was intentionally created
        # before the AI pipeline ran so genuine audio/transcript
        # data would not depend on model availability.
        #
        # If, and only if, the frozen calibrated scoring model
        # produced valid 1-5 scores, update those five AEGIE
        # prediction columns in the SAME sample_id row.
        #
        # This does not:
        # - append a duplicate primary row
        # - modify human annotation labels
        # - write an adaptive difficulty decision
        # ----------------------------------------------------

        calibrated_scores = agent_state.get(
            "aegie_scores"
        )

        calibrated_scoring_status = agent_state.get(
            "calibrated_scoring_status"
        )


        if (
            calibrated_scoring_status
            == "CALIBRATED_SCORES_READY"
            and isinstance(
                calibrated_scores,
                dict
            )
        ):

            score_save_result = (
                update_primary_row_with_calibrated_scores(
                    dataset_path=
                        DATASET_PATH,

                    sample_id=
                        sample_id,

                    scores=
                        calibrated_scores
                )
            )


            print()

            print("-" * 55)

            print(
                "AEGIE CALIBRATED SCORE STORE"
            )

            print(
                "Status:",
                score_save_result.get(
                    "status"
                )
            )


            if not score_save_result.get(
                "success",
                False
            ):

                print(
                    "Score Save Error:",
                    score_save_result.get(
                        "error"
                    )
                )

                print(
                    "Primary response row remains preserved."
                )

            else:

                print(
                    "Sample ID:",
                    sample_id
                )

                print(
                    "Five calibrated AEGIE scores "
                    "saved to existing row."
                )


            print("-" * 55)


        else:

            print()

            print("-" * 55)

            print(
                "AEGIE CALIBRATED SCORE STORE"
            )

            print(
                "Primary row not updated."
            )

            print(
                "Calibrated Scoring Status:",
                calibrated_scoring_status
            )

            print(
                "Reason: valid calibrated "
                "1-5 scores are not available."
            )

            print("-" * 55)


        session[
            "last_evaluation_status"
        ] = agent_state.get(
            "evaluation_status",
            "UNKNOWN"
        )

        session[
            "last_adaptive_status"
        ] = agent_state.get(
            "adaptive_status",
            "UNKNOWN"
        )

        session[
            "last_feedback_status"
        ] = agent_state.get(
            "feedback_status",
            "UNKNOWN"
        )


        next_difficulty = agent_state.get(
            "next_difficulty"
        )


        # ----------------------------------------------------
        # DEVELOPMENT / PILOT MODES
        #
        # Ignore any uncalibrated adaptive decision for question
        # selection. DEVELOPMENT uses its deterministic software
        # test schedule; PILOT uses its frozen research schedule.
        # ----------------------------------------------------

        if COLLECTION_MODE in {
            "DEVELOPMENT",
            "PILOT"
        }:

            session[
                "target_difficulty"
            ] = None


        elif next_difficulty in {
            "Easy",
            "Medium",
            "Hard"
        }:

            session[
                "target_difficulty"
            ] = next_difficulty

        else:

            session[
                "target_difficulty"
            ] = None


    except Exception as error:

        if timing_agent_pipeline is None:
            timing_agent_pipeline = (
                time.perf_counter()
                - agent_pipeline_start
            )

        if timing_feature_store is None:
            timing_feature_store = 0.0

        # Do not delete genuine audio or the dataset row merely
        # because an AI component failed after data collection.

        print()
        print("-" * 55)
        print("AEGIE AGENT PIPELINE ERROR")
        print("Reason:", error)
        print("Primary recording remains saved.")
        print("-" * 55)


        session[
            "last_evaluation_status"
        ] = "PIPELINE_ERROR"

        session[
            "last_adaptive_status"
        ] = "WAITING_FOR_EVALUATION"

        session[
            "last_feedback_status"
        ] = "WAITING_FOR_EVALUATION"

        session[
            "target_difficulty"
        ] = None


    # ========================================================
    # MARK QUESTION COMPLETED
    # ========================================================

    asked = session.get(
        "asked_question_ids",
        []
    )

    if question_id not in asked:

        asked.append(
            question_id
        )

    session[
        "asked_question_ids"
    ] = asked


    # --------------------------------------------------------
    # TRACK CURRENT-INTERVIEW SAMPLE
    # --------------------------------------------------------

    current_interview_sample_ids = session.get(
        "current_interview_sample_ids",
        []
    )

    if sample_id not in current_interview_sample_ids:

        current_interview_sample_ids.append(
            sample_id
        )

    session[
        "current_interview_sample_ids"
    ] = current_interview_sample_ids


    # ========================================================
    # ADVANCE QUESTION NUMBER
    # ========================================================

    session[
        "question_number"
    ] = (
        question_number
        + 1
    )


    session.pop(
        "current_question",
        None
    )


    # ========================================================
    # DEVELOPMENT PERFORMANCE SUMMARY
    # ========================================================

    total_save_time = (
        time.perf_counter()
        - save_start_time
    )

    if COLLECTION_MODE == "DEVELOPMENT":

        def _display_time(value):

            if value is None:
                return "N/A"

            return f"{value:.3f} sec"


        print()
        print("=" * 55)
        print("AEGIE SAVE PERFORMANCE")
        print("=" * 55)

        print(
            "Audio file save:",
            _display_time(
                timing_audio_save
            )
        )

        print(
            "Audio duration + pause analysis:",
            _display_time(
                timing_audio_analysis
            )
        )

        print(
            "Parakeet STT:",
            _display_time(
                timing_stt
            )
        )

        print(
            "Speech features:",
            _display_time(
                timing_speech_features
            )
        )

        print(
            "Dataset CSV save:",
            _display_time(
                timing_dataset_save
            )
        )

        print(
            "AEGIE agent / MiniLM pipeline:",
            _display_time(
                timing_agent_pipeline
            )
        )

        print(
            "Evaluation feature store:",
            _display_time(
                timing_feature_store
            )
        )

        print("-" * 55)

        print(
            "TOTAL SAVE TIME:",
            _display_time(
                total_save_time
            )
        )

        print("=" * 55)


    # ========================================================
    # SUCCESS
    # ========================================================

    return jsonify({

        "success":
            True,

        "message":
            "Response saved successfully.",

        "collection_mode":
            COLLECTION_MODE,

        "dataset_path":
            DATASET_PATH,

        "sample_id":
            sample_id,

        "duration_sec":
            csv_duration_sec,

        "pause_count":
            csv_pause_count,

        "quality_status":
            quality_result["status"],

        "stt_status":
            session.get(
                "last_stt_status"
            ),

        "evaluation_status":
            session.get(
                "last_evaluation_status"
            ),

        "adaptive_status":
            session.get(
                "last_adaptive_status"
            ),

        "feedback_status":
            session.get(
                "last_feedback_status"
            ),

        "next_difficulty":
            session.get(
                "target_difficulty"
            ),

        "next_url":
            url_for("interview")

    })


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    ensure_datasets()

    print()
    print("=" * 55)
    print("AEGIE Research Framework")
    print("=" * 55)

    print(
        "Collection Mode:",
        COLLECTION_MODE
    )

    print(
        "Active Dataset:",
        DATASET_PATH
    )

    print(
        "Audio Root:",
        AUDIO_ROOT
    )

    if COLLECTION_MODE == "DEVELOPMENT":

        print(
            "Pilot Dataset: INACTIVE"
        )

        print(
            "Final Research Dataset: PROTECTED"
        )

    elif COLLECTION_MODE == "PILOT":

        print(
            "Pilot Dataset: ACTIVE"
        )

        print(
            "Pilot Question Mode: STATIC / NON-ADAPTIVE"
        )

        print(
            "Pilot Participant IDs: PL001-PL300"
        )

        print(
            "Final Research Dataset: PROTECTED"
        )

    else:

        print(
            "Pilot Dataset: INACTIVE"
        )

        print(
            "Final Research Dataset: ACTIVE - CONFIRMED"
        )

    print()

    print(
        "Interview Agent: CONNECTED"
    )

    print(
        "Question Selector: CONNECTED"
    )

    print(
        "72-Question Reference Registry: CONNECTED"
    )

    print(
        "MiniLM Semantic Evaluation: CONNECTED"
    )

    print(
        "STT Layer: CONNECTED"
    )

    print(
        "Parakeet Model: CHECKED AT RUNTIME"
    )

    print(
        "Evaluation Agent: CONNECTED"
    )

    print(
        "Adaptive Agent: CONNECTED - CALIBRATION PENDING"
    )

    print(
        "Feedback Agent: CONNECTED - CALIBRATION PENDING"
    )

    print()
    print(
        "Open: http://127.0.0.1:5000"
    )

    print("=" * 55)


    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False,
        threaded=True
    )
