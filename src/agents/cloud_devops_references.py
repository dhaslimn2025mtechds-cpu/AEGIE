# ============================================================
# AEGIE CLOUD/DEVOPS ENGINEER REFERENCE KNOWLEDGE
# ============================================================
#
# Reference concepts for the 12 Cloud/DevOps Engineer
# interview questions.
#
# IMPORTANT:
# - These are NOT participant answers.
# - These are NOT primary dataset samples.
# - They are semantic reference concepts for AEGIE.
# - Expert review is required before the final study.
# ============================================================


CLOUD_DEVOPS_ENGINEER_REFERENCES = {

    # ========================================================
    # EASY
    # ========================================================

    "CD_E01": {
        "question": (
            "What is cloud computing?"
        ),
        "key_concepts": [
            "Cloud computing provides computing resources and services over a network, commonly the internet.",
            "Cloud resources can include servers, storage, databases, networking, and software services.",
            "Resources can often be provisioned or scaled on demand.",
            "Cloud services commonly use shared infrastructure and usage-based or service-based consumption models."
        ],
        "acceptable_examples": [
            "A company can run an application on cloud virtual machines instead of maintaining its own physical servers.",
            "Cloud object storage can be used to store application files and backups."
        ]
    },


    "CD_E02": {
        "question": (
            "What is the difference between a virtual machine and a container?"
        ),
        "key_concepts": [
            "A virtual machine virtualizes hardware and normally runs its own guest operating system.",
            "A container provides process-level isolation while sharing the host operating system kernel.",
            "Containers are generally more lightweight and can start faster than full virtual machines.",
            "Virtual machines typically provide stronger operating-system-level separation, while containers provide portable application packaging and isolation."
        ],
        "acceptable_examples": [
            "A virtual machine can run a separate Linux or Windows guest operating system.",
            "Docker containers can package an application together with its required runtime dependencies."
        ]
    },


    "CD_E03": {
        "question": (
            "What is version control and why is Git used?"
        ),
        "key_concepts": [
            "Version control records and manages changes to files over time.",
            "It allows developers to track history and restore earlier versions when necessary.",
            "Git is a distributed version control system that supports branching and merging.",
            "Git helps multiple developers collaborate on the same codebase while maintaining change history."
        ],
        "acceptable_examples": [
            "A developer can create a Git branch to work on a feature without immediately changing the main branch.",
            "Git commits record changes and their history."
        ]
    },


    "CD_E04": {
        "question": (
            "What is continuous integration?"
        ),
        "key_concepts": [
            "Continuous integration is a development practice in which code changes are integrated frequently into a shared repository.",
            "Automated builds and tests are commonly triggered when changes are integrated.",
            "Continuous integration helps detect integration problems and defects earlier.",
            "A CI pipeline can provide repeatable validation of software changes."
        ],
        "acceptable_examples": [
            "A push to a Git repository can automatically trigger unit tests.",
            "A CI pipeline can build an application and report whether automated tests pass."
        ]
    },


    # ========================================================
    # MEDIUM
    # ========================================================

    "CD_M01": {
        "question": (
            "Explain the difference between continuous integration and continuous deployment."
        ),
        "key_concepts": [
            "Continuous integration focuses on frequently integrating code changes and automatically validating them through builds and tests.",
            "Continuous deployment automatically releases validated changes to production when the deployment pipeline succeeds.",
            "CI primarily addresses code integration and verification.",
            "Continuous deployment extends automation through the production release process."
        ],
        "acceptable_examples": [
            "CI may automatically run tests whenever code is pushed.",
            "Continuous deployment can automatically release a successfully validated build to production."
        ]
    },


    "CD_M02": {
        "question": (
            "What is containerization and why is it useful in application deployment?"
        ),
        "key_concepts": [
            "Containerization packages an application together with the runtime dependencies required for execution.",
            "Containers provide isolated application environments while generally sharing the host operating system kernel.",
            "Container images improve consistency across development, testing, and deployment environments.",
            "Containers can support portability, repeatable deployment, and efficient scaling."
        ],
        "acceptable_examples": [
            "A Docker image can package a web application and its runtime dependencies.",
            "The same container image can be tested before being deployed to another compatible environment."
        ]
    },


    "CD_M03": {
        "question": (
            "How would you monitor the health of an application running in the cloud?"
        ),
        "key_concepts": [
            "Application health should be monitored using relevant metrics, logs, traces, and health checks.",
            "Infrastructure metrics can include CPU, memory, disk, network usage, and resource availability.",
            "Application metrics can include latency, throughput, error rates, and request success rates.",
            "Alerts should be configured for meaningful abnormal conditions so failures can be investigated promptly."
        ],
        "acceptable_examples": [
            "Monitor HTTP error rates and response latency.",
            "Use application logs to investigate failed requests.",
            "A health-check endpoint can indicate whether a service instance is available."
        ]
    },


    "CD_M04": {
        "question": (
            "What is infrastructure as code and what problem does it solve?"
        ),
        "key_concepts": [
            "Infrastructure as code represents infrastructure configuration using machine-readable configuration or code.",
            "It allows infrastructure provisioning and configuration to be automated.",
            "Infrastructure definitions can be version controlled and reviewed.",
            "It helps improve repeatability and reduce inconsistencies caused by manual infrastructure configuration."
        ],
        "acceptable_examples": [
            "Terraform can describe cloud infrastructure using configuration files.",
            "Infrastructure configuration stored in Git can be reviewed and versioned."
        ]
    },


    # ========================================================
    # HARD
    # ========================================================

    "CD_H01": {
        "question": (
            "How would you design a highly available cloud application that can tolerate server failures?"
        ),
        "key_concepts": [
            "The application should avoid a single point of failure by using redundant service instances.",
            "Traffic can be distributed across healthy instances using load balancing.",
            "Instances or services can be distributed across separate failure domains such as availability zones where appropriate.",
            "Health checks, automatic recovery, replicated or resilient data services, and monitoring should support failure detection and continuity."
        ],
        "acceptable_examples": [
            "Run multiple application instances behind a load balancer.",
            "Deploy instances across multiple availability zones.",
            "Replace unhealthy instances automatically after failed health checks."
        ]
    },


    "CD_H02": {
        "question": (
            "How would you investigate and recover from a failed production deployment?"
        ),
        "key_concepts": [
            "The impact and symptoms of the failed deployment should first be identified using monitoring, logs, metrics, traces, and deployment records.",
            "The deployment change should be compared with the previously working version to help identify the cause.",
            "Service can be restored using a safe rollback or other recovery procedure when appropriate.",
            "After recovery, the root cause should be investigated and corrective measures should be added to reduce the chance of recurrence."
        ],
        "acceptable_examples": [
            "Check application error logs immediately after the deployment.",
            "Rollback to the previous stable release when the new release causes critical failures.",
            "Add an automated test for the defect that caused the deployment failure."
        ]
    },


    "CD_H03": {
        "question": (
            "How would you design an auto-scaling strategy for an application with unpredictable traffic?"
        ),
        "key_concepts": [
            "Scaling signals should be selected based on application behavior and capacity requirements.",
            "Possible signals include CPU utilization, memory usage, request rate, queue length, latency, or custom application metrics.",
            "Minimum and maximum capacity, scaling thresholds or targets, and stabilization or cooldown behavior should be defined.",
            "The strategy should be tested and monitored to balance availability, responsiveness, and resource cost."
        ],
        "acceptable_examples": [
            "Add application instances when request load or CPU usage remains above an appropriate target.",
            "Queue length can be used as a scaling signal for worker services.",
            "Maintain minimum capacity so the service can handle normal traffic without waiting for new instances."
        ]
    },


    "CD_H04": {
        "question": (
            "How would you implement a deployment strategy that minimizes downtime and allows safe rollback?"
        ),
        "key_concepts": [
            "A controlled deployment strategy should limit user impact while the new version is validated.",
            "Blue-green, canary, or rolling deployment strategies can reduce downtime when appropriately implemented.",
            "Health checks and production metrics should be monitored during the rollout.",
            "The previous stable version should remain recoverable so traffic or deployment can be rolled back when predefined failure conditions occur."
        ],
        "acceptable_examples": [
            "Blue-green deployment can switch traffic between old and new environments after validation.",
            "Canary deployment can expose the new version to a limited amount of traffic before wider rollout.",
            "Automated rollback can be triggered when critical health metrics violate predefined conditions."
        ]
    }
}


