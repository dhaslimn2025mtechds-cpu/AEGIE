# ============================================================
# AEGIE CYBERSECURITY ANALYST REFERENCE KNOWLEDGE
# ============================================================
#
# Reference concepts for the 12 Cybersecurity Analyst
# interview questions.
#
# IMPORTANT:
# - These are NOT participant answers.
# - These are NOT primary dataset samples.
# - They are semantic reference concepts for AEGIE.
# - Expert review is required before the final study.
# ============================================================


CYBERSECURITY_ANALYST_REFERENCES = {

    # ========================================================
    # EASY
    # ========================================================

    "CS_E01": {
        "question": (
            "What is cybersecurity?"
        ),
        "key_concepts": [
            "Cybersecurity is the practice of protecting systems, networks, applications, and data from digital threats.",
            "Cybersecurity aims to reduce unauthorized access, misuse, disruption, alteration, or destruction of information and systems.",
            "Important security objectives include confidentiality, integrity, and availability.",
            "Cybersecurity uses technical, administrative, and operational controls to manage security risks."
        ],
        "acceptable_examples": [
            "Firewalls and access controls can help protect systems from unauthorized access.",
            "Security monitoring can help identify suspicious activity."
        ]
    },


    "CS_E02": {
        "question": (
            "What is the difference between authentication and authorization?"
        ),
        "key_concepts": [
            "Authentication verifies the identity of a user, device, or other entity.",
            "Authorization determines what an authenticated entity is permitted to access or perform.",
            "Authentication normally occurs before authorization decisions are applied.",
            "Authorization can restrict access according to roles, permissions, policies, or other access-control rules."
        ],
        "acceptable_examples": [
            "Entering a password can be part of authentication.",
            "Allowing only administrators to modify user accounts is an authorization decision."
        ]
    },


    "CS_E03": {
        "question": (
            "What is phishing?"
        ),
        "key_concepts": [
            "Phishing is a social-engineering technique in which an attacker impersonates a trusted or legitimate source.",
            "The attacker attempts to deceive a person into revealing information, opening malicious content, or performing an unsafe action.",
            "Phishing can be delivered through email, messages, websites, or other communication channels.",
            "Common targets include credentials, financial information, and access to organizational systems."
        ],
        "acceptable_examples": [
            "A fake login page may be used to steal a user's credentials.",
            "An email pretending to be from a trusted organization may contain a malicious link."
        ]
    },


    "CS_E04": {
        "question": (
            "What is a firewall and why is it used?"
        ),
        "key_concepts": [
            "A firewall monitors and controls network traffic according to defined security rules.",
            "A firewall can allow or block traffic based on characteristics such as addresses, ports, protocols, connections, or application information depending on its capabilities.",
            "Firewalls help reduce unauthorized or unwanted network access.",
            "A firewall is one security control and should normally be used as part of a broader defense strategy."
        ],
        "acceptable_examples": [
            "A firewall can block unwanted inbound connections to a server.",
            "Rules can permit required application traffic while denying unnecessary network traffic."
        ]
    },


    # ========================================================
    # MEDIUM
    # ========================================================

    "CS_M01": {
        "question": (
            "What is the difference between symmetric and asymmetric encryption?"
        ),
        "key_concepts": [
            "Symmetric encryption uses the same secret key, or effectively the same shared secret, for encryption and decryption.",
            "Asymmetric cryptography uses a mathematically related public and private key pair.",
            "Symmetric encryption is generally efficient for protecting larger amounts of data.",
            "Asymmetric cryptography can support functions such as key establishment and digital signatures, depending on the algorithm and protocol."
        ],
        "acceptable_examples": [
            "AES is a commonly used symmetric encryption algorithm.",
            "RSA and elliptic-curve cryptography are examples of asymmetric cryptographic approaches.",
            "Protocols can combine asymmetric techniques for key establishment with symmetric encryption for data transfer."
        ]
    },


    "CS_M02": {
        "question": (
            "How would you identify a phishing email?"
        ),
        "key_concepts": [
            "The sender identity and domain should be checked for suspicious or misleading details.",
            "Links and requested destinations should be inspected carefully before interaction.",
            "Unexpected requests for credentials, payments, sensitive information, or urgent actions are warning signs.",
            "Attachments, unusual language, impersonation, and message context should be evaluated rather than relying on a single indicator."
        ],
        "acceptable_examples": [
            "A domain that closely imitates a legitimate company domain can be suspicious.",
            "An unexpected request to immediately enter a password through an email link can indicate phishing.",
            "A suspicious attachment from an unexpected sender should not be opened without verification."
        ]
    },


    "CS_M03": {
        "question": (
            "What is multi-factor authentication and why does it improve security?"
        ),
        "key_concepts": [
            "Multi-factor authentication requires evidence from more than one authentication factor category.",
            "Authentication factors can include something the user knows, possesses, or is.",
            "MFA reduces reliance on a password as the only protection for an account.",
            "Compromise of one factor alone may be insufficient for successful authentication when additional independent factors are required."
        ],
        "acceptable_examples": [
            "A password combined with a hardware security key is an example of multi-factor authentication.",
            "A password plus an authenticator-based verification mechanism can provide an additional authentication factor."
        ]
    },


    "CS_M04": {
        "question": (
            "What is the principle of least privilege?"
        ),
        "key_concepts": [
            "The principle of least privilege gives users, applications, and processes only the permissions necessary for their required tasks.",
            "Unnecessary permissions should be avoided or removed.",
            "Privileges should be limited in scope and, where appropriate, duration.",
            "Least privilege can reduce the potential impact of compromised accounts, applications, or accidental misuse."
        ],
        "acceptable_examples": [
            "A user who only needs to read reports should not automatically receive administrative privileges.",
            "A service account should receive only the permissions required by that service."
        ]
    },


    # ========================================================
    # HARD
    # ========================================================

    "CS_H01": {
        "question": (
            "How would you investigate suspicious login activity in an organization?"
        ),
        "key_concepts": [
            "Relevant authentication and security logs should be collected and reviewed to understand the suspicious activity.",
            "Important context can include timestamps, source locations or addresses, devices, accounts, authentication results, and behavioral patterns.",
            "The activity should be correlated with other available security evidence to determine whether it represents legitimate use or potential compromise.",
            "Confirmed or high-risk incidents should follow the organization's incident-response process, including containment, evidence preservation, remediation, and documentation."
        ],
        "acceptable_examples": [
            "Review repeated failed logins followed by an unusual successful login.",
            "Compare the login with the user's normal device or access pattern where such data is available and appropriate.",
            "Investigate related alerts or account activity occurring around the same time."
        ]
    },


    "CS_H02": {
        "question": (
            "How would you respond if you discovered that an employee account had been compromised?"
        ),
        "key_concepts": [
            "The compromised account should be contained promptly according to the organization's incident-response procedures.",
            "Active sessions, credentials, authentication factors, and access tokens may need to be revoked or reset depending on the incident.",
            "Logs and other evidence should be preserved and investigated to determine the scope, cause, and actions performed through the account.",
            "After containment and remediation, access should be restored safely and relevant security controls should be improved based on the incident findings."
        ],
        "acceptable_examples": [
            "Disable or restrict the compromised account while the incident is investigated.",
            "Revoke active sessions and reset compromised credentials.",
            "Review account activity to identify unauthorized access to systems or data."
        ]
    },


    "CS_H03": {
        "question": (
            "How would you detect and respond to unusual network traffic that may indicate an attack?"
        ),
        "key_concepts": [
            "Network telemetry and security monitoring should be used to identify traffic patterns that differ from expected behavior or match known indicators.",
            "Relevant evidence can include source and destination information, ports, protocols, connection patterns, traffic volume, and security alerts.",
            "Suspicious activity should be correlated with endpoint, identity, application, and other available security evidence before determining the incident scope.",
            "Response can include containment, blocking malicious communication, isolating affected systems, preserving evidence, remediation, and continued monitoring."
        ],
        "acceptable_examples": [
            "An unexpected increase in outbound traffic from a server can be investigated for possible compromise or data exfiltration.",
            "Repeated connections to known malicious infrastructure can trigger investigation and containment.",
            "A compromised endpoint may be isolated from the network according to incident-response procedures."
        ]
    },


    "CS_H04": {
        "question": (
            "How would you design a security monitoring strategy for a cloud-based application?"
        ),
        "key_concepts": [
            "The monitoring strategy should identify important assets, threats, trust boundaries, and security-relevant events for the cloud application.",
            "Logs and telemetry should be collected from relevant identity, application, infrastructure, network, data, and cloud-control sources.",
            "Detection rules or analytics should focus on meaningful suspicious behavior and be connected to alert triage and incident-response procedures.",
            "Monitoring should include secure log handling, appropriate retention, access control, testing, tuning, and continuous improvement."
        ],
        "acceptable_examples": [
            "Monitor unusual authentication events and privilege changes.",
            "Collect application, cloud audit, and network security logs in a centralized monitoring system.",
            "Create alerts for suspicious administrative activity or unexpected access to sensitive resources."
        ]
    }
}


