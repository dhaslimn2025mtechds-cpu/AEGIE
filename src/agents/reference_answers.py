# ============================================================
# AEGIE REFERENCE ANSWER / KEY-CONCEPT KNOWLEDGE BASE
# ============================================================
#
# Purpose:
# Provides expected technical concepts for evaluating answers.
#
# IMPORTANT:
# - These are NOT participant responses.
# - These are NOT primary dataset samples.
# - They must never be counted toward the 3,000 samples.
# - They should be expert-reviewed before the final experiment.
# ============================================================


REFERENCE_ANSWERS = {

    # ========================================================
    # EASY
    # ========================================================

    "DS_E01": {

        "question":
            "What is the difference between supervised "
            "and unsupervised learning?",

        "key_concepts": [
            "Supervised learning uses labeled data.",
            "Supervised learning learns from input-output pairs.",
            "Unsupervised learning uses unlabeled data.",
            "Unsupervised learning discovers patterns or structure."
        ],

        "acceptable_examples": [
            "Classification",
            "Regression",
            "Clustering"
        ]
    },


    "DS_E02": {

        "question":
            "What is overfitting in machine learning?",

        "key_concepts": [
            "The model learns the training data too closely.",
            "The model may also learn noise or irrelevant patterns.",
            "Training performance can be high.",
            "Performance on unseen data is poor."
        ],

        "acceptable_examples": [
            "High training accuracy but low test accuracy."
        ]
    },


    "DS_E03": {

        "question":
            "What is the difference between a population "
            "and a sample?",

        "key_concepts": [
            "Population is the complete group of interest.",
            "A sample is a subset of the population.",
            "Samples are used to make inferences about a population."
        ],

        "acceptable_examples": [
            "All customers versus a selected group of customers."
        ]
    },


    "DS_E04": {

        "question":
            "Why do we split a dataset into training "
            "and testing data?",

        "key_concepts": [
            "Training data is used to fit the model.",
            "Testing data is kept separate from training.",
            "Testing estimates performance on unseen data.",
            "The split helps evaluate generalization."
        ],

        "acceptable_examples": [
            "Train the model on one portion and evaluate "
            "it on a separate portion."
        ]
    },


    # ========================================================
    # MEDIUM
    # ========================================================

    "DS_M01": {

        "question":
            "Explain the bias-variance tradeoff in "
            "machine learning.",

        "key_concepts": [
            "High bias is associated with underfitting.",
            "High variance is associated with overfitting.",
            "Reducing one can increase the other.",
            "The objective is good generalization to unseen data."
        ],

        "acceptable_examples": [
            "A very simple model may underfit while a very "
            "complex model may overfit."
        ]
    },


    "DS_M02": {

        "question":
            "What is cross-validation and why is it useful?",

        "key_concepts": [
            "Data is divided into multiple folds.",
            "The model is trained and validated multiple times.",
            "Different folds are used for validation.",
            "It provides a more robust estimate of model performance."
        ],

        "acceptable_examples": [
            "K-fold cross-validation."
        ]
    },


    "DS_M03": {

        "question":
            "What is the difference between L1 and "
            "L2 regularization?",

        "key_concepts": [
            "L1 regularization uses the absolute magnitude "
            "of coefficients.",
            "L2 regularization uses squared coefficient values.",
            "L1 can drive some coefficients to zero.",
            "L2 generally shrinks coefficients without forcing "
            "many exactly to zero."
        ],

        "acceptable_examples": [
            "Lasso uses L1 regularization.",
            "Ridge uses L2 regularization."
        ]
    },


    "DS_M04": {

        "question":
            "How would you handle an imbalanced "
            "classification dataset?",

        "key_concepts": [
            "Accuracy alone can be misleading.",
            "Use suitable evaluation metrics.",
            "Resampling or class weighting can be considered.",
            "The choice depends on the problem and error costs."
        ],

        "acceptable_examples": [
            "Precision",
            "Recall",
            "F1 score",
            "PR-AUC",
            "Class weights",
            "Oversampling",
            "Undersampling"
        ]
    },


    # ========================================================
    # HARD
    # ========================================================

    "DS_H01": {

        "question":
            "How would you detect and prevent data leakage "
            "in a machine learning project?",

        "key_concepts": [
            "Information unavailable at prediction time must not "
            "leak into model training.",
            "Train and test data must be separated correctly.",
            "Preprocessing should be fitted using training data.",
            "Feature construction should respect time or prediction "
            "boundaries when relevant."
        ],

        "acceptable_examples": [
            "Fit a scaler only on the training data.",
            "Use time-based splitting for temporal prediction.",
            "Remove features containing future information."
        ]
    },


    "DS_H02": {

        "question":
            "How would you select an appropriate evaluation "
            "metric for an imbalanced classification problem?",

        "key_concepts": [
            "Metric selection depends on the application objective.",
            "False-positive and false-negative costs should "
            "be considered.",
            "Accuracy may be misleading with class imbalance.",
            "Precision and recall measure different error tradeoffs."
        ],

        "acceptable_examples": [
            "Recall when missing positive cases is costly.",
            "Precision when false alarms are costly.",
            "F1 when balancing precision and recall is useful.",
            "PR-AUC for imbalanced positive-class evaluation."
        ]
    },


    "DS_H03": {

        "question":
            "How would you determine whether adding a new "
            "feature genuinely improves a predictive model?",

        "key_concepts": [
            "Compare models with and without the new feature.",
            "Use the same evaluation protocol for both models.",
            "Evaluate using unseen or validation data.",
            "Use an appropriate performance metric.",
            "Check whether the improvement is stable across "
            "repeated evaluations or folds."
        ],

        "acceptable_examples": [
            "Cross-validation",
            "Ablation comparison",
            "Confidence intervals",
            "Statistical comparison where appropriate"
        ]
    },


    "DS_H04": {

        "question":
            "How would you investigate a machine learning "
            "model that performs well during training but "
            "poorly on new data?",

        "key_concepts": [
            "Investigate possible overfitting.",
            "Check for train-test distribution differences.",
            "Check for data leakage or incorrect evaluation.",
            "Review model complexity and regularization.",
            "Validate preprocessing and feature pipelines."
        ],

        "acceptable_examples": [
            "Cross-validation",
            "Learning curves",
            "Regularization",
            "Simpler model",
            "More representative training data"
        ]
    }
}


