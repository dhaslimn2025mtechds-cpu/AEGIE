# ============================================================
# AEGIE CONCEPT-LEVEL SEMANTIC EVALUATOR
# ============================================================
#
# Purpose:
# Compare the complete participant transcript with each
# semantic reference concept using MiniLM ONNX embeddings.
#
# Reference knowledge is retrieved from the CENTRAL
# 72-question reference registry covering all six roles.
#
# IMPORTANT:
# - Similarities are semantic evidence/features only.
# - They are NOT human labels.
# - They are NOT final 1-5 AEGIE scores.
# - No adaptive threshold is applied here.
# ============================================================

import numpy as np


# ============================================================
# PACKAGE-SAFE IMPORTS
# ============================================================

try:

    from .minilm_embedder import (
        get_shared_minilm_embedder,
        cosine_similarity
    )

    from .reference_registry import (
        get_reference_answer
    )

except ImportError:

    from minilm_embedder import (
        get_shared_minilm_embedder,
        cosine_similarity
    )

    from reference_registry import (
        get_reference_answer
    )


# ============================================================
# CONCEPT EVALUATOR
# ============================================================

class ConceptEvaluator:

    def __init__(self):

        self.embedder = get_shared_minilm_embedder()


    # ========================================================
    # EVALUATE
    # ========================================================

    def evaluate(
        self,
        question_id,
        transcript
    ):

        # ----------------------------------------------------
        # Validate question ID
        # ----------------------------------------------------

        if question_id is None:

            return {
                "success": False,
                "status": "QUESTION_ID_MISSING",
                "question_id": None,
                "concept_results": [],
                "mean_similarity": None,
                "max_similarity": None,
                "min_similarity": None,
                "reason": "Question ID is unavailable."
            }


        question_id = str(
            question_id
        ).strip()


        if not question_id:

            return {
                "success": False,
                "status": "QUESTION_ID_EMPTY",
                "question_id": question_id,
                "concept_results": [],
                "mean_similarity": None,
                "max_similarity": None,
                "min_similarity": None,
                "reason": "Question ID is empty."
            }


        # ----------------------------------------------------
        # Validate transcript
        # ----------------------------------------------------

        if transcript is None:

            return {
                "success": False,
                "status": "TRANSCRIPT_MISSING",
                "question_id": question_id,
                "concept_results": [],
                "mean_similarity": None,
                "max_similarity": None,
                "min_similarity": None,
                "reason": "Transcript is unavailable."
            }


        transcript = str(
            transcript
        ).strip()


        if not transcript:

            return {
                "success": False,
                "status": "TRANSCRIPT_EMPTY",
                "question_id": question_id,
                "concept_results": [],
                "mean_similarity": None,
                "max_similarity": None,
                "min_similarity": None,
                "reason": "Transcript is empty."
            }


        # ----------------------------------------------------
        # Get reference knowledge from CENTRAL REGISTRY
        # ----------------------------------------------------

        reference = get_reference_answer(
            question_id
        )


        if reference is None:

            return {
                "success": False,
                "status": "REFERENCE_NOT_FOUND",
                "question_id": question_id,
                "concept_results": [],
                "mean_similarity": None,
                "max_similarity": None,
                "min_similarity": None,
                "reason": (
                    f"No reference knowledge "
                    f"found for {question_id}."
                )
            }


        reference_role = reference.get(
            "job_role"
        )


        reference_question = reference.get(
            "question"
        )


        concepts = reference.get(
            "key_concepts",
            []
        )


        if not concepts:

            return {
                "success": False,
                "status": "CONCEPTS_MISSING",
                "question_id": question_id,
                "reference_role": reference_role,
                "concept_results": [],
                "mean_similarity": None,
                "max_similarity": None,
                "min_similarity": None,
                "reason": (
                    "Reference concepts are unavailable."
                )
            }


        # ----------------------------------------------------
        # Encode transcript + concepts in one batch
        # ----------------------------------------------------

        texts = [
            transcript
        ] + concepts


        embeddings = self.embedder.encode(
            texts
        )


        transcript_embedding = (
            embeddings[0]
        )


        concept_embeddings = (
            embeddings[1:]
        )


        # ----------------------------------------------------
        # Calculate whole-answer-to-concept similarities
        # ----------------------------------------------------

        concept_results = []


        for index, (
            concept,
            concept_embedding
        ) in enumerate(

            zip(
                concepts,
                concept_embeddings
            ),

            start=1
        ):

            similarity = cosine_similarity(
                transcript_embedding,
                concept_embedding
            )


            concept_results.append(
                {
                    "concept_number":
                        index,

                    "concept":
                        concept,

                    "similarity":
                        round(
                            float(similarity),
                            4
                        )
                }
            )


        # ----------------------------------------------------
        # Aggregate semantic evidence
        # ----------------------------------------------------

        similarities = [

            result[
                "similarity"
            ]

            for result in concept_results
        ]


        mean_similarity = float(
            np.mean(
                similarities
            )
        )


        max_similarity = float(
            np.max(
                similarities
            )
        )


        min_similarity = float(
            np.min(
                similarities
            )
        )


        # ----------------------------------------------------
        # Return semantic features
        # ----------------------------------------------------

        return {

            "success": True,

            "status":
                "SEMANTIC_EVIDENCE_READY",

            "question_id":
                question_id,

            "reference_role":
                reference_role,

            "question_text":
                reference_question,

            "concept_count":
                len(concepts),

            "concept_results":
                concept_results,

            "mean_similarity":
                round(
                    mean_similarity,
                    4
                ),

            "max_similarity":
                round(
                    max_similarity,
                    4
                ),

            "min_similarity":
                round(
                    min_similarity,
                    4
                ),

            "reason":
                None
        }


