"""
AEGIE calibrated scoring runtime.

Purpose:
- Load the frozen calibrated scoring bundle created by
  src/train_calibrated_scoring.py.
- Convert an already-created AEGIE evaluation feature dictionary
  into five calibrated continuous scores on the 1-5 scale.
- Fail safely when the trained model does not yet exist.

Research safeguards:
- No human labels are used at runtime.
- participant_id is never used as a predictive feature.
- Feature order comes from the trained model bundle.
- Predictions are clipped to the approved 1-5 score range.
- If the calibrated model is unavailable, no score is fabricated.
- DEVELOPMENT can exercise a trained model before final deployment.
- FINAL research use is blocked until the frozen TEST evaluation
  artifacts exist and are verified for the exact same model bundle.
- No arbitrary TEST-performance pass/fail threshold is invented here.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import threading
from typing import Any

import joblib
import numpy as np


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

MODEL_PATH = os.path.join(
    PROJECT_ROOT,
    "models",
    "calibrated_scoring",
    "aegie_calibrated_scoring.joblib",
)

FROZEN_TEST_PREDICTIONS_PATH = os.path.join(
    PROJECT_ROOT,
    "results",
    "aegie_frozen_test_predictions.csv",
)

FROZEN_TEST_METRICS_PATH = os.path.join(
    PROJECT_ROOT,
    "results",
    "aegie_frozen_test_metrics.csv",
)

FROZEN_TEST_ROLE_METRICS_PATH = os.path.join(
    PROJECT_ROOT,
    "results",
    "aegie_frozen_test_role_metrics.csv",
)

FROZEN_TEST_METADATA_PATH = os.path.join(
    PROJECT_ROOT,
    "results",
    "aegie_frozen_test_metadata.json",
)

EXPECTED_FROZEN_TEST_ROWS = 120
EXPECTED_FROZEN_TEST_PARTICIPANTS = 12


# ============================================================
# CACHE / LOCK
# ============================================================

_MODEL_BUNDLE = None
_MODEL_BUNDLE_PATH = None
_MODEL_LOCK = threading.Lock()


# ============================================================
# EXPECTED SCORE DIMENSIONS
# ============================================================

EXPECTED_DIMENSIONS = [
    "relevance",
    "technical",
    "clarity",
    "communication",
    "overall",
]


# ============================================================
# HELPERS
# ============================================================

def calibrated_model_exists() -> bool:
    """
    Return True only when the frozen calibrated model bundle exists.
    """

    return os.path.isfile(
        MODEL_PATH
    )


def _sha256_file(
    path: str,
) -> str:
    """
    Return the SHA-256 fingerprint of a local research artifact.
    """

    digest = hashlib.sha256()

    with open(
        path,
        "rb",
    ) as file_handle:

        while True:

            block = file_handle.read(
                1024 * 1024
            )

            if not block:
                break

            digest.update(
                block
            )

    return digest.hexdigest()


def _current_collection_mode() -> str:
    """
    Read the active AEGIE collection mode.

    DEVELOPMENT is the safe default, matching app.py.
    """

    return os.getenv(
        "AEGIE_COLLECTION_MODE",
        "DEVELOPMENT",
    ).strip().upper()


def check_final_research_use_gate() -> dict:
    """
    Verify whether the trained scoring bundle may be used in FINAL mode.

    DEVELOPMENT and PILOT are not blocked by this deployment gate.

    FINAL mode requires a completed frozen TEST evaluation for the
    exact same calibrated model artifact. This function verifies
    provenance/integrity only. It deliberately does not invent a
    performance cutoff.
    """

    collection_mode = (
        _current_collection_mode()
    )

    if collection_mode != "FINAL":

        return {
            "success": True,
            "status": "NON_FINAL_MODE",
            "collection_mode": collection_mode,
            "reason": (
                "Frozen TEST deployment gate is required only "
                "for FINAL research use."
            ),
        }


    if not calibrated_model_exists():

        return {
            "success": False,
            "status": "CALIBRATION_MODEL_NOT_AVAILABLE",
            "collection_mode": collection_mode,
            "reason": (
                "The calibrated AEGIE scoring model has not been "
                "trained yet."
            ),
        }


    required_artifacts = [
        FROZEN_TEST_PREDICTIONS_PATH,
        FROZEN_TEST_METRICS_PATH,
        FROZEN_TEST_ROLE_METRICS_PATH,
        FROZEN_TEST_METADATA_PATH,
    ]

    missing_artifacts = [
        path
        for path in required_artifacts
        if not os.path.isfile(
            path
        )
    ]

    if missing_artifacts:

        return {
            "success": False,
            "status": "FINAL_RESEARCH_USE_BLOCKED",
            "collection_mode": collection_mode,
            "reason": (
                "Frozen TEST evaluation is not complete for "
                "FINAL research use."
            ),
            "missing_artifacts": missing_artifacts,
        }


    try:

        with open(
            FROZEN_TEST_METADATA_PATH,
            "r",
            encoding="utf-8",
        ) as metadata_file:

            metadata = json.load(
                metadata_file
            )

    except Exception as error:

        return {
            "success": False,
            "status": "FINAL_RESEARCH_USE_BLOCKED",
            "collection_mode": collection_mode,
            "reason": (
                "Frozen TEST metadata could not be read: "
                + str(
                    error
                )
            ),
        }


    if not isinstance(
        metadata,
        dict,
    ):

        return {
            "success": False,
            "status": "FINAL_RESEARCH_USE_BLOCKED",
            "collection_mode": collection_mode,
            "reason": (
                "Frozen TEST metadata is not a valid dictionary."
            ),
        }


    if metadata.get(
        "framework"
    ) != "AEGIE":

        return {
            "success": False,
            "status": "FINAL_RESEARCH_USE_BLOCKED",
            "collection_mode": collection_mode,
            "reason": (
                "Frozen TEST metadata framework is not AEGIE."
            ),
        }


    if metadata.get(
        "artifact_type"
    ) != "frozen_test_evaluation":

        return {
            "success": False,
            "status": "FINAL_RESEARCH_USE_BLOCKED",
            "collection_mode": collection_mode,
            "reason": (
                "Frozen TEST metadata has an unexpected artifact type."
            ),
        }


    research_policy = metadata.get(
        "research_policy",
        {},
    )

    required_false_policy_flags = [
        "test_used_for_training",
        "test_used_for_alpha_selection",
        "test_used_for_model_selection",
        "model_refit_during_test_evaluation",
    ]

    for flag_name in required_false_policy_flags:

        if research_policy.get(
            flag_name
        ) is not False:

            return {
                "success": False,
                "status": "FINAL_RESEARCH_USE_BLOCKED",
                "collection_mode": collection_mode,
                "reason": (
                    "Frozen TEST research policy is invalid for "
                    f"'{flag_name}'."
                ),
            }


    test_counts = metadata.get(
        "test_counts",
        {},
    )

    try:

        test_rows = int(
            test_counts.get(
                "rows",
                -1,
            )
        )

        test_participants = int(
            test_counts.get(
                "participants",
                -1,
            )
        )

    except (
        TypeError,
        ValueError,
    ):

        return {
            "success": False,
            "status": "FINAL_RESEARCH_USE_BLOCKED",
            "collection_mode": collection_mode,
            "reason": (
                "Frozen TEST count metadata is invalid."
            ),
        }


    if (
        test_rows
        != EXPECTED_FROZEN_TEST_ROWS
        or test_participants
        != EXPECTED_FROZEN_TEST_PARTICIPANTS
    ):

        return {
            "success": False,
            "status": "FINAL_RESEARCH_USE_BLOCKED",
            "collection_mode": collection_mode,
            "reason": (
                "Frozen TEST count metadata does not match the "
                "approved 120-response / 12-participant design."
            ),
        }


    metadata_model = metadata.get(
        "model",
        {},
    )

    expected_model_sha256 = metadata_model.get(
        "sha256"
    )

    if not isinstance(
        expected_model_sha256,
        str,
    ) or not expected_model_sha256.strip():

        return {
            "success": False,
            "status": "FINAL_RESEARCH_USE_BLOCKED",
            "collection_mode": collection_mode,
            "reason": (
                "Frozen TEST metadata does not contain a valid "
                "model SHA-256 fingerprint."
            ),
        }


    try:

        current_model_sha256 = _sha256_file(
            MODEL_PATH
        )

    except Exception as error:

        return {
            "success": False,
            "status": "FINAL_RESEARCH_USE_BLOCKED",
            "collection_mode": collection_mode,
            "reason": (
                "Current calibrated model could not be fingerprinted: "
                + str(
                    error
                )
            ),
        }


    if (
        current_model_sha256
        != expected_model_sha256
    ):

        return {
            "success": False,
            "status": "FINAL_RESEARCH_USE_BLOCKED",
            "collection_mode": collection_mode,
            "reason": (
                "The current calibrated model does not match the "
                "model evaluated by the frozen TEST run."
            ),
            "current_model_sha256": current_model_sha256,
            "evaluated_model_sha256": expected_model_sha256,
        }


    return {
        "success": True,
        "status": "FROZEN_TEST_EVALUATION_CONFIRMED",
        "collection_mode": collection_mode,
        "reason": (
            "Frozen TEST provenance is verified for the exact "
            "current calibrated model. No performance threshold "
            "was invented by the runtime gate."
        ),
        "model_sha256": current_model_sha256,
    }


def _validate_bundle(
    bundle: Any,
) -> None:
    """
    Validate the minimum runtime structure of the saved bundle.
    """

    if not isinstance(
        bundle,
        dict,
    ):
        raise ValueError(
            "Calibrated scoring artifact is not a dictionary bundle."
        )

    feature_columns = bundle.get(
        "feature_columns"
    )

    models = bundle.get(
        "models"
    )

    if not isinstance(
        feature_columns,
        list,
    ) or not feature_columns:
        raise ValueError(
            "Calibrated scoring bundle has no valid feature_columns."
        )

    if not isinstance(
        models,
        dict,
    ):
        raise ValueError(
            "Calibrated scoring bundle has no valid models dictionary."
        )

    missing_dimensions = [
        dimension
        for dimension in EXPECTED_DIMENSIONS
        if dimension not in models
    ]

    if missing_dimensions:
        raise ValueError(
            "Calibrated scoring bundle is missing score models: "
            + ", ".join(
                missing_dimensions
            )
        )

    score_min = bundle.get(
        "score_min"
    )

    score_max = bundle.get(
        "score_max"
    )

    try:
        score_min = float(
            score_min
        )
        score_max = float(
            score_max
        )
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise ValueError(
            "Calibrated scoring bundle has invalid score limits."
        ) from exc

    if (
        not math.isfinite(
            score_min
        )
        or not math.isfinite(
            score_max
        )
        or score_min >= score_max
    ):
        raise ValueError(
            "Calibrated scoring bundle score range is invalid."
        )


def get_calibrated_model_bundle() -> dict:
    """
    Lazy-load and cache the calibrated scoring bundle.

    The function intentionally raises FileNotFoundError when calibration
    has not yet produced a trained model. The public scoring function
    catches that condition and returns a safe waiting status.
    """

    global _MODEL_BUNDLE
    global _MODEL_BUNDLE_PATH

    if _MODEL_BUNDLE is not None:
        return _MODEL_BUNDLE

    with _MODEL_LOCK:

        if _MODEL_BUNDLE is not None:
            return _MODEL_BUNDLE

        if not os.path.isfile(
            MODEL_PATH
        ):
            raise FileNotFoundError(
                "Calibrated AEGIE scoring model does not exist yet."
            )

        bundle = joblib.load(
            MODEL_PATH
        )

        _validate_bundle(
            bundle
        )

        _MODEL_BUNDLE = bundle
        _MODEL_BUNDLE_PATH = MODEL_PATH

        return _MODEL_BUNDLE


def _build_feature_row(
    features: dict,
    feature_columns: list[str],
) -> np.ndarray:
    """
    Build one model input row in the exact frozen feature order.
    """

    if not isinstance(
        features,
        dict,
    ):
        raise ValueError(
            "Evaluation features must be provided as a dictionary."
        )

    values = []

    for feature_name in feature_columns:

        if feature_name not in features:
            raise ValueError(
                "Missing required calibrated scoring feature: "
                f"{feature_name}"
            )

        raw_value = features.get(
            feature_name
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
                "Non-numeric calibrated scoring feature: "
                f"{feature_name}"
            ) from exc

        if not math.isfinite(
            numeric_value
        ):
            raise ValueError(
                "Invalid non-finite calibrated scoring feature: "
                f"{feature_name}"
            )

        values.append(
            numeric_value
        )

    return np.asarray(
        [
            values
        ],
        dtype=float,
    )


def _clip_score(
    value: float,
    score_min: float,
    score_max: float,
) -> float:
    """
    Clip a continuous prediction to the approved research score range.
    """

    clipped = np.clip(
        float(
            value
        ),
        float(
            score_min
        ),
        float(
            score_max
        ),
    )

    return float(
        clipped
    )


# ============================================================
# PUBLIC RUNTIME SCORING
# ============================================================

def generate_calibrated_scores(
    features: dict,
) -> dict:
    """
    Generate calibrated AEGIE scores when a trained model exists.

    Returns a structured result instead of raising for the expected
    pre-calibration state.

    Successful output example:
    {
        "success": True,
        "status": "CALIBRATED_SCORES_READY",
        "scores": {
            "relevance_score": 3.42,
            "technical_score": 3.17,
            "clarity_score": 3.88,
            "communication_score": 3.64,
            "overall_score": 3.51,
        },
        "model_family": "StandardScaler + Ridge Regression"
    }
    """

    if not calibrated_model_exists():
        return {
            "success": False,
            "status": "CALIBRATION_MODEL_NOT_AVAILABLE",
            "reason": (
                "The calibrated AEGIE scoring model has not been "
                "trained yet."
            ),
            "scores": None,
        }


    final_use_gate = (
        check_final_research_use_gate()
    )


    if not final_use_gate.get(
        "success",
        False,
    ):

        return {
            "success": False,
            "status": final_use_gate.get(
                "status",
                "FINAL_RESEARCH_USE_BLOCKED",
            ),
            "reason": final_use_gate.get(
                "reason",
                "FINAL research-use gate was not satisfied.",
            ),
            "scores": None,
            "collection_mode": final_use_gate.get(
                "collection_mode"
            ),
        }


    try:
        bundle = get_calibrated_model_bundle()

        feature_columns = bundle[
            "feature_columns"
        ]

        models = bundle[
            "models"
        ]

        score_min = float(
            bundle[
                "score_min"
            ]
        )

        score_max = float(
            bundle[
                "score_max"
            ]
        )

        feature_row = _build_feature_row(
            features,
            feature_columns,
        )

        scores = {}

        for dimension in EXPECTED_DIMENSIONS:

            model = models[
                dimension
            ]

            prediction = model.predict(
                feature_row
            )

            if prediction is None:
                raise ValueError(
                    f"{dimension} model returned no prediction."
                )

            prediction_array = np.asarray(
                prediction,
                dtype=float,
            ).reshape(
                -1
            )

            if prediction_array.size != 1:
                raise ValueError(
                    f"{dimension} model returned an unexpected "
                    "prediction shape."
                )

            value = float(
                prediction_array[
                    0
                ]
            )

            if not math.isfinite(
                value
            ):
                raise ValueError(
                    f"{dimension} model returned a non-finite score."
                )

            scores[
                f"{dimension}_score"
            ] = _clip_score(
                value,
                score_min,
                score_max,
            )

        return {
            "success": True,
            "status": "CALIBRATED_SCORES_READY",
            "scores": scores,
            "model_family": bundle.get(
                "model_family"
            ),
            "created_utc": bundle.get(
                "created_utc"
            ),
            "selected_alphas": bundle.get(
                "selected_alphas"
            ),
            "collection_mode": final_use_gate.get(
                "collection_mode"
            ),
            "final_research_use_gate": final_use_gate.get(
                "status"
            ),
        }

    except Exception as error:
        return {
            "success": False,
            "status": "CALIBRATED_SCORING_ERROR",
            "reason": str(
                error
            ),
            "scores": None,
        }


# ============================================================
# DEVELOPMENT / DIAGNOSTIC CHECK
# ============================================================

def main() -> int:

    print(
        "=" * 72
    )

    print(
        "AEGIE CALIBRATED SCORING RUNTIME CHECK"
    )

    print(
        "=" * 72
    )

    print()

    print(
        "Collection mode:",
        _current_collection_mode(),
    )

    print(
        "Model path:",
        MODEL_PATH,
    )

    print(
        "Model exists:",
        calibrated_model_exists(),
    )

    if not calibrated_model_exists():

        print()

        print(
            "CALIBRATED SCORING STATUS: "
            "WAITING FOR TRAINED PILOT MODEL"
        )

        print(
            "No runtime AEGIE 1-5 score will be fabricated."
        )

        return 0

    try:
        bundle = get_calibrated_model_bundle()

    except Exception as error:

        print()

        print(
            "CALIBRATED SCORING STATUS: ERROR"
        )

        print(
            "Reason:",
            str(
                error
            ),
        )

        return 1

    print()

    print(
        "Model family:",
        bundle.get(
            "model_family"
        ),
    )

    print(
        "Feature count:",
        len(
            bundle.get(
                "feature_columns",
                [],
            )
        ),
    )

    print(
        "Score dimensions:",
        ", ".join(
            EXPECTED_DIMENSIONS
        ),
    )

    final_use_gate = (
        check_final_research_use_gate()
    )

    print()

    print(
        "FINAL Research-Use Gate:",
        final_use_gate.get(
            "status"
        ),
    )

    print(
        "Gate Reason:",
        final_use_gate.get(
            "reason"
        ),
    )


    if (
        _current_collection_mode()
        == "FINAL"
        and not final_use_gate.get(
            "success",
            False,
        )
    ):

        print()

        print(
            "CALIBRATED SCORING STATUS: "
            "MODEL TRAINED - FINAL USE BLOCKED"
        )

        return 0


    print()

    print(
        "CALIBRATED SCORING STATUS: MODEL READY"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
