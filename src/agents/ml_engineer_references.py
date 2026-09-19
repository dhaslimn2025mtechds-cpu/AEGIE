# ============================================================
# AEGIE MACHINE LEARNING ENGINEER REFERENCE KNOWLEDGE
# ============================================================
#
# Reference concepts for the 12 Machine Learning Engineer
# interview questions.
#
# IMPORTANT:
# - These are NOT participant answers.
# - These are NOT primary dataset samples.
# - They are semantic reference concepts for AEGIE.
# - Expert review is required before the final study.
# ============================================================


MACHINE_LEARNING_ENGINEER_REFERENCES = {

    # ========================================================
    # EASY
    # ========================================================

    "MLE_E01": {
        "question": (
            "What is the difference between training data and testing data?"
        ),
        "key_concepts": [
            "Training data is used to fit or learn the parameters of a machine learning model.",
            "Testing data is kept separate from model training and is used to evaluate the trained model.",
            "The test set helps estimate how well the model generalizes to unseen data.",
            "Information from the test set should not leak into the training process."
        ],
        "acceptable_examples": [
            "A dataset can be divided so one portion is used for training and another independent portion is used for final testing.",
            "A model learns patterns from training examples and is later evaluated on unseen test examples."
        ]
    },


    "MLE_E02": {
        "question": (
            "What is feature scaling and why is it used?"
        ),
        "key_concepts": [
            "Feature scaling transforms numerical features so that their magnitudes are on comparable scales.",
            "Scaling can prevent large-magnitude features from dominating algorithms that depend on distances or gradients.",
            "Common approaches include standardization and normalization.",
            "Scaling is especially important for models such as k-nearest neighbors, support vector machines, and many gradient-based models."
        ],
        "acceptable_examples": [
            "Standardization can transform a feature using its mean and standard deviation.",
            "Min-max normalization can transform values into a specified range such as zero to one."
        ]
    },


    "MLE_E03": {
        "question": (
            "What is the purpose of a machine learning model?"
        ),
        "key_concepts": [
            "A machine learning model learns patterns or relationships from data.",
            "The learned model can be used to make predictions, classifications, estimates, or other data-driven outputs.",
            "The goal is generally to perform appropriately on relevant unseen data rather than merely memorize training examples.",
            "The model maps input information to an output or representation according to the learning task."
        ],
        "acceptable_examples": [
            "A classification model can predict whether an email is spam.",
            "A regression model can estimate a numerical value such as house price."
        ]
    },


    "MLE_E04": {
        "question": (
            "What is the difference between classification and regression?"
        ),
        "key_concepts": [
            "Classification predicts discrete classes or categories.",
            "Regression predicts continuous numerical values.",
            "The appropriate problem type depends on the target variable and objective.",
            "Classification and regression generally use different evaluation metrics."
        ],
        "acceptable_examples": [
            "Predicting spam or not spam is classification.",
            "Predicting house price is regression."
        ]
    },


    # ========================================================
    # MEDIUM
    # ========================================================

    "MLE_M01": {
        "question": (
            "How would you handle missing values before training a machine learning model?"
        ),
        "key_concepts": [
            "The amount and pattern of missing values should be investigated before selecting a treatment.",
            "Missing values can sometimes be removed or imputed using appropriate statistical or model-based methods.",
            "The imputation strategy should depend on the feature type, missingness pattern, model, and problem context.",
            "Preprocessing parameters should be learned from training data and then applied to validation or test data to avoid leakage."
        ],
        "acceptable_examples": [
            "Numerical values may be imputed using the median when appropriate.",
            "Categorical missing values can use an appropriate category or imputation method.",
            "An imputer should be fitted using training data rather than the complete dataset."
        ]
    },


    "MLE_M02": {
        "question": (
            "How would you detect overfitting and reduce it?"
        ),
        "key_concepts": [
            "Overfitting can be indicated by strong training performance but substantially weaker validation or test performance.",
            "Validation data or cross-validation can be used to estimate generalization performance.",
            "Regularization, reducing model complexity, early stopping, or collecting more representative data can help reduce overfitting.",
            "The selected prevention technique should be appropriate for the model and dataset."
        ],
        "acceptable_examples": [
            "A large training-validation performance gap can indicate overfitting.",
            "L1 or L2 regularization can reduce excessive model complexity in suitable models.",
            "Early stopping can stop training when validation performance stops improving."
        ]
    },


    "MLE_M03": {
        "question": (
            "Explain the purpose of hyperparameter tuning."
        ),
        "key_concepts": [
            "Hyperparameters are configuration values that are chosen outside the ordinary parameter-learning process.",
            "Hyperparameter tuning searches for configurations that provide better validation performance according to a chosen objective.",
            "Candidate configurations should be evaluated using validation data or an appropriate cross-validation procedure.",
            "The final test set should remain separate from repeated hyperparameter selection."
        ],
        "acceptable_examples": [
            "Grid search can evaluate a predefined set of hyperparameter combinations.",
            "Random search can sample combinations from specified ranges.",
            "Learning rate, tree depth, and regularization strength are examples of hyperparameters."
        ]
    },


    "MLE_M04": {
        "question": (
            "How would you choose between precision recall and F1 score for a classification problem?"
        ),
        "key_concepts": [
            "The choice depends on the consequences of false positives and false negatives.",
            "Precision is important when false positive predictions are particularly costly.",
            "Recall is important when missing positive cases is particularly costly.",
            "F1 score combines precision and recall using their harmonic mean and can be useful when both need to be balanced."
        ],
        "acceptable_examples": [
            "Recall may be emphasized when missing an important positive case is costly.",
            "Precision may be emphasized when false alarms are costly.",
            "F1 can summarize precision and recall when neither should dominate the evaluation."
        ]
    },


    # ========================================================
    # HARD
    # ========================================================

    "MLE_H01": {
        "question": (
            "How would you detect model drift after deploying a machine learning model?"
        ),
        "key_concepts": [
            "Production input distributions and relevant model outputs should be monitored over time.",
            "Changes in feature distributions can indicate data or covariate drift.",
            "When reliable ground-truth labels become available, predictive performance should be monitored for degradation.",
            "Drift detection should use defined reference periods, metrics, thresholds, and investigation procedures rather than relying on a single signal."
        ],
        "acceptable_examples": [
            "Compare production feature distributions with a reference training or validation distribution.",
            "Track metrics such as accuracy, precision, recall, error, or calibration when labels become available.",
            "Statistical distribution measures can be used as monitoring signals where appropriate."
        ]
    },


    "MLE_H02": {
        "question": (
            "How would you design a machine learning inference system that handles a large number of requests?"
        ),
        "key_concepts": [
            "The inference service should be designed for scalable request handling and appropriate latency and throughput requirements.",
            "Horizontal scaling and load balancing can distribute requests across multiple inference workers or instances.",
            "Batching, caching, asynchronous processing, or model optimization can improve efficiency when appropriate.",
            "The system should include monitoring, fault handling, capacity planning, and suitable deployment infrastructure."
        ],
        "acceptable_examples": [
            "Multiple model-serving instances can operate behind a load balancer.",
            "Frequently repeated predictions may be cached when the application permits it.",
            "Batch inference can improve throughput for workloads that do not require immediate individual responses."
        ]
    },


    "MLE_H03": {
        "question": (
            "How would you monitor the performance of a machine learning model in production when ground-truth labels are delayed?"
        ),
        "key_concepts": [
            "When labels are delayed, direct predictive performance metrics cannot immediately be calculated for recent predictions.",
            "Proxy signals such as input drift, prediction distributions, confidence or calibration-related signals, and system behavior can be monitored while waiting for labels.",
            "Operational metrics such as latency, error rates, throughput, and missing-feature rates should also be monitored.",
            "When ground-truth labels arrive, predictions should be joined with their outcomes and true model performance should be evaluated retrospectively."
        ],
        "acceptable_examples": [
            "Monitor whether production features differ substantially from the reference distribution.",
            "Track prediction-class proportions for unexpected changes.",
            "Store prediction IDs and timestamps so delayed labels can later be matched to predictions."
        ]
    },


    "MLE_H04": {
        "question": (
            "How would you safely deploy a new model version while minimizing the risk of performance degradation?"
        ),
        "key_concepts": [
            "The new model should be validated offline using appropriate datasets and predefined acceptance criteria before deployment.",
            "Controlled deployment strategies such as shadow testing, canary deployment, or staged rollout can reduce deployment risk.",
            "Production technical and model-quality metrics should be monitored during rollout.",
            "A rollback mechanism and versioned model artifacts should be available if the new model causes unacceptable degradation."
        ],
        "acceptable_examples": [
            "A canary deployment can initially send a small proportion of production traffic to the new model.",
            "Shadow deployment can compare a new model with the existing model without using the new predictions for user-facing decisions.",
            "The previous model version can be restored when predefined rollback conditions are met."
        ]
    }
}


