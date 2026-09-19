# ============================================================
# AEGIE SENTENCE-LEVEL CONCEPT EVALUATOR
# ============================================================
#
# Development semantic evidence component.
#
# For every reference concept:
#   1. Retrieve the correct semantic reference from the
#      central 72-question reference registry.
#   2. Split the participant answer into sentences.
#   3. Compare every concept with every answer sentence.
#   4. Keep the highest similarity for each concept.
#
# IMPORTANT:
# - Similarities are semantic evidence/features only.
# - Similarities are NOT final 1-5 interview scores.
# - No human annotation label is used here.
# - No adaptive threshold is assigned here.
# ============================================================

import re
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
# SENTENCE CONCEPT EVALUATOR
# ============================================================

class SentenceConceptEvaluator:

    def __init__(self):

        self.embedder = get_shared_minilm_embedder()


    # --------------------------------------------------------
    # Sentence splitting
    # --------------------------------------------------------

    @staticmethod
    def split_sentences(text):

        if not text:
            return []

        text = str(text).strip()

        if not text:
            return []

        sentences = re.split(
            r'(?<=[.!?])\s+',
            text
        )

        return [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]


    # --------------------------------------------------------
    # Evaluation
    # --------------------------------------------------------

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
                "status": "QUESTION_ID_MISSING"
            }


        question_id = str(
            question_id
        ).strip()


        if not question_id:

            return {
                "success": False,
                "status": "QUESTION_ID_EMPTY"
            }


        # ----------------------------------------------------
        # Validate transcript
        # ----------------------------------------------------

        if transcript is None:

            return {
                "success": False,
                "status": "TRANSCRIPT_MISSING"
            }


        transcript = str(
            transcript
        ).strip()


        if not transcript:

            return {
                "success": False,
                "status": "TRANSCRIPT_EMPTY"
            }


        # ----------------------------------------------------
        # Retrieve semantic reference
        #
        # This now searches the CENTRAL REGISTRY containing
        # all 72 questions from all six roles.
        # ----------------------------------------------------

        reference = get_reference_answer(
            question_id
        )


        if reference is None:

            return {
                "success": False,
                "status": "REFERENCE_NOT_FOUND",
                "question_id": question_id
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
                "question_id": question_id
            }


        # ----------------------------------------------------
        # Split participant response
        # ----------------------------------------------------

        sentences = self.split_sentences(
            transcript
        )


        if not sentences:

            return {
                "success": False,
                "status": "NO_SENTENCES",
                "question_id": question_id
            }


        # ----------------------------------------------------
        # Create one embedding batch
        #
        # This is more efficient than calling the model
        # separately for every sentence/concept pair.
        # ----------------------------------------------------

        all_texts = (
            sentences
            + concepts
        )


        embeddings = self.embedder.encode(
            all_texts
        )


        sentence_count = len(
            sentences
        )


        sentence_embeddings = (
            embeddings[
                :sentence_count
            ]
        )


        concept_embeddings = (
            embeddings[
                sentence_count:
            ]
        )


        concept_results = []


        # ----------------------------------------------------
        # Compare each reference concept against every
        # participant-answer sentence.
        # ----------------------------------------------------

        for concept_index, (
            concept,
            concept_embedding
        ) in enumerate(

            zip(
                concepts,
                concept_embeddings
            ),

            start=1
        ):

            similarities = []


            for sentence_index, (
                sentence,
                sentence_embedding
            ) in enumerate(

                zip(
                    sentences,
                    sentence_embeddings
                ),

                start=1
            ):

                score = cosine_similarity(
                    concept_embedding,
                    sentence_embedding
                )


                similarities.append(
                    {
                        "sentence_number":
                            sentence_index,

                        "sentence":
                            sentence,

                        "similarity":
                            round(
                                float(score),
                                4
                            )
                    }
                )


            best_match = max(
                similarities,
                key=lambda item:
                    item["similarity"]
            )


            concept_results.append(
                {
                    "concept_number":
                        concept_index,

                    "concept":
                        concept,

                    "best_similarity":
                        best_match[
                            "similarity"
                        ],

                    "best_sentence_number":
                        best_match[
                            "sentence_number"
                        ],

                    "best_sentence":
                        best_match[
                            "sentence"
                        ]
                }
            )


        # ----------------------------------------------------
        # Aggregate semantic evidence
        # ----------------------------------------------------

        best_scores = [

            item[
                "best_similarity"
            ]

            for item in concept_results
        ]


        # ----------------------------------------------------
        # Return semantic feature evidence
        # ----------------------------------------------------

        return {

            "success": True,

            "status":
                "SENTENCE_CONCEPT_EVIDENCE_READY",

            "question_id":
                question_id,

            "reference_role":
                reference_role,

            "reference_question":
                reference_question,

            "sentence_count":
                len(sentences),

            "concept_count":
                len(concepts),

            "concept_results":
                concept_results,

            "mean_best_similarity":
                round(
                    float(
                        np.mean(
                            best_scores
                        )
                    ),
                    4
                ),

            "max_best_similarity":
                round(
                    float(
                        np.max(
                            best_scores
                        )
                    ),
                    4
                ),

            "min_best_similarity":
                round(
                    float(
                        np.min(
                            best_scores
                        )
                    ),
                    4
                )
        }


