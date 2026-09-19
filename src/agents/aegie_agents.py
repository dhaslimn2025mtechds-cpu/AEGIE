# ============================================================
# AEGIE AGENT ARCHITECTURE
# ============================================================
#
# AEGIE:
# Adaptive Agentic AI-Based Voice Interview Evaluation
#
# Agents:
#
# 1. Interview Agent
# 2. Evaluation Agent
# 3. Adaptive Decision Agent
# 4. Feedback & Reporting Agent
#
# Research rule:
#
# Semantic and speech measurements are research FEATURES.
# They are NOT automatically converted into 1-5 scores.
#
# Human annotations are used to train and validate the
# calibrated AEGIE scoring model.
#
# Runtime 1-5 scores may be generated ONLY when the frozen
# calibrated scoring model exists and successfully predicts.
#
# If the calibrated model is unavailable, AEGIE keeps
# aegie_scores = None and does not fabricate scores.
#
# ============================================================


# ============================================================
# PACKAGE-SAFE IMPORTS
# ============================================================

try:

    from .question_selector import (
        select_question
    )

    from .semantic_evaluator import (
        prepare_semantic_evaluation
    )

    from .evaluation_features import (
        build_evaluation_features
    )

    from .calibrated_scorer import (
        generate_calibrated_scores,
        calibrated_model_exists
    )

except ImportError:

    from question_selector import (
        select_question
    )

    from semantic_evaluator import (
        prepare_semantic_evaluation
    )

    from evaluation_features import (
        build_evaluation_features
    )

    from calibrated_scorer import (
        generate_calibrated_scores,
        calibrated_model_exists
    )


# ============================================================
# 1. INTERVIEW AGENT
# ============================================================

class InterviewAgent:

    def __init__(self):

        self.name = "Interview Agent"


    # ========================================================
    # PROCESS
    # ========================================================

    def process(
        self,
        state
    ):

        print()
        print(
            "[Interview Agent]"
        )


        # ----------------------------------------------------
        # Basic interview state
        # ----------------------------------------------------

        job_role = state.get(
            "job_role"
        )


        question_number = state.get(
            "question_number",
            1
        )


        asked_question_ids = state.get(
            "asked_question_ids",
            []
        )


        target_difficulty = state.get(
            "next_difficulty"
        )


        # ----------------------------------------------------
        # Existing question
        # ----------------------------------------------------

        existing_question = state.get(
            "current_question"
        )


        if existing_question:

            print(
                "Current question already available."
            )

            print(
                "Question ID:",
                existing_question.get(
                    "question_id"
                )
            )

            print(
                "Difficulty:",
                existing_question.get(
                    "difficulty"
                )
            )


            state[
                "interview_agent_status"
            ] = "QUESTION_READY"


            return state


        # ----------------------------------------------------
        # Select question
        # ----------------------------------------------------

        question = select_question(

            job_role=
                job_role,

            question_number=
                question_number,

            asked_question_ids=
                asked_question_ids,

            target_difficulty=
                target_difficulty
        )


        # ----------------------------------------------------
        # No question
        # ----------------------------------------------------

        if question is None:

            if (
                question_number > 1
                and target_difficulty is None
            ):

                print(
                    "Waiting for adaptive "
                    "difficulty decision."
                )

                state[
                    "interview_agent_status"
                ] = (
                    "WAITING_FOR_ADAPTIVE_DECISION"
                )

            else:

                print(
                    "No suitable unused "
                    "question available."
                )

                state[
                    "interview_agent_status"
                ] = (
                    "NO_QUESTION_AVAILABLE"
                )


            return state


        # ----------------------------------------------------
        # Store selected question
        # ----------------------------------------------------

        state[
            "current_question"
        ] = question


        state[
            "current_difficulty"
        ] = question.get(
            "difficulty"
        )


        state[
            "interview_agent_status"
        ] = "QUESTION_READY"


        print(
            "Question selected successfully."
        )

        print(
            "Question ID:",
            question.get(
                "question_id"
            )
        )

        print(
            "Difficulty:",
            question.get(
                "difficulty"
            )
        )

        print(
            "Question:",
            question.get(
                "question_text"
            )
        )


        return state


