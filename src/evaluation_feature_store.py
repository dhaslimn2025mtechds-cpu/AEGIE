# ============================================================
# AEGIE EVALUATION FEATURE STORE
# ============================================================
#
# Purpose:
#
# Persist AEGIE research evaluation features in a separate CSV.
#
# This keeps:
#
#   Primary response data
#   Human reference labels
#   Machine-generated research features
#
# logically separated.
#
# IMPORTANT:
#
# - Human annotation labels are NOT stored here.
# - Final AEGIE 1-5 scores are NOT stored here.
# - participant_id is metadata only.
# - sample_id is the unique link to the response dataset.
# - Existing feature rows are never silently overwritten.
# ============================================================

import os
import threading
from datetime import datetime, timezone

import pandas as pd


# ============================================================
# FEATURE FILE PATHS
# ============================================================

DEVELOPMENT_FEATURE_PATH = os.path.join(
    "data",
    "development_evaluation_features.csv"
)

PILOT_FEATURE_PATH = os.path.join(
    "data",
    "pilot_evaluation_features.csv"
)

FINAL_FEATURE_PATH = os.path.join(
    "data",
    "evaluation_features.csv"
)


# ============================================================
# FEATURE TABLE SCHEMA
# ============================================================

FEATURE_COLUMNS = [

    # --------------------------------------------------------
    # LINKING / RESEARCH METADATA
    # --------------------------------------------------------

    "sample_id",
    "participant_id",
    "job_role",
    "question_id",
    "difficulty",
    "collection_mode",

    # --------------------------------------------------------
    # WHOLE-ANSWER MINILM FEATURES
    # --------------------------------------------------------

    "whole_mean_similarity",
    "whole_max_similarity",
    "whole_min_similarity",

    # --------------------------------------------------------
    # SENTENCE-LEVEL SEMANTIC FEATURES
    # --------------------------------------------------------

    "sentence_mean_best_similarity",
    "sentence_max_best_similarity",
    "sentence_min_best_similarity",

    # --------------------------------------------------------
    # SEMANTIC STRUCTURE FEATURES
    # --------------------------------------------------------

    "reference_concept_count",
    "answer_sentence_count",

    # --------------------------------------------------------
    # OBJECTIVE SPEECH FEATURES
    # --------------------------------------------------------

    "duration_sec",
    "word_count",
    "wpm",
    "filler_count",
    "pause_count",

    # --------------------------------------------------------
    # DERIVED SPEECH FEATURES
    # --------------------------------------------------------

    "filler_rate_per_100_words",
    "pause_rate_per_minute",

    # --------------------------------------------------------
    # REPRODUCIBILITY METADATA
    # --------------------------------------------------------

    "feature_status",
    "created_at_utc"
]


# ============================================================
# EXPECTED FEATURE KEYS
# ============================================================

EXPECTED_FEATURE_KEYS = [

    "participant_id",
    "job_role",
    "question_id",
    "difficulty",

    "whole_mean_similarity",
    "whole_max_similarity",
    "whole_min_similarity",

    "sentence_mean_best_similarity",
    "sentence_max_best_similarity",
    "sentence_min_best_similarity",

    "reference_concept_count",
    "answer_sentence_count",

    "duration_sec",
    "word_count",
    "wpm",
    "filler_count",
    "pause_count",

    "filler_rate_per_100_words",
    "pause_rate_per_minute"
]


# ============================================================
# IN-PROCESS WRITE LOCK
# ============================================================

_FEATURE_FILE_LOCK = threading.Lock()


# ============================================================
# HELPERS
# ============================================================

def _clean_text(value):

    if value is None:
        return ""

    try:

        if pd.isna(value):
            return ""

    except Exception:
        pass

    return str(value).strip()


def _normalize_mode(
    collection_mode
):

    mode = _clean_text(
        collection_mode
    ).upper()

    if mode not in {
        "DEVELOPMENT",
        "PILOT",
        "FINAL"
    }:

        raise ValueError(
            "collection_mode must be "
            "DEVELOPMENT, PILOT, or FINAL."
        )

    return mode


def get_feature_path(
    collection_mode
):

    mode = _normalize_mode(
        collection_mode
    )

    if mode == "FINAL":

        return FINAL_FEATURE_PATH

    if mode == "PILOT":

        return PILOT_FEATURE_PATH

    return DEVELOPMENT_FEATURE_PATH


def _ensure_parent_directory(
    path
):

    parent = os.path.dirname(
        path
    )

    if parent:

        os.makedirs(
            parent,
            exist_ok=True
        )


def _create_empty_feature_file(
    path
):

    _ensure_parent_directory(
        path
    )

    dataframe = pd.DataFrame(
        columns=FEATURE_COLUMNS
    )

    dataframe.to_csv(
        path,
        index=False
    )