# ============================================================
# GET REFERENCE ANSWER
# ============================================================

def get_reference_answer(question_id):

    return REFERENCE_ANSWERS.get(
        question_id
    )


# ============================================================
# VALIDATE KNOWLEDGE BASE
# ============================================================

def validate_reference_answers():

    expected_ids = {

        "DS_E01",
        "DS_E02",
        "DS_E03",
        "DS_E04",

        "DS_M01",
        "DS_M02",
        "DS_M03",
        "DS_M04",

        "DS_H01",
        "DS_H02",
        "DS_H03",
        "DS_H04"
    }


    actual_ids = set(
        REFERENCE_ANSWERS.keys()
    )


    if actual_ids != expected_ids:

        missing = (
            expected_ids - actual_ids
        )

        extra = (
            actual_ids - expected_ids
        )

        return (
            False,
            f"Missing={missing}, Extra={extra}"
        )


    for question_id, data in (
        REFERENCE_ANSWERS.items()
    ):

        if not data.get("question"):

            return (
                False,
                f"{question_id}: question missing."
            )


        if not data.get("key_concepts"):

            return (
                False,
                f"{question_id}: key concepts missing."
            )


        if not isinstance(
            data["key_concepts"],
            list
        ):

            return (
                False,
                f"{question_id}: key_concepts must be a list."
            )


        if not isinstance(
            data.get(
                "acceptable_examples",
                []
            ),
            list
        ):

            return (
                False,
                f"{question_id}: acceptable_examples "
                f"must be a list."
            )


    return (
        True,
        "All 12 Data Scientist references are valid."
    )


# ============================================================
# DEVELOPMENT TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 65)
    print("AEGIE REFERENCE ANSWER TEST")
    print("=" * 65)


    valid, message = (
        validate_reference_answers()
    )


    print()
    print(
        "Knowledge Base Valid:",
        valid
    )

    print(
        "Status:",
        message
    )


    print()
    print("-" * 65)
    print("EXAMPLE REFERENCE")
    print("-" * 65)


    example = get_reference_answer(
        "DS_E02"
    )


    print(
        "Question:",
        example["question"]
    )


    print()
    print("Key Concepts:")


    for concept in example[
        "key_concepts"
    ]:

        print(
            "-",
            concept
        )


    print()
    print("Acceptable Examples:")


    for example_text in example[
        "acceptable_examples"
    ]:

        print(
            "-",
            example_text
        )


    print()
    print("=" * 65)
    print("REFERENCE ANSWER TEST COMPLETE")
    print("=" * 65)