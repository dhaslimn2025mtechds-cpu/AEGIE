import json
import os
from datetime import datetime, timezone

import pandas as pd


FEATURE_PATH = os.path.join(
    "data",
    "development_evaluation_features.csv"
)

RESULTS_DIR = "results"

OVERALL_OUTPUT = os.path.join(
    RESULTS_DIR,
    "prototype_overall_summary.csv"
)

DIFFICULTY_OUTPUT = os.path.join(
    RESULTS_DIR,
    "prototype_difficulty_summary.csv"
)

QUESTION_OUTPUT = os.path.join(
    RESULTS_DIR,
    "prototype_question_summary.csv"
)

QUALITY_OUTPUT = os.path.join(
    RESULTS_DIR,
    "prototype_data_quality.csv"
)

METADATA_OUTPUT = os.path.join(
    RESULTS_DIR,
    "prototype_experiment_metadata.json"
)

TEXT_REPORT_OUTPUT = os.path.join(
    RESULTS_DIR,
    "prototype_experiment_report.txt"
)


MEASURE_COLUMNS = [
    "whole_mean_similarity",
    "sentence_mean_best_similarity",
    "duration_sec",
    "word_count",
    "wpm",
    "filler_count",
    "pause_count",
    "filler_rate_per_100_words",
    "pause_rate_per_minute",
]


def safe_numeric(df, column):
    if column not in df.columns:
        return pd.Series(dtype=float)

    return pd.to_numeric(
        df[column],
        errors="coerce"
    )


def summarize_series(series, label):
    values = pd.to_numeric(
        series,
        errors="coerce"
    ).dropna()

    if values.empty:
        return {
            "measure": label,
            "count": 0,
            "mean": None,
            "std": None,
            "min": None,
            "max": None,
        }

    return {
        "measure": label,
        "count": int(values.count()),
        "mean": round(float(values.mean()), 4),
        "std": (
            round(float(values.std(ddof=1)), 4)
            if len(values) > 1
            else 0.0
        ),
        "min": round(float(values.min()), 4),
        "max": round(float(values.max()), 4),
    }


def grouped_summary(df, group_column):
    rows = []

    if group_column not in df.columns:
        return pd.DataFrame()

    for group_value, group_df in df.groupby(
        group_column,
        dropna=False
    ):
        row = {
            group_column: group_value,
            "sample_count": int(len(group_df)),
        }

        for column in MEASURE_COLUMNS:
            values = safe_numeric(
                group_df,
                column
            ).dropna()

            row[f"{column}_mean"] = (
                round(float(values.mean()), 4)
                if not values.empty
                else None
            )

        rows.append(row)

    return pd.DataFrame(rows)