# ============================================================
# 2. EVALUATION AGENT
# ============================================================

class EvaluationAgent:

    def __init__(self):

        self.name = (
            "Evaluation Agent"
        )


    # ========================================================
    # CLEAR EVALUATION OUTPUT
    # ========================================================

    @staticmethod
    def _clear_evaluation_outputs(
        state
    ):

        state[
            "evaluation_context"
        ] = None

        state[
            "semantic_evidence"
        ] = None

        state[
            "evaluation_features"
        ] = None

        state[
            "aegie_scores"
        ] = None

        state[
            "calibrated_scoring_status"
        ] = None

        state[
            "calibrated_scoring_reason"
        ] = None


    # ========================================================
    # PROCESS
    # ========================================================

    def process(
        self,
        state
    ):

        print()
        print(
            "[Evaluation Agent]"
        )


        # ----------------------------------------------------
        # Transcript required
        # ----------------------------------------------------

        transcript = state.get(
            "transcript"
        )


        if (
            transcript is None
            or not str(
                transcript
            ).strip()
        ):

            print(
                "Transcript is not available."
            )

            print(
                "Waiting for speech-to-text."
            )


            state[
                "evaluation_status"
            ] = "WAITING_FOR_TRANSCRIPT"


            self._clear_evaluation_outputs(
                state
            )


            return state


        # ----------------------------------------------------
        # Current question required
        # ----------------------------------------------------

        current_question = state.get(
            "current_question"
        )


        if not current_question:

            print(
                "Current question is not available."
            )


            state[
                "evaluation_status"
            ] = "WAITING_FOR_QUESTION"


            self._clear_evaluation_outputs(
                state
            )


            return state


        # ----------------------------------------------------
        # Question ID required
        # ----------------------------------------------------

        question_id = (
            current_question.get(
                "question_id"
            )
        )


        if not question_id:

            print(
                "Question ID is missing."
            )


            state[
                "evaluation_status"
            ] = "QUESTION_ID_MISSING"


            self._clear_evaluation_outputs(
                state
            )


            return state


        # ----------------------------------------------------
        # Generate complete semantic evidence
        #
        # This now uses:
        #
        # - Central 72-question registry
        # - Whole-answer MiniLM evidence
        # - Sentence-level MiniLM evidence
        #
        # No human score labels are used at runtime.
        # ----------------------------------------------------

        print(
            "Generating complete semantic "
            "evaluation evidence..."
        )


        try:

            semantic_result = (
                prepare_semantic_evaluation(
                    state,
                    generate_semantic_evidence=True
                )
            )

        except Exception as error:

            print(
                "Semantic evaluation failed."
            )

            print(
                "Reason:",
                str(error)
            )


            state[
                "evaluation_status"
            ] = (
                "SEMANTIC_EVALUATION_ERROR"
            )


            self._clear_evaluation_outputs(
                state
            )


            return state


        # ----------------------------------------------------
        # Semantic evaluation unsuccessful
        # ----------------------------------------------------

        if not semantic_result.get(
            "ready",
            False
        ):

            status = (
                semantic_result.get(
                    "status",
                    "SEMANTIC_EVALUATION_FAILED"
                )
            )


            reason = (
                semantic_result.get(
                    "reason"
                )
            )


            print(
                "Semantic evidence "
                "was not generated."
            )

            print(
                "Status:",
                status
            )

            print(
                "Reason:",
                reason
            )


            state[
                "evaluation_status"
            ] = status


            state[
                "evaluation_context"
            ] = semantic_result.get(
                "evaluation_context"
            )


            state[
                "semantic_evidence"
            ] = semantic_result.get(
                "semantic_evidence"
            )


            state[
                "evaluation_features"
            ] = None


            state[
                "aegie_scores"
            ] = None


            state[
                "calibrated_scoring_status"
            ] = None


            state[
                "calibrated_scoring_reason"
            ] = None


            return state


        # ----------------------------------------------------
        # Store semantic evaluation context
        # ----------------------------------------------------

        state[
            "evaluation_context"
        ] = semantic_result.get(
            "evaluation_context"
        )


        # ----------------------------------------------------
        # Store complete semantic evidence
        # ----------------------------------------------------

        semantic_evidence = (
            semantic_result.get(
                "semantic_evidence"
            )
        )


        state[
            "semantic_evidence"
        ] = semantic_evidence


        state[
            "evaluation_model"
        ] = (
            "sentence-transformers/"
            "all-MiniLM-L6-v2-ONNX"
        )


        print(
            "Semantic evidence generated."
        )


        print(
            "Question ID:",
            question_id
        )


        # ----------------------------------------------------
        # Reference role
        # ----------------------------------------------------

        reference_role = None


        if isinstance(
            semantic_evidence,
            dict
        ):

            reference_role = (
                semantic_evidence.get(
                    "reference_role"
                )
            )


        print(
            "Reference role:",
            reference_role
        )


        # ----------------------------------------------------
        # Whole-answer evidence
        # ----------------------------------------------------

        whole_answer = {}


        if isinstance(
            semantic_evidence,
            dict
        ):

            whole_answer = (
                semantic_evidence.get(
                    "whole_answer"
                )
                or {}
            )


        print()

        print(
            "Whole-answer semantic evidence:"
        )


        print(
            "  Mean similarity:",
            whole_answer.get(
                "mean_similarity"
            )
        )


        print(
            "  Maximum similarity:",
            whole_answer.get(
                "max_similarity"
            )
        )


        print(
            "  Minimum similarity:",
            whole_answer.get(
                "min_similarity"
            )
        )


        # ----------------------------------------------------
        # Sentence-level evidence
        # ----------------------------------------------------

        sentence_level = {}


        if isinstance(
            semantic_evidence,
            dict
        ):

            sentence_level = (
                semantic_evidence.get(
                    "sentence_level"
                )
                or {}
            )


        print()

        print(
            "Sentence-level semantic evidence:"
        )


        print(
            "  Answer sentences:",
            sentence_level.get(
                "sentence_count"
            )
        )


        print(
            "  Mean best similarity:",
            sentence_level.get(
                "mean_best_similarity"
            )
        )


        print(
            "  Maximum best similarity:",
            sentence_level.get(
                "max_best_similarity"
            )
        )


        print(
            "  Minimum best similarity:",
            sentence_level.get(
                "min_best_similarity"
            )
        )


        # ----------------------------------------------------
        # Build combined evaluation feature vector
        # ----------------------------------------------------

        print()

        print(
            "Building combined evaluation "
            "feature vector..."
        )


        try:

            feature_result = (
                build_evaluation_features(
                    state
                )
            )

        except Exception as error:

            print(
                "Evaluation feature "
                "generation failed."
            )

            print(
                "Reason:",
                str(error)
            )


            state[
                "evaluation_status"
            ] = (
                "FEATURE_GENERATION_ERROR"
            )


            state[
                "evaluation_features"
            ] = None


            state[
                "aegie_scores"
            ] = None


            state[
                "calibrated_scoring_status"
            ] = None


            state[
                "calibrated_scoring_reason"
            ] = None


            return state


        # ----------------------------------------------------
        # Feature generation unsuccessful
        # ----------------------------------------------------

        if not feature_result.get(
            "success",
            False
        ):

            print(
                "Evaluation feature vector "
                "was not generated."
            )


            print(
                "Status:",
                feature_result.get(
                    "status"
                )
            )


            print(
                "Reason:",
                feature_result.get(
                    "reason"
                )
            )


            state[
                "evaluation_status"
            ] = feature_result.get(
                "status",
                "FEATURE_GENERATION_FAILED"
            )


            state[
                "evaluation_features"
            ] = None


            state[
                "aegie_scores"
            ] = None


            state[
                "calibrated_scoring_status"
            ] = None


            state[
                "calibrated_scoring_reason"
            ] = None


            return state


        # ----------------------------------------------------
        # Store combined feature vector
        # ----------------------------------------------------

        features = (
            feature_result.get(
                "features"
            )
        )


        state[
            "evaluation_features"
        ] = features


        # IMPORTANT:
        # Keep this status as EVALUATION_FEATURES_READY even if
        # calibrated scores are also generated later. app.py
        # uses this status to persist the feature record.
        state[
            "evaluation_status"
        ] = "EVALUATION_FEATURES_READY"


        print(
            "Evaluation feature vector generated."
        )


        # ----------------------------------------------------
        # Whole-answer features
        # ----------------------------------------------------

        print()

        print(
            "Whole Mean:",
            features.get(
                "whole_mean_similarity"
            )
        )


        print(
            "Whole Maximum:",
            features.get(
                "whole_max_similarity"
            )
        )


        print(
            "Whole Minimum:",
            features.get(
                "whole_min_similarity"
            )
        )


        # ----------------------------------------------------
        # Sentence-level features
        # ----------------------------------------------------

        print()

        print(
            "Sentence Mean Best:",
            features.get(
                "sentence_mean_best_similarity"
            )
        )


        print(
            "Sentence Maximum Best:",
            features.get(
                "sentence_max_best_similarity"
            )
        )


        print(
            "Sentence Minimum Best:",
            features.get(
                "sentence_min_best_similarity"
            )
        )


        # ----------------------------------------------------
        # Semantic structure
        # ----------------------------------------------------

        print()

        print(
            "Reference Concept Count:",
            features.get(
                "reference_concept_count"
            )
        )


        print(
            "Answer Sentence Count:",
            features.get(
                "answer_sentence_count"
            )
        )


        # ----------------------------------------------------
        # Objective speech features
        # ----------------------------------------------------

        print()

        print(
            "Duration:",
            features.get(
                "duration_sec"
            )
        )


        print(
            "Word Count:",
            features.get(
                "word_count"
            )
        )


        print(
            "WPM:",
            features.get(
                "wpm"
            )
        )


        print(
            "Filler Count:",
            features.get(
                "filler_count"
            )
        )


        print(
            "Pause Count:",
            features.get(
                "pause_count"
            )
        )


        print(
            "Filler Rate / 100 Words:",
            features.get(
                "filler_rate_per_100_words"
            )
        )


        print(
            "Pause Rate / Minute:",
            features.get(
                "pause_rate_per_minute"
            )
        )


        # ----------------------------------------------------
        # CALIBRATED AEGIE SCORING
        #
        # IMPORTANT RESEARCH RULE:
        #
        # The feature vector is NEVER converted using arbitrary
        # hand-written thresholds.
        #
        # generate_calibrated_scores() returns scores only when
        # the frozen pilot-trained calibrated model exists.
        #
        # Before calibration:
        #     aegie_scores = None
        #
        # After valid calibration:
        #     aegie_scores = five model predictions clipped
        #     to the approved 1-5 scale.
        # ----------------------------------------------------

        try:

            scoring_result = (
                generate_calibrated_scores(
                    features
                )
            )

        except Exception as error:

            scoring_result = {

                "success":
                    False,

                "status":
                    "CALIBRATED_SCORING_ERROR",

                "reason":
                    str(error),

                "scores":
                    None
            }


        state[
            "calibrated_scoring_status"
        ] = scoring_result.get(
            "status"
        )


        state[
            "calibrated_scoring_reason"
        ] = scoring_result.get(
            "reason"
        )


        print()

        print(
            "AEGIE 1-5 scores:"
        )


        if scoring_result.get(
            "success",
            False
        ):

            scores = scoring_result.get(
                "scores"
            )


            if isinstance(
                scores,
                dict
            ):

                state[
                    "aegie_scores"
                ] = scores


                print(
                    "Calibrated scores generated."
                )


                print(
                    "Relevance:",
                    scores.get(
                        "relevance_score"
                    )
                )


                print(
                    "Technical:",
                    scores.get(
                        "technical_score"
                    )
                )


                print(
                    "Clarity:",
                    scores.get(
                        "clarity_score"
                    )
                )


                print(
                    "Communication:",
                    scores.get(
                        "communication_score"
                    )
                )


                print(
                    "Overall:",
                    scores.get(
                        "overall_score"
                    )
                )

            else:

                state[
                    "aegie_scores"
                ] = None


                state[
                    "calibrated_scoring_status"
                ] = (
                    "CALIBRATED_SCORING_INVALID_OUTPUT"
                )


                state[
                    "calibrated_scoring_reason"
                ] = (
                    "Scoring result reported success "
                    "without a valid score dictionary."
                )


                print(
                    "Not generated - calibrated "
                    "scoring returned invalid output."
                )

        else:

            state[
                "aegie_scores"
            ] = None


            scoring_status = (
                scoring_result.get(
                    "status"
                )
            )


            if (
                scoring_status
                ==
                "CALIBRATION_MODEL_NOT_AVAILABLE"
            ):

                print(
                    "Not generated - "
                    "calibration pending."
                )

            else:

                print(
                    "Not generated - calibrated "
                    "scoring unavailable."
                )


                print(
                    "Status:",
                    scoring_status
                )


                reason = (
                    scoring_result.get(
                        "reason"
                    )
                )


                if reason:

                    print(
                        "Reason:",
                        reason
                    )


        return state