def ensure_feature_file(
    collection_mode
):

    path = get_feature_path(
        collection_mode
    )

    with _FEATURE_FILE_LOCK:

        if not os.path.exists(
            path
        ):

            _create_empty_feature_file(
                path
            )

            return {
                "success": True,
                "status": "FEATURE_FILE_CREATED",
                "path": path
            }

    return {
        "success": True,
        "status": "FEATURE_FILE_READY",
        "path": path
    }


# ============================================================
# VALIDATE EXISTING FEATURE FILE
# ============================================================

def validate_feature_file(
    collection_mode
):

    try:

        mode = _normalize_mode(
            collection_mode
        )

        path = get_feature_path(
            mode
        )

    except Exception as error:

        return {
            "success": False,
            "status": "INVALID_COLLECTION_MODE",
            "path": None,
            "error": str(error)
        }


    if not os.path.exists(
        path
    ):

        return {
            "success": False,
            "status": "FEATURE_FILE_MISSING",
            "path": path,
            "error": (
                "Evaluation feature file "
                "does not exist."
            )
        }


    try:

        dataframe = pd.read_csv(
            path
        )

    except pd.errors.EmptyDataError:

        return {
            "success": False,
            "status": "FEATURE_FILE_EMPTY_NO_SCHEMA",
            "path": path,
            "error": (
                "Feature file exists but "
                "contains no CSV schema."
            )
        }

    except Exception as error:

        return {
            "success": False,
            "status": "FEATURE_FILE_READ_ERROR",
            "path": path,
            "error": str(error)
        }


    actual_columns = list(
        dataframe.columns
    )


    if actual_columns != FEATURE_COLUMNS:

        missing = [

            column

            for column in FEATURE_COLUMNS

            if column not in actual_columns
        ]


        unexpected = [

            column

            for column in actual_columns

            if column not in FEATURE_COLUMNS
        ]


        return {
            "success": False,
            "status": "FEATURE_SCHEMA_MISMATCH",
            "path": path,
            "error": (
                "Feature CSV schema does not match "
                "the expected research schema."
            ),
            "missing_columns": missing,
            "unexpected_columns": unexpected
        }


    return {
        "success": True,
        "status": "FEATURE_FILE_VALID",
        "path": path,
        "rows": len(dataframe),
        "error": None
    }


# ============================================================
# BUILD FEATURE RECORD
# ============================================================

def build_feature_record(
    sample_id,
    collection_mode,
    features
):

    sample_id = _clean_text(
        sample_id
    )


    if not sample_id:

        return {
            "success": False,
            "status": "SAMPLE_ID_MISSING",
            "record": None,
            "error": (
                "sample_id is required."
            )
        }


    if not isinstance(
        features,
        dict
    ):

        return {
            "success": False,
            "status": "FEATURES_INVALID",
            "record": None,
            "error": (
                "features must be a dictionary."
            )
        }


    try:

        mode = _normalize_mode(
            collection_mode
        )

    except Exception as error:

        return {
            "success": False,
            "status": "INVALID_COLLECTION_MODE",
            "record": None,
            "error": str(error)
        }


    # --------------------------------------------------------
    # Check that the expected feature-builder keys exist.
    #
    # Values may legitimately be None for some measurements,
    # but the keys themselves should exist.
    # --------------------------------------------------------

    missing_keys = [

        key

        for key in EXPECTED_FEATURE_KEYS

        if key not in features
    ]


    if missing_keys:

        return {
            "success": False,
            "status": "FEATURE_KEYS_MISSING",
            "record": None,
            "error": (
                "Evaluation feature vector is missing: "
                + ", ".join(
                    missing_keys
                )
            )
        }


    record = {

        "sample_id":
            sample_id,

        "participant_id":
            features.get(
                "participant_id"
            ),

        "job_role":
            features.get(
                "job_role"
            ),

        "question_id":
            features.get(
                "question_id"
            ),

        "difficulty":
            features.get(
                "difficulty"
            ),

        "collection_mode":
            mode,


        "whole_mean_similarity":
            features.get(
                "whole_mean_similarity"
            ),

        "whole_max_similarity":
            features.get(
                "whole_max_similarity"
            ),

        "whole_min_similarity":
            features.get(
                "whole_min_similarity"
            ),


        "sentence_mean_best_similarity":
            features.get(
                "sentence_mean_best_similarity"
            ),

        "sentence_max_best_similarity":
            features.get(
                "sentence_max_best_similarity"
            ),

        "sentence_min_best_similarity":
            features.get(
                "sentence_min_best_similarity"
            ),


        "reference_concept_count":
            features.get(
                "reference_concept_count"
            ),

        "answer_sentence_count":
            features.get(
                "answer_sentence_count"
            ),


        "duration_sec":
            features.get(
                "duration_sec"
            ),

        "word_count":
            features.get(
                "word_count"
            ),

        "wpm":
            features.get(
                "wpm"
            ),

        "filler_count":
            features.get(
                "filler_count"
            ),

        "pause_count":
            features.get(
                "pause_count"
            ),


        "filler_rate_per_100_words":
            features.get(
                "filler_rate_per_100_words"
            ),

        "pause_rate_per_minute":
            features.get(
                "pause_rate_per_minute"
            ),


        "feature_status":
            "EVALUATION_FEATURES_READY",

        "created_at_utc":
            datetime.now(
                timezone.utc
            ).isoformat(
                timespec="seconds"
            )
    }


    return {
        "success": True,
        "status": "FEATURE_RECORD_READY",
        "record": record,
        "error": None
    }


