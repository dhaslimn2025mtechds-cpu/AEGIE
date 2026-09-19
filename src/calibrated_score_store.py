"""
AEGIE calibrated score dataset updater.

Purpose:
- Update the already-saved primary response row after the
  calibrated scoring model produces valid AEGIE scores.
- Never create a duplicate response row.
- Never overwrite human annotation columns.
- Never write fabricated adaptive difficulty values.

Research integrity rules:
- Exactly one matching sample_id must exist.
- All five calibrated scores must be numeric and within 1-5.
- Existing non-empty AEGIE score values are protected from
  conflicting overwrite.
- The CSV replacement is atomic within the same filesystem.
"""

from __future__ import annotations

import math
import os
import tempfile
import threading
from typing import Any

import pandas as pd


_SCORE_UPDATE_LOCK = threading.Lock()


SCORE_COLUMN_MAP = {
    "relevance_score":
        "aegie_relevance_score",

    "technical_score":
        "aegie_technical_score",

    "clarity_score":
        "aegie_clarity_score",

    "communication_score":
        "aegie_communication_score",

    "overall_score":
        "aegie_overall_score",
}


def _is_blank(
    value: Any,
) -> bool:

    if value is None:
        return True

    try:

        if pd.isna(
            value
        ):
            return True

    except Exception:
        pass

    return not str(
        value
    ).strip()


def _validate_scores(
    scores: dict,
) -> dict:

    if not isinstance(
        scores,
        dict,
    ):

        raise ValueError(
            "Calibrated scores must be a dictionary."
        )


    validated = {}


    for score_key in SCORE_COLUMN_MAP:

        if score_key not in scores:

            raise ValueError(
                "Missing calibrated score: "
                f"{score_key}"
            )


        raw_value = scores.get(
            score_key
        )


        try:

            numeric_value = float(
                raw_value
            )

        except (
            TypeError,
            ValueError,
        ) as exc:

            raise ValueError(
                "Non-numeric calibrated score: "
                f"{score_key}"
            ) from exc


        if not math.isfinite(
            numeric_value
        ):

            raise ValueError(
                "Non-finite calibrated score: "
                f"{score_key}"
            )


        if not (
            1.0
            <= numeric_value
            <= 5.0
        ):

            raise ValueError(
                "Calibrated score outside 1-5 range: "
                f"{score_key}={numeric_value}"
            )


        validated[
            score_key
        ] = numeric_value


    return validated


