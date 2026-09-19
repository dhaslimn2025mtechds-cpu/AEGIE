# ============================================================
# AEGIE MINILM ONNX EMBEDDING ENGINE
# ============================================================
#
# Model:
# sentence-transformers/all-MiniLM-L6-v2
#
# Runtime:
# ONNX Runtime - CPU
#
# No PyTorch required.
# No Sentence Transformers required.
#
# Pipeline:
#
# Text
#   ↓
# Tokenizer
#   ↓
# ONNX MiniLM
#   ↓
# Last Hidden State
#   ↓
# Mean Pooling
#   ↓
# L2 Normalization
#   ↓
# 384-dimensional sentence embedding
#
# ============================================================

import os

import numpy as np
import onnxruntime as ort

from tokenizers import Tokenizer


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".."
    )
)


MODEL_DIR = os.path.join(
    PROJECT_ROOT,
    "models",
    "semantic_minilm"
)


MODEL_PATH = os.path.join(
    MODEL_DIR,
    "model.onnx"
)


TOKENIZER_PATH = os.path.join(
    MODEL_DIR,
    "tokenizer.json"
)


# ============================================================
# MINILM EMBEDDER
# ============================================================

class MiniLMEmbedder:

    def __init__(self):

        print(
            "Loading MiniLM ONNX semantic model..."
        )


        # ----------------------------------------------------
        # Check files
        # ----------------------------------------------------

        if not os.path.exists(
            MODEL_PATH
        ):

            raise FileNotFoundError(
                f"Model not found: {MODEL_PATH}"
            )


        if not os.path.exists(
            TOKENIZER_PATH
        ):

            raise FileNotFoundError(
                f"Tokenizer not found: {TOKENIZER_PATH}"
            )


        # ----------------------------------------------------
        # Load tokenizer
        # ----------------------------------------------------

        self.tokenizer = (
            Tokenizer.from_file(
                TOKENIZER_PATH
            )
        )


        # Truncate long interview responses.
        self.tokenizer.enable_truncation(
            max_length=256
        )


        # Dynamic batch padding.
        self.tokenizer.enable_padding()


        # ----------------------------------------------------
        # Load ONNX model
        # ----------------------------------------------------

        self.session = (
            ort.InferenceSession(
                MODEL_PATH,
                providers=[
                    "CPUExecutionProvider"
                ]
            )
        )


        # ----------------------------------------------------
        # Detect model input names
        # ----------------------------------------------------

        self.input_names = {

            item.name

            for item in
            self.session.get_inputs()
        }


        print(
            "MiniLM model loaded successfully."
        )

        print(
            "Provider:",
            self.session.get_providers()
        )


    # ========================================================
    # TOKENIZE
    # ========================================================

    def _tokenize(self, texts):

        encodings = (
            self.tokenizer.encode_batch(
                texts
            )
        )


        input_ids = np.array(
            [
                encoding.ids
                for encoding in encodings
            ],
            dtype=np.int64
        )


        attention_mask = np.array(
            [
                encoding.attention_mask
                for encoding in encodings
            ],
            dtype=np.int64
        )


        token_type_ids = np.array(
            [
                encoding.type_ids
                for encoding in encodings
            ],
            dtype=np.int64
        )


        inputs = {}


        if "input_ids" in self.input_names:

            inputs[
                "input_ids"
            ] = input_ids


        if "attention_mask" in self.input_names:

            inputs[
                "attention_mask"
            ] = attention_mask


        if "token_type_ids" in self.input_names:

            inputs[
                "token_type_ids"
            ] = token_type_ids


        return (
            inputs,
            attention_mask
        )


    # ========================================================
    # MEAN POOLING
    # ========================================================

    @staticmethod
    def _mean_pooling(
        token_embeddings,
        attention_mask
    ):

        mask = np.expand_dims(
            attention_mask,
            axis=-1
        ).astype(
            np.float32
        )


        masked_embeddings = (
            token_embeddings
            * mask
        )


        summed = np.sum(
            masked_embeddings,
            axis=1
        )


        counts = np.sum(
            mask,
            axis=1
        )


        counts = np.clip(
            counts,
            1e-9,
            None
        )


        return summed / counts


    # ========================================================
    # L2 NORMALIZATION
    # ========================================================

    @staticmethod
    def _normalize(
        embeddings
    ):

        norms = np.linalg.norm(
            embeddings,
            axis=1,
            keepdims=True
        )


        norms = np.clip(
            norms,
            1e-12,
            None
        )


        return embeddings / norms


    # ========================================================
    # ENCODE
    # ========================================================

    def encode(
        self,
        texts
    ):

        # ----------------------------------------------------
        # Accept one string or list
        # ----------------------------------------------------

        if isinstance(
            texts,
            str
        ):

            texts = [texts]


        if not texts:

            raise ValueError(
                "No text supplied for embedding."
            )


        # ----------------------------------------------------
        # Validate text
        # ----------------------------------------------------

        cleaned_texts = []


        for text in texts:

            if text is None:

                raise ValueError(
                    "Text cannot be None."
                )


            text = str(
                text
            ).strip()


            if not text:

                raise ValueError(
                    "Text cannot be empty."
                )


            cleaned_texts.append(
                text
            )


        # ----------------------------------------------------
        # Tokenize
        # ----------------------------------------------------

        inputs, attention_mask = (
            self._tokenize(
                cleaned_texts
            )
        )


        # ----------------------------------------------------
        # ONNX inference
        # ----------------------------------------------------

        outputs = self.session.run(
            None,
            inputs
        )


        # Model output:
        #
        # [batch, sequence_length, 384]

        token_embeddings = (
            outputs[0]
        )


        # ----------------------------------------------------
        # Mean pooling
        # ----------------------------------------------------

        sentence_embeddings = (
            self._mean_pooling(
                token_embeddings,
                attention_mask
            )
        )


        # ----------------------------------------------------
        # Normalize
        # ----------------------------------------------------

        sentence_embeddings = (
            self._normalize(
                sentence_embeddings
            )
        )


        return sentence_embeddings