# ============================================================
# 3. ADAPTIVE DECISION AGENT
# ============================================================

class AdaptiveDecisionAgent:

    def __init__(self):

        self.name = (
            "Adaptive Decision Agent"
        )


    # ========================================================
    # PROCESS
    # ========================================================

    def process(
        self,
        state
    ):

        print()
        print(
            "[Adaptive Decision Agent]"
        )


        scores = state.get(
            "aegie_scores"
        )


        features = state.get(
            "evaluation_features"
        )


        # ----------------------------------------------------
        # Features exist, calibrated scores do not
        # ----------------------------------------------------

        if scores is None:

            if features:

                print(
                    "Evaluation features are available."
                )

                print(
                    "Final calibrated AEGIE "
                    "scores are not available."
                )

                print(
                    "Adaptive difficulty decision "
                    "will not be fabricated."
                )


                state[
                    "adaptive_status"
                ] = (
                    "WAITING_FOR_CALIBRATED_EVALUATION"
                )

            else:

                print(
                    "No valid evaluation "
                    "features available."
                )

                print(
                    "Adaptive decision skipped."
                )


                state[
                    "adaptive_status"
                ] = (
                    "WAITING_FOR_EVALUATION"
                )


            state[
                "next_difficulty"
            ] = None


            return state


        # ----------------------------------------------------
        # Calibrated scores exist, but the adaptive difficulty
        # policy itself has not yet been scientifically frozen.
        #
        # Do not invent Easy / Medium / Hard score thresholds.
        # ----------------------------------------------------

        print(
            "Valid calibrated evaluation scores "
            "are available."
        )


        print(
            "Adaptive rule has not "
            "been calibrated yet."
        )


        state[
            "adaptive_status"
        ] = (
            "ADAPTATION_NOT_CALIBRATED"
        )


        state[
            "next_difficulty"
        ] = None


        return state