# ============================================================
# EXPECTED QUESTION IDS
# ============================================================

EXPECTED_CLOUD_DEVOPS_ENGINEER_IDS = {

    "CD_E01",
    "CD_E02",
    "CD_E03",
    "CD_E04",

    "CD_M01",
    "CD_M02",
    "CD_M03",
    "CD_M04",

    "CD_H01",
    "CD_H02",
    "CD_H03",
    "CD_H04"
}


# ============================================================
# STRUCTURAL VALIDATOR
# ============================================================

def validate_cloud_devops_references():

    actual_ids = set(
        CLOUD_DEVOPS_ENGINEER_REFERENCES.keys()
    )

    errors = []


    # --------------------------------------------------------
    # Missing / unexpected IDs
    # --------------------------------------------------------

    missing = (
        EXPECTED_CLOUD_DEVOPS_ENGINEER_IDS
        - actual_ids
    )

    extra = (
        actual_ids
        - EXPECTED_CLOUD_DEVOPS_ENGINEER_IDS
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


    # --------------------------------------------------------
    # Validate reference structure
    # --------------------------------------------------------

    for question_id, reference in (
        CLOUD_DEVOPS_ENGINEER_REFERENCES.items()
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
        "AEGIE CLOUD/DEVOPS ENGINEER "
        "REFERENCE VALIDATOR"
    )

    print("=" * 70)


    result = (
        validate_cloud_devops_references()
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
            "PASS: All 12 Cloud/DevOps Engineer "
            "references are structurally valid."
        )

    else:

        print(
            "FAIL: Cloud/DevOps Engineer "
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