# ============================================================
# COSINE SIMILARITY
# ============================================================

def cosine_similarity(
    embedding_a,
    embedding_b
):

    a = np.asarray(
        embedding_a
    ).reshape(-1)


    b = np.asarray(
        embedding_b
    ).reshape(-1)


    denominator = (
        np.linalg.norm(a)
        * np.linalg.norm(b)
    )


    if denominator == 0:

        return 0.0


    similarity = (
        np.dot(a, b)
        / denominator
    )


    return float(
        similarity
    )



# ============================================================
# SHARED MINILM EMBEDDER
# ============================================================
#
# The concept-level and sentence-level evaluators both use
# the same ONNX MiniLM model. Reusing one embedder avoids
# loading the same model twice inside a Flask process.
#
# ============================================================

_SHARED_MINILM_EMBEDDER = None


def get_shared_minilm_embedder():

    global _SHARED_MINILM_EMBEDDER

    if _SHARED_MINILM_EMBEDDER is None:

        _SHARED_MINILM_EMBEDDER = (
            MiniLMEmbedder()
        )

    return _SHARED_MINILM_EMBEDDER


# ============================================================
# DEVELOPMENT TEST
# ============================================================

def main():

    print("=" * 65)
    print("AEGIE MINILM EMBEDDING TEST")
    print("=" * 65)


    embedder = MiniLMEmbedder()


    # --------------------------------------------------------
    # Development-only sentences.
    # NOT research participant data.
    # --------------------------------------------------------

    reference = (
        "Overfitting happens when a machine learning "
        "model learns the training data too closely "
        "and performs poorly on unseen data."
    )


    similar_answer = (
        "A model is overfitting when it performs very "
        "well on training data but fails to generalize "
        "to new unseen examples."
    )


    unrelated_answer = (
        "Cloud computing provides computing resources "
        "such as servers and storage over the internet."
    )


    # --------------------------------------------------------
    # Generate embeddings
    # --------------------------------------------------------

    embeddings = embedder.encode(
        [
            reference,
            similar_answer,
            unrelated_answer
        ]
    )


    print()
    print(
        "Embedding shape:",
        embeddings.shape
    )


    print(
        "Embedding dimension:",
        embeddings.shape[1]
    )


    # --------------------------------------------------------
    # Similarity
    # --------------------------------------------------------

    similar_score = cosine_similarity(
        embeddings[0],
        embeddings[1]
    )


    unrelated_score = cosine_similarity(
        embeddings[0],
        embeddings[2]
    )


    print()
    print(
        "Reference vs Similar Answer:"
    )

    print(
        round(
            similar_score,
            4
        )
    )


    print()
    print(
        "Reference vs Unrelated Answer:"
    )

    print(
        round(
            unrelated_score,
            4
        )
    )


    # --------------------------------------------------------
    # Structural test only
    # --------------------------------------------------------

    print()
    print("-" * 65)


    if (
        embeddings.shape[1] == 384
        and similar_score
        > unrelated_score
    ):

        print(
            "PASS: Semantic embedding "
            "engine is working."
        )

    else:

        print(
            "CHECK: Unexpected semantic "
            "embedding result."
        )


    print()
    print(
        "IMPORTANT:"
    )

    print(
        "Similarity values are semantic "
        "features, NOT final interview scores."
    )

    print(
        "No 1-5 scoring thresholds have "
        "been defined."
    )


    print()
    print("=" * 65)
    print("MINILM TEST COMPLETE")
    print("=" * 65)


if __name__ == "__main__":

    main()