# ============================================================
# 4. FEEDBACK & REPORTING AGENT
# ============================================================

class FeedbackReportingAgent:

    def __init__(self):

        self.name = (
            "Feedback & Reporting Agent"
        )


    # ========================================================
    # PROCESS
    # ========================================================

    def process(
        self,
        state
    ):

        print()
        print(
            "[Feedback & Reporting Agent]"
        )


        scores = state.get(
            "aegie_scores"
        )


        features = state.get(
            "evaluation_features"
        )


        # ----------------------------------------------------
        # No calibrated scores
        # ----------------------------------------------------

        if scores is None:

            if features:

                print(
                    "Evaluation features are available."
                )

                print(
                    "Calibrated evaluation scores "
                    "are not available."
                )

                print(
                    "Final feedback generation "
                    "is postponed."
                )


                state[
                    "feedback_status"
                ] = (
                    "WAITING_FOR_CALIBRATED_EVALUATION"
                )

            else:

                print(
                    "No evaluation features available."
                )

                print(
                    "Feedback generation skipped."
                )


                state[
                    "feedback_status"
                ] = (
                    "WAITING_FOR_EVALUATION"
                )


            state[
                "feedback"
            ] = None


            return state


        # ----------------------------------------------------
        # Reporting implemented later
        # ----------------------------------------------------

        state[
            "feedback_status"
        ] = (
            "REPORTING_NOT_IMPLEMENTED"
        )


        state[
            "feedback"
        ] = None


        print(
            "Calibrated evaluation is available, "
            "but reporting is not implemented yet."
        )


        return state