# ============================================================
# DEVELOPMENT TEST
# ============================================================

def main():

    print("=" * 70)

    print(
        "AEGIE MULTI-ROLE CONCEPT-LEVEL "
        "SEMANTIC TEST"
    )

    print("=" * 70)


    evaluator = ConceptEvaluator()


    # --------------------------------------------------------
    # NON-DATA-SCIENTIST DEVELOPMENT TEST
    #
    # CS_E02:
    # What is the difference between authentication
    # and authorization?
    #
    # This proves the evaluator can retrieve references
    # through the new 72-question central registry.
    #
    # This answer is development-only.
    # It is NOT primary participant research data.
    # --------------------------------------------------------

    question_id = "CS_E02"


    test_answer = (

        "Authentication verifies who the user is. "

        "For example, a password or another login factor "
        "can be used to verify identity. "

        "Authorization determines what an authenticated "
        "user is allowed to access or perform. "

        "For example, an administrator may have permission "
        "to modify accounts while a normal user does not."
    )


    print()

    print(
        "Test question ID:",
        question_id
    )


    result = evaluator.evaluate(
        question_id=question_id,
        transcript=test_answer
    )


    print()

    print(
        "Status:",
        result[
            "status"
        ]
    )


    if not result[
        "success"
    ]:

        print()

        print(
            "Reason:",
            result[
                "reason"
            ]
        )

        return


    # --------------------------------------------------------
    # Registry lookup proof
    # --------------------------------------------------------

    print()

    print(
        "Reference role:",
        result[
            "reference_role"
        ]
    )


    print(
        "Question ID:",
        result[
            "question_id"
        ]
    )


    print(
        "Question:",
        result[
            "question_text"
        ]
    )


    print()

    print(
        "Concept count:",
        result[
            "concept_count"
        ]
    )


    # --------------------------------------------------------
    # Concept-level evidence
    # --------------------------------------------------------

    print()

    print("-" * 70)

    print(
        "CONCEPT-LEVEL EVIDENCE"
    )

    print("-" * 70)


    for item in result[
        "concept_results"
    ]:

        print()

        print(
            f"Concept "
            f"{item['concept_number']}:"
        )

        print(
            item[
                "concept"
            ]
        )

        print(
            "Semantic similarity:",
            item[
                "similarity"
            ]
        )


    # --------------------------------------------------------
    # Aggregated features
    # --------------------------------------------------------

    print()

    print("-" * 70)

    print(
        "AGGREGATED SEMANTIC FEATURES"
    )

    print("-" * 70)


    print(
        "Mean similarity:",
        result[
            "mean_similarity"
        ]
    )


    print(
        "Maximum similarity:",
        result[
            "max_similarity"
        ]
    )


    print(
        "Minimum similarity:",
        result[
            "min_similarity"
        ]
    )


    # --------------------------------------------------------
    # Final development result
    # --------------------------------------------------------

    print()

    print("=" * 70)

    print(
        "PASS: MULTI-ROLE CONCEPT-LEVEL "
        "SEMANTIC EVIDENCE GENERATED"
    )

    print("=" * 70)


    print()

    print(
        "Central registry lookup: PASS"
    )

    print(
        "Question tested: CS_E02"
    )

    print(
        "Expected role: Cybersecurity Analyst"
    )


    print()

    print(
        "These similarity values are "
        "semantic features only."
    )

    print(
        "They are NOT final 1-5 "
        "AEGIE evaluation scores."
    )

    print(
        "No arbitrary similarity "
        "threshold was applied."
    )

    print(
        "No human annotation label "
        "was used."
    )

    print(
        "Score calibration will later "
        "use genuine human-annotated "
        "research data."
    )


# ============================================================
# RUN DEVELOPMENT TEST
# ============================================================

if __name__ == "__main__":

    main()