def main():

    print("=" * 68)
    print("AEGIE NO-PARTICIPANT PROTOTYPE EXPERIMENTS")
    print("=" * 68)

    if not os.path.isfile(FEATURE_PATH):
        print(
            "ERROR: Feature store not found:",
            FEATURE_PATH
        )
        return

    os.makedirs(
        RESULTS_DIR,
        exist_ok=True
    )

    df = pd.read_csv(
        FEATURE_PATH
    )

    if df.empty:
        print(
            "ERROR: Development feature store is empty."
        )
        return

    required_columns = [
        "sample_id",
        "participant_id",
        "job_role",
        "question_id",
        "difficulty",
        "collection_mode",
        "feature_status",
    ]

    missing_required = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_required:
        print(
            "ERROR: Missing required columns:",
            missing_required
        )
        return

    # --------------------------------------------------------
    # BASIC DATA INTEGRITY
    # --------------------------------------------------------

    df["sample_id"] = (
        df["sample_id"]
        .astype(str)
    )

    duplicate_sample_rows = int(
        df["sample_id"]
        .duplicated(
            keep=False
        )
        .sum()
    )

    unique_samples = int(
        df["sample_id"]
        .nunique()
    )

    unique_question_ids = int(
        df["question_id"]
        .astype(str)
        .nunique()
    )

    unique_roles = int(
        df["job_role"]
        .astype(str)
        .nunique()
    )

    unique_participant_ids = int(
        df["participant_id"]
        .astype(str)
        .nunique()
    )

    feature_status_counts = (
        df["feature_status"]
        .fillna("MISSING")
        .astype(str)
        .value_counts(
            dropna=False
        )
        .to_dict()
    )

    # --------------------------------------------------------
    # OVERALL DESCRIPTIVE SUMMARY
    # --------------------------------------------------------

    overall_rows = []

    for column in MEASURE_COLUMNS:
        if column in df.columns:
            overall_rows.append(
                summarize_series(
                    df[column],
                    column
                )
            )

    overall_df = pd.DataFrame(
        overall_rows
    )

    overall_df.to_csv(
        OVERALL_OUTPUT,
        index=False
    )

    # --------------------------------------------------------
    # DIFFICULTY DESCRIPTIVE SUMMARY
    # --------------------------------------------------------

    difficulty_df = grouped_summary(
        df,
        "difficulty"
    )

    if not difficulty_df.empty:
        difficulty_order = {
            "Easy": 1,
            "Medium": 2,
            "Hard": 3,
        }

        difficulty_df["_order"] = (
            difficulty_df[
                "difficulty"
            ]
            .map(
                difficulty_order
            )
            .fillna(99)
        )

        difficulty_df = (
            difficulty_df
            .sort_values(
                [
                    "_order",
                    "difficulty"
                ]
            )
            .drop(
                columns=[
                    "_order"
                ]
            )
        )

    difficulty_df.to_csv(
        DIFFICULTY_OUTPUT,
        index=False
    )

    # --------------------------------------------------------
    # QUESTION-LEVEL DESCRIPTIVE SUMMARY
    # --------------------------------------------------------

    question_df = grouped_summary(
        df,
        "question_id"
    )

    if not question_df.empty:
        question_df = (
            question_df
            .sort_values(
                "question_id"
            )
            .reset_index(
                drop=True
            )
        )

    question_df.to_csv(
        QUESTION_OUTPUT,
        index=False
    )

    # --------------------------------------------------------
    # DATA QUALITY SUMMARY
    # --------------------------------------------------------

    quality_rows = [
        {
            "check": "total_rows",
            "value": int(len(df)),
            "status": "INFO",
        },
        {
            "check": "unique_sample_ids",
            "value": unique_samples,
            "status": "INFO",
        },
        {
            "check": "duplicate_sample_rows",
            "value": duplicate_sample_rows,
            "status": (
                "PASS"
                if duplicate_sample_rows == 0
                else "REVIEW"
            ),
        },
        {
            "check": "unique_participant_ids",
            "value": unique_participant_ids,
            "status": "INFO",
        },
        {
            "check": "unique_job_roles",
            "value": unique_roles,
            "status": "INFO",
        },
        {
            "check": "unique_question_ids",
            "value": unique_question_ids,
            "status": "INFO",
        },
    ]

    for column in MEASURE_COLUMNS:
        if column not in df.columns:
            continue

        missing_count = int(
            safe_numeric(
                df,
                column
            )
            .isna()
            .sum()
        )

        quality_rows.append({
            "check": f"missing_{column}",
            "value": missing_count,
            "status": (
                "PASS"
                if missing_count == 0
                else "REVIEW"
            ),
        })

    quality_df = pd.DataFrame(
        quality_rows
    )

    quality_df.to_csv(
        QUALITY_OUTPUT,
        index=False
    )

    # --------------------------------------------------------
    # METADATA
    # --------------------------------------------------------

    metadata = {
        "framework": "AEGIE",
        "experiment_type":
            "no-participant prototype descriptive analysis",
        "created_utc":
            datetime.now(
                timezone.utc
            ).isoformat(),
        "source_feature_store":
            FEATURE_PATH,
        "source_rows":
            int(len(df)),
        "unique_sample_ids":
            unique_samples,
        "unique_participant_ids":
            unique_participant_ids,
        "unique_job_roles":
            unique_roles,
        "unique_question_ids":
            unique_question_ids,
        "duplicate_sample_rows":
            duplicate_sample_rows,
        "feature_status_counts":
            feature_status_counts,
        "research_scope": {
            "validated_interview_scores":
                False,
            "human_agreement_claim":
                False,
            "population_accuracy_claim":
                False,
            "participant_study_claim":
                False,
            "purpose":
                "proof-of-concept system verification and descriptive evidence analysis",
        },
        "outputs": [
            OVERALL_OUTPUT,
            DIFFICULTY_OUTPUT,
            QUESTION_OUTPUT,
            QUALITY_OUTPUT,
            TEXT_REPORT_OUTPUT,
        ],
    }

    with open(
        METADATA_OUTPUT,
        "w",
        encoding="utf-8"
    ) as handle:
        json.dump(
            metadata,
            handle,
            indent=2
        )

    # --------------------------------------------------------
    # HUMAN-READABLE REPORT
    # --------------------------------------------------------

    report_lines = []

    report_lines.append(
        "AEGIE NO-PARTICIPANT PROTOTYPE EXPERIMENT REPORT"
    )
    report_lines.append(
        "=" * 60
    )
    report_lines.append(
        ""
    )
    report_lines.append(
        f"Development feature rows: {len(df)}"
    )
    report_lines.append(
        f"Unique sample IDs: {unique_samples}"
    )
    report_lines.append(
        f"Unique participant IDs: {unique_participant_ids}"
    )
    report_lines.append(
        f"Unique job roles: {unique_roles}"
    )
    report_lines.append(
        f"Unique question IDs: {unique_question_ids}"
    )
    report_lines.append(
        f"Duplicate sample rows: {duplicate_sample_rows}"
    )
    report_lines.append(
        ""
    )

    report_lines.append(
        "OVERALL DESCRIPTIVE EVIDENCE"
    )
    report_lines.append(
        "-" * 60
    )

    for _, row in overall_df.iterrows():
        report_lines.append(
            (
                f"{row['measure']}: "
                f"n={int(row['count'])}, "
                f"mean={row['mean']}, "
                f"std={row['std']}, "
                f"min={row['min']}, "
                f"max={row['max']}"
            )
        )

    report_lines.append(
        ""
    )
    report_lines.append(
        "RESEARCH INTERPRETATION"
    )
    report_lines.append(
        "-" * 60
    )
    report_lines.append(
        "These results are descriptive measurements from the "
        "AEGIE DEVELOPMENT proof-of-concept feature store."
    )
    report_lines.append(
        "MiniLM similarity values are semantic evidence and "
        "must not be interpreted as validated 1-5 interview scores."
    )
    report_lines.append(
        "No population-level accuracy, human-agreement, or "
        "participant-study conclusion is made from these data."
    )

    with open(
        TEXT_REPORT_OUTPUT,
        "w",
        encoding="utf-8"
    ) as handle:
        handle.write(
            "\n".join(
                report_lines
            )
        )

    # --------------------------------------------------------
    # TERMINAL SUMMARY
    # --------------------------------------------------------

    print()
    print(
        "Development rows:",
        len(df)
    )

    print(
        "Unique samples:",
        unique_samples
    )

    print(
        "Duplicate sample rows:",
        duplicate_sample_rows
    )

    print()
    print(
        "Outputs created:"
    )

    for output_path in [
        OVERALL_OUTPUT,
        DIFFICULTY_OUTPUT,
        QUESTION_OUTPUT,
        QUALITY_OUTPUT,
        METADATA_OUTPUT,
        TEXT_REPORT_OUTPUT,
    ]:
        print(
            " -",
            output_path
        )

    print()
    print(
        "IMPORTANT:"
    )
    print(
        "These outputs are descriptive proof-of-concept evidence only."
    )
    print(
        "They do not represent validated interview-scoring accuracy."
    )
    print("=" * 68)


if __name__ == "__main__":
    main()