# ============================================================
# COMPLETE AEGIE PIPELINE
# ============================================================

class AEGIEAgentPipeline:

    def __init__(self):

        self.interview_agent = (
            InterviewAgent()
        )


        self.evaluation_agent = (
            EvaluationAgent()
        )


        self.adaptive_agent = (
            AdaptiveDecisionAgent()
        )


        self.feedback_agent = (
            FeedbackReportingAgent()
        )


    # ========================================================
    # RUN
    # ========================================================

    def run(
        self,
        state
    ):

        print()
        print("=" * 70)
        print("AEGIE AGENT PIPELINE")
        print("=" * 70)


        # ----------------------------------------------------
        # Interview Agent
        # ----------------------------------------------------

        state = (
            self.interview_agent.process(
                state
            )
        )


        # ----------------------------------------------------
        # Evaluation Agent
        # ----------------------------------------------------

        state = (
            self.evaluation_agent.process(
                state
            )
        )


        # ----------------------------------------------------
        # Adaptive Decision Agent
        # ----------------------------------------------------

        state = (
            self.adaptive_agent.process(
                state
            )
        )


        # ----------------------------------------------------
        # Feedback & Reporting Agent
        # ----------------------------------------------------

        state = (
            self.feedback_agent.process(
                state
            )
        )


        # ----------------------------------------------------
        # Pipeline summary
        # ----------------------------------------------------

        print()
        print("-" * 70)
        print("PIPELINE STATUS SUMMARY")
        print("-" * 70)


        print(
            "Interview Agent:",
            state.get(
                "interview_agent_status"
            )
        )


        print(
            "Evaluation Agent:",
            state.get(
                "evaluation_status"
            )
        )


        print(
            "Calibrated Scoring:",
            state.get(
                "calibrated_scoring_status"
            )
        )


        print(
            "Adaptive Agent:",
            state.get(
                "adaptive_status"
            )
        )


        print(
            "Feedback Agent:",
            state.get(
                "feedback_status"
            )
        )


        print()

        print(
            "AEGIE calibrated scores:",
            state.get(
                "aegie_scores"
            )
        )


        print(
            "Next difficulty:",
            state.get(
                "next_difficulty"
            )
        )


        print()

        print("=" * 70)
        print("PIPELINE COMPLETE")
        print("=" * 70)


        return state