# ============================================================
# DEVELOPMENT TEST
# ============================================================

def main():

    print("=" * 70)

    print(
        "AEGIE MULTI-ROLE SENTENCE-LEVEL "
        "CONCEPT TEST"
    )

    print("=" * 70)


    evaluator = SentenceConceptEvaluator()


    # --------------------------------------------------------
    # IMPORTANT:
    # Test a NON-DATA-SCIENTIST question.
    #
    # CD_E01 belongs to:
    # Cloud DevOps Engineer
    #
    # If this succeeds, it proves the evaluator is using
    # the new central 72-question registry rather than
    # the old Data-Scientist-only reference source.
    # --------------------------------------------------------

    question_id = "CD_E01"


    test_answer = (

        "Cloud computing provides computing resources "
        "and services over the internet. "

        "Organizations can use resources such as "
        "servers, storage, databases and networking "
        "without managing all physical infrastructure "
        "themselves. "

        "These resources can often be provisioned "
        "on demand and scaled according to usage."
    )


    print()

    print(
        "Test question ID:",
        question_id
    )


    result = evaluator.evaluate(
        question_id,
        test_answer
    )


    print()

    print(
        "Status:",
        result.get(
            "status"
        )
    )


    if not result.get(
        "success"
    ):

        print()

        print(
            "FAIL: Semantic evidence "
            "was not generated."
        )

        print(
            result
        )

        return


    # --------------------------------------------------------
    # Registry proof
    # --------------------------------------------------------

    print()

    print(
        "Reference role:",
        result[
            "reference_role"
        ]
    )

    print(
        "Reference question:",
        result[
            "reference_question"
        ]
    )


    print()

    print(
        "Answer sentences:",
        result[
            "sentence_count"
        ]
    )

    print(
        "Reference concepts:",
        result[
            "concept_count"
        ]
    )


    # --------------------------------------------------------
    # Concept evidence
    # --------------------------------------------------------

    print()

    print("-" * 70)

    print(
        "BEST MATCH FOR EACH CONCEPT"
    )

    print("-" * 70)


    for item in result[
        "concept_results"
    ]:

        print()

        print(
            f"Concept "
            f"{item['concept_number']}: "
            f"{item['concept']}"
        )

        print(
            "Best sentence:",
            item[
                "best_sentence"
            ]
        )

        print(
            "Similarity:",
            item[
                "best_similarity"
            ]
        )


    # --------------------------------------------------------
    # Aggregate semantic features
    # --------------------------------------------------------

    print()

    print("-" * 70)

    print(
        "SEMANTIC FEATURES"
    )

    print("-" * 70)


    print(
        "Mean best similarity:",
        result[
            "mean_best_similarity"
        ]
    )


    print(
        "Maximum best similarity:",
        result[
            "max_best_similarity"
        ]
    )


    print(
        "Minimum best similarity:",
        result[
            "min_best_similarity"
        ]
    )


    # --------------------------------------------------------
    # Final development result
    # --------------------------------------------------------

    print()

    print("=" * 70)

    print(
        "PASS: MULTI-ROLE SEMANTIC "
        "EVIDENCE GENERATED"
    )

    print("=" * 70)


    print()

    print(
        "Central registry lookup: PASS"
    )

    print(
        "Question tested: CD_E01"
    )

    print(
        "Expected role: Cloud DevOps Engineer"
    )


    print()

    print(
        "No similarity threshold was applied."
    )

    print(
        "No 1-5 AEGIE score was generated."
    )

    print(
        "No human annotation label was used."
    )

    print(
        "No participant data was modified."
    )


# ============================================================
# RUN DEVELOPMENT TEST
# ============================================================

if __name__ == "__main__":

    main()