# ============================================================
# EXPECTED QUESTION IDS
# ============================================================

EXPECTED_CYBERSECURITY_ANALYST_IDS = {

    "CS_E01",
    "CS_E02",
    "CS_E03",
    "CS_E04",

    "CS_M01",
    "CS_M02",
    "CS_M03",
    "CS_M04",

    "CS_H01",
    "CS_H02",
    "CS_H03",
    "CS_H04"
}


# ============================================================
# STRUCTURAL VALIDATOR
# ============================================================

def validate_cybersecurity_references():

    actual_ids = set(
        CYBERSECURITY_ANALYST_REFERENCES.keys()
    )

    errors = []


    # --------------------------------------------------------
    # Check IDs
    # --------------------------------------------------------

    missing = (
        EXPECTED_CYBERSECURITY_ANALYST_IDS
        - actual_ids
    )

    extra = (
        actual_ids
        - EXPECTED_CYBERSECURITY_ANALYST_IDS
    )


    if missing:

        errors.append(
            "Missing IDs: "
            + ", ".join(
                sorted(missing)
            )
        )


    if extra:

        errors.append(
            "Unexpected IDs: "
            + ", ".join(
                sorted(extra)
            )
        )


    # --------------------------------------------------------
    # Validate structure
    # --------------------------------------------------------

    for question_id, reference in (
        CYBERSECURITY_ANALYST_REFERENCES.items()
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


    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

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
        "AEGIE CYBERSECURITY ANALYST "
        "REFERENCE VALIDATOR"
    )

    print("=" * 70)


    result = (
        validate_cybersecurity_references()
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
            "PASS: All 12 Cybersecurity Analyst "
            "references are structurally valid."
        )

    else:

        print(
            "FAIL: Cybersecurity Analyst "
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