# ============================================================
# DEVELOPMENT TEST
# ============================================================

def main():

    print("=" * 70)

    print(
        "AEGIE COMPLETE AGENT "
        "INTEGRATION TEST"
    )

    print("=" * 70)


    # --------------------------------------------------------
    # DEVELOPMENT-ONLY STATE
    #
    # Uses an already selected Cybersecurity question.
    # This prevents the test from depending on random
    # question selection.
    #
    # This is NOT participant research data.
    # --------------------------------------------------------

    development_state = {

        "participant_id":
            "DEV_TEST",

        "job_role":
            "Cybersecurity Analyst",

        "question_number":
            1,

        "asked_question_ids":
            [],

        "next_difficulty":
            None,


        "current_question": {

            "question_id":
                "CS_E02",

            "question_text":
                (
                    "What is the difference between "
                    "authentication and authorization?"
                ),

            "difficulty":
                "Easy"
        },


        "current_difficulty":
            "Easy",


        "transcript": (

            "Authentication verifies the identity "
            "of a user. "

            "A password or another authentication "
            "factor can help verify who the user is. "

            "Authorization determines what an "
            "authenticated user is permitted to "
            "access or perform. "

            "For example, an administrator can have "
            "permissions that a normal user does not."
        ),


        "duration_sec":
            20.0,

        "word_count":
            43,

        "wpm":
            129.0,

        "filler_count":
            1,

        "pause_count":
            2,


        "evaluation_context":
            None,

        "semantic_evidence":
            None,

        "evaluation_features":
            None,

        "aegie_scores":
            None,

        "calibrated_scoring_status":
            None,

        "calibrated_scoring_reason":
            None,

        "feedback":
            None
    }


    # --------------------------------------------------------
    # Run complete pipeline
    # --------------------------------------------------------

    pipeline = (
        AEGIEAgentPipeline()
    )


    final_state = (
        pipeline.run(
            development_state
        )
    )


    # --------------------------------------------------------
    # Development assertions
    #
    # This test is intentionally valid BOTH:
    #
    # 1. Before a calibrated scoring model exists.
    # 2. After a calibrated scoring model exists.
    #
    # It never creates a fake scoring artifact.
    # --------------------------------------------------------

    print()
    print("-" * 70)
    print("INTEGRATION CHECK")
    print("-" * 70)


    model_is_ready = (
        calibrated_model_exists()
    )


    if model_is_ready:

        scoring_gate_valid = (
            isinstance(
                final_state.get(
                    "aegie_scores"
                ),
                dict
            )
            and
            final_state.get(
                "calibrated_scoring_status"
            )
            ==
            "CALIBRATED_SCORES_READY"
        )


        adaptive_gate_valid = (
            final_state.get(
                "adaptive_status"
            )
            ==
            "ADAPTATION_NOT_CALIBRATED"
        )


        feedback_gate_valid = (
            final_state.get(
                "feedback_status"
            )
            ==
            "REPORTING_NOT_IMPLEMENTED"
        )

    else:

        scoring_gate_valid = (
            final_state.get(
                "aegie_scores"
            )
            is None
            and
            final_state.get(
                "calibrated_scoring_status"
            )
            ==
            "CALIBRATION_MODEL_NOT_AVAILABLE"
        )


        adaptive_gate_valid = (
            final_state.get(
                "adaptive_status"
            )
            ==
            "WAITING_FOR_CALIBRATED_EVALUATION"
        )


        feedback_gate_valid = (
            final_state.get(
                "feedback_status"
            )
            ==
            "WAITING_FOR_CALIBRATED_EVALUATION"
        )


    checks = {

        "Question ready":
            (
                final_state.get(
                    "interview_agent_status"
                )
                == "QUESTION_READY"
            ),

        "Evaluation features ready":
            (
                final_state.get(
                    "evaluation_status"
                )
                == "EVALUATION_FEATURES_READY"
            ),

        "Semantic evidence present":
            isinstance(
                final_state.get(
                    "semantic_evidence"
                ),
                dict
            ),

        "Feature vector present":
            isinstance(
                final_state.get(
                    "evaluation_features"
                ),
                dict
            ),

        "Calibrated scoring gate valid":
            scoring_gate_valid,

        "Adaptive calibration gate valid":
            adaptive_gate_valid,

        "No fabricated next difficulty":
            (
                final_state.get(
                    "next_difficulty"
                )
                is None
            ),

        "Feedback calibration gate valid":
            feedback_gate_valid
    }


    all_passed = True


    for check_name, passed in (
        checks.items()
    ):

        if passed:

            label = "PASS"

        else:

            label = "FAIL"

            all_passed = False


        print(
            f"[{label}] {check_name}"
        )


    print()
    print("=" * 70)


    if all_passed:

        print(
            "PASS: COMPLETE AEGIE "
            "AGENT INTEGRATION IS READY"
        )

    else:

        print(
            "CHECK: ONE OR MORE AEGIE "
            "INTEGRATION TESTS FAILED"
        )


    print("=" * 70)


    print()

    print(
        "This development test did not "
        "modify participant data."
    )

    print(
        "No development record was added "
        "to the 3000-sample research dataset."
    )

    print(
        "No human annotation label was used "
        "as a runtime predictive input."
    )


    if model_is_ready:

        print(
            "AEGIE scores were generated only "
            "by the existing calibrated model."
        )

    else:

        print(
            "No arbitrary 1-5 score was created."
        )


    print(
        "No arbitrary adaptive threshold "
        "was created."
    )


# ============================================================
# RUN DEVELOPMENT TEST
# ============================================================

if __name__ == "__main__":

    main()