def update_primary_row_with_calibrated_scores(
    dataset_path: str,
    sample_id: str,
    scores: dict,
) -> dict:
    """
    Update the five AEGIE prediction columns for exactly one
    already-existing primary response row.

    This function does NOT:
    - append a new row
    - modify human labels
    - modify transcript/audio/features
    - write aegie_next_difficulty
    """

    if not dataset_path:

        return {
            "success": False,
            "status": "DATASET_PATH_MISSING",
            "error": "Dataset path is missing.",
        }


    if not sample_id:

        return {
            "success": False,
            "status": "SAMPLE_ID_MISSING",
            "error": "Sample ID is missing.",
        }


    if not os.path.isfile(
        dataset_path
    ):

        return {
            "success": False,
            "status": "DATASET_NOT_FOUND",
            "error": (
                "Primary dataset does not exist: "
                f"{dataset_path}"
            ),
        }


    try:

        validated_scores = (
            _validate_scores(
                scores
            )
        )

    except Exception as error:

        return {
            "success": False,
            "status": "INVALID_CALIBRATED_SCORES",
            "error": str(
                error
            ),
        }


    with _SCORE_UPDATE_LOCK:

        try:

            df = pd.read_csv(
                dataset_path
            )

        except Exception as error:

            return {
                "success": False,
                "status": "DATASET_READ_ERROR",
                "error": str(
                    error
                ),
            }


        if "sample_id" not in df.columns:

            return {
                "success": False,
                "status": "SAMPLE_ID_COLUMN_MISSING",
                "error": (
                    "Primary dataset has no sample_id column."
                ),
            }


        missing_columns = [
            column
            for column in SCORE_COLUMN_MAP.values()
            if column not in df.columns
        ]


        if missing_columns:

            return {
                "success": False,
                "status": "AEGIE_SCORE_COLUMNS_MISSING",
                "error": (
                    "Missing dataset columns: "
                    + ", ".join(
                        missing_columns
                    )
                ),
            }


        sample_mask = (
            df[
                "sample_id"
            ].astype(
                str
            )
            ==
            str(
                sample_id
            )
        )


        match_count = int(
            sample_mask.sum()
        )


        if match_count == 0:

            return {
                "success": False,
                "status": "SAMPLE_NOT_FOUND",
                "error": (
                    "No primary response row found for "
                    f"sample_id={sample_id}"
                ),
            }


        if match_count > 1:

            return {
                "success": False,
                "status": "DUPLICATE_SAMPLE_ID",
                "error": (
                    "More than one primary row exists for "
                    f"sample_id={sample_id}. Update blocked."
                ),
            }


        row_index = df.index[
            sample_mask
        ][0]


        # ----------------------------------------------------
        # Protect against conflicting overwrite
        # ----------------------------------------------------

        for score_key, column_name in (
            SCORE_COLUMN_MAP.items()
        ):

            existing_value = df.at[
                row_index,
                column_name
            ]


            new_value = validated_scores[
                score_key
            ]


            if not _is_blank(
                existing_value
            ):

                try:

                    existing_numeric = float(
                        existing_value
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    return {
                        "success": False,
                        "status": "EXISTING_SCORE_INVALID",
                        "error": (
                            "Existing AEGIE score is not numeric: "
                            f"{column_name}={existing_value}"
                        ),
                    }


                if not math.isclose(
                    existing_numeric,
                    new_value,
                    rel_tol=1e-9,
                    abs_tol=1e-9,
                ):

                    return {
                        "success": False,
                        "status": "SCORE_OVERWRITE_CONFLICT",
                        "error": (
                            "Existing calibrated score differs "
                            "from the new prediction for "
                            f"{column_name}. Update blocked."
                        ),
                    }


        # ----------------------------------------------------
        # Apply five calibrated scores
        # ----------------------------------------------------

        for score_key, column_name in (
            SCORE_COLUMN_MAP.items()
        ):

            df.at[
                row_index,
                column_name
            ] = validated_scores[
                score_key
            ]


        # ----------------------------------------------------
        # Atomic CSV replacement
        # ----------------------------------------------------

        dataset_directory = (
            os.path.dirname(
                os.path.abspath(
                    dataset_path
                )
            )
        )


        temp_path = None


        try:

            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="",
                suffix=".csv",
                prefix="aegie_scores_",
                dir=dataset_directory,
                delete=False,
            ) as temp_file:

                temp_path = (
                    temp_file.name
                )


            df.to_csv(
                temp_path,
                index=False
            )


            os.replace(
                temp_path,
                dataset_path
            )


        except Exception as error:

            if (
                temp_path
                and os.path.exists(
                    temp_path
                )
            ):

                try:

                    os.remove(
                        temp_path
                    )

                except Exception:
                    pass


            return {
                "success": False,
                "status": "SCORE_UPDATE_WRITE_ERROR",
                "error": str(
                    error
                ),
            }


        return {
            "success": True,
            "status": "CALIBRATED_SCORES_SAVED",
            "sample_id": str(
                sample_id
            ),
            "updated_columns": list(
                SCORE_COLUMN_MAP.values()
            ),
            "dataset_path": dataset_path,
        }


def main() -> int:

    print(
        "=" * 72
    )

    print(
        "AEGIE CALIBRATED SCORE DATASET UPDATER"
    )

    print(
        "=" * 72
    )

    print()

    print(
        "This module updates an existing primary response row."
    )

    print(
        "It does not append rows and does not modify human labels."
    )

    print(
        "Run it through app.py after calibrated scores are available."
    )

    return 0


if __name__ == "__main__":

    raise SystemExit(
        main()
    )