# ============================================================
# SAVE FEATURE RECORD
# ============================================================

def save_evaluation_features(
    sample_id,
    collection_mode,
    features
):

    build_result = (
        build_feature_record(
            sample_id=
                sample_id,

            collection_mode=
                collection_mode,

            features=
                features
        )
    )


    if not build_result[
        "success"
    ]:

        return build_result


    record = build_result[
        "record"
    ]


    try:

        mode = _normalize_mode(
            collection_mode
        )

        path = get_feature_path(
            mode
        )

    except Exception as error:

        return {
            "success": False,
            "status": "INVALID_COLLECTION_MODE",
            "path": None,
            "sample_id": sample_id,
            "error": str(error)
        }


    try:

        with _FEATURE_FILE_LOCK:

            # ------------------------------------------------
            # Create file with correct schema when absent.
            # ------------------------------------------------

            if not os.path.exists(
                path
            ):

                _create_empty_feature_file(
                    path
                )


            # ------------------------------------------------
            # Read current table.
            # ------------------------------------------------

            try:

                existing = pd.read_csv(
                    path
                )

            except pd.errors.EmptyDataError:

                existing = pd.DataFrame(
                    columns=FEATURE_COLUMNS
                )


            # ------------------------------------------------
            # Protect schema.
            # ------------------------------------------------

            if list(
                existing.columns
            ) != FEATURE_COLUMNS:

                return {
                    "success": False,
                    "status": "FEATURE_SCHEMA_MISMATCH",
                    "path": path,
                    "sample_id": sample_id,
                    "error": (
                        "Existing feature CSV schema "
                        "does not match expected schema."
                    )
                }


            # ------------------------------------------------
            # Idempotency protection.
            #
            # Never silently append a second feature record
            # for the same response sample.
            # ------------------------------------------------

            if len(
                existing
            ) > 0:

                existing_ids = (
                    existing[
                        "sample_id"
                    ]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                )


                if (
                    str(
                        sample_id
                    ).strip()
                    in set(
                        existing_ids
                    )
                ):

                    return {
                        "success": True,
                        "status": "FEATURE_RECORD_ALREADY_EXISTS",
                        "path": path,
                        "sample_id": sample_id,
                        "error": None
                    }


            # ------------------------------------------------
            # Append in memory.
            # ------------------------------------------------

            new_row = pd.DataFrame(
                [record],
                columns=FEATURE_COLUMNS
            )


            combined = pd.concat(
                [
                    existing,
                    new_row
                ],
                ignore_index=True
            )


            # ------------------------------------------------
            # Atomic-style replacement.
            #
            # Write the complete file to a temporary path,
            # then replace the destination.
            # ------------------------------------------------

            temporary_path = (
                path
                + ".tmp"
            )


            combined.to_csv(
                temporary_path,
                index=False
            )


            os.replace(
                temporary_path,
                path
            )


        return {
            "success": True,
            "status": "FEATURE_RECORD_SAVED",
            "path": path,
            "sample_id": sample_id,
            "rows": len(
                combined
            ),
            "error": None
        }


    except Exception as error:

        return {
            "success": False,
            "status": "FEATURE_SAVE_ERROR",
            "path": path,
            "sample_id": sample_id,
            "error": str(error)
        }


# ============================================================
# DEVELOPMENT TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 72)

    print(
        "AEGIE EVALUATION FEATURE STORE TEST"
    )

    print("=" * 72)


    print()

    print(
        "This module is ready to store "
        "research evaluation features."
    )

    print()

    print(
        "No participant feature record "
        "is written by this direct test."
    )

    print()

    print(
        "Development path:",
        DEVELOPMENT_FEATURE_PATH
    )

    print(
        "Pilot path:",
        PILOT_FEATURE_PATH
    )

    print(
        "Final path:",
        FINAL_FEATURE_PATH
    )


    print()

    print(
        "Human labels stored here: NO"
    )

    print(
        "Final AEGIE 1-5 scores stored here: NO"
    )

    print(
        "Unique linking key: sample_id"
    )


    print()

    print("=" * 72)