# ============================================================
# EXPECTED QUESTION IDS
# ============================================================

EXPECTED_MACHINE_LEARNING_ENGINEER_IDS = {

    "MLE_E01",
    "MLE_E02",
    "MLE_E03",
    "MLE_E04",

    "MLE_M01",
    "MLE_M02",
    "MLE_M03",
    "MLE_M04",

    "MLE_H01",
    "MLE_H02",
    "MLE_H03",
    "MLE_H04"
}


# ============================================================
# STRUCTURAL VALIDATOR
# ============================================================

def validate_ml_engineer_references():

    actual_ids = set(
        MACHINE_LEARNING_ENGINEER_REFERENCES.keys()
    )

    errors = []


    missing = (
        EXPECTED_MACHINE_LEARNING_ENGINEER_IDS
        - actual_ids
    )

    extra = (
        actual_ids
        - EXPECTED_MACHINE_LEARNING_ENGINEER_IDS
    )


    if missing:

        errors.append(
            "Missing IDs: "
            + ", ".join(sorted(missing))
        )


    if extra:

        errors.append(
            "Unexpected IDs: "
            + ", ".join(sorted(extra))
        )


    for question_id, reference in (
        MACHINE_LEARNING_ENGINEER_REFERENCES.items()
    ):

        question = reference.get(
            "question"
        )

        concepts = reference.get(
            "key_concepts"
        )

        examples = reference.get(
            "acceptable_examples"
        )


        if not question:

            errors.append(
                f"{question_id}: question is empty."
            )


        if (
            not isinstance(concepts, list)
            or len(concepts) == 0
        ):

            errors.append(
                f"{question_id}: "
                "key_concepts are missing."
            )


        if not isinstance(
            examples,
            list
        ):

            errors.append(
                f"{question_id}: "
                "acceptable_examples must be a list."
            )


    return {
        "valid": len(errors) == 0,
        "reference_count": len(actual_ids),
        "errors": errors
    }


# ============================================================
# DEVELOPMENT VALIDATION
# ============================================================

if __name__ == "__main__":

    print("=" * 70)

    print(
        "AEGIE MACHINE LEARNING ENGINEER "
        "REFERENCE VALIDATOR"
    )

    print("=" * 70)

    result = (
        validate_ml_engineer_references()
    )

    print()

    print(
        "Reference count:",
        result["reference_count"]
    )

    print(
        "Valid:",
        result["valid"]
    )

    print()


    if result["valid"]:

        print(
            "PASS: All 12 Machine Learning Engineer "
            "references are structurally valid."
        )

    else:

        print(
            "FAIL: Machine Learning Engineer "
            "reference validation failed."
        )

        for error in result["errors"]:

            print(
                "-",
                error
            )


    print()

    print("=" * 70)

    print(
        "These are semantic reference concepts, "
        "not participant responses."
    )

    print(
        "No record was added to the "
        "3000-sample research dataset."
    )

    print(
        "Expert review is required before "
        "the final research experiment."
    )

    print("=" * 70)