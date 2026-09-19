import os
import onnxruntime as ort


# ============================================================
# PATH
# ============================================================

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

MODEL_PATH = os.path.join(
    PROJECT_ROOT,
    "models",
    "semantic_minilm",
    "model.onnx"
)


# ============================================================
# VALIDATION
# ============================================================

print("=" * 65)
print("AEGIE MINILM ONNX MODEL VALIDATOR")
print("=" * 65)

print()
print("Model path:")
print(MODEL_PATH)


# ------------------------------------------------------------
# File check
# ------------------------------------------------------------

if not os.path.exists(MODEL_PATH):

    print()
    print("FAIL: model.onnx does not exist.")
    raise SystemExit(1)


size_mb = os.path.getsize(MODEL_PATH) / (
    1024 * 1024
)

print()
print(
    "Model size:",
    round(size_mb, 2),
    "MB"
)


if size_mb < 50:

    print()
    print(
        "WARNING: Model file looks "
        "unexpectedly small."
    )


# ------------------------------------------------------------
# ONNX Runtime session
# ------------------------------------------------------------

print()
print("Loading model with ONNX Runtime...")


try:

    session = ort.InferenceSession(
        MODEL_PATH,
        providers=[
            "CPUExecutionProvider"
        ]
    )

except Exception as e:

    print()
    print("FAIL: ONNX model could not be loaded.")
    print()
    print("Error:")
    print(e)

    raise SystemExit(1)


print()
print("PASS: ONNX model loaded successfully.")


# ------------------------------------------------------------
# Provider
# ------------------------------------------------------------

print()
print(
    "Execution providers:",
    session.get_providers()
)


# ------------------------------------------------------------
# Inputs
# ------------------------------------------------------------

print()
print("-" * 65)
print("MODEL INPUTS")
print("-" * 65)


for model_input in session.get_inputs():

    print()
    print(
        "Name:",
        model_input.name
    )

    print(
        "Shape:",
        model_input.shape
    )

    print(
        "Type:",
        model_input.type
    )


# ------------------------------------------------------------
# Outputs
# ------------------------------------------------------------

print()
print("-" * 65)
print("MODEL OUTPUTS")
print("-" * 65)


for model_output in session.get_outputs():

    print()
    print(
        "Name:",
        model_output.name
    )

    print(
        "Shape:",
        model_output.shape
    )

    print(
        "Type:",
        model_output.type
    )


# ------------------------------------------------------------
# Final status
# ------------------------------------------------------------

print()
print("=" * 65)
print("PASS: MINILM ONNX MODEL IS READY")
print("=" * 65)

print()
print(
    "No participant data was processed "
    "during this validation."
)