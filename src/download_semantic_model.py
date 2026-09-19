import os
import shutil
import truststore

truststore.inject_into_ssl()

from huggingface_hub import hf_hub_download


PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

MODEL_DIR = os.path.join(
    PROJECT_ROOT,
    "models",
    "semantic_minilm"
)

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)


REPO_ID = (
    "sentence-transformers/"
    "all-MiniLM-L6-v2"
)


FILES = {
    "config.json":
        "config.json",

    "tokenizer.json":
        "tokenizer.json",

    "tokenizer_config.json":
        "tokenizer_config.json",

    "special_tokens_map.json":
        "special_tokens_map.json",

    "vocab.txt":
        "vocab.txt",

    "onnx/model.onnx":
        "model.onnx"
}


print("=" * 60)
print("AEGIE MiniLM ONNX MODEL DOWNLOAD")
print("=" * 60)


for remote_file, local_name in FILES.items():

    print()
    print(
        "Downloading:",
        remote_file
    )

    try:

        downloaded_path = hf_hub_download(
            repo_id=REPO_ID,
            filename=remote_file
        )

        destination = os.path.join(
            MODEL_DIR,
            local_name
        )

        shutil.copy2(
            downloaded_path,
            destination
        )

        print(
            "Saved:",
            destination
        )

    except Exception as e:

        print()
        print(
            "DOWNLOAD FAILED:",
            remote_file
        )

        print(
            "Error:",
            e
        )

        raise


print()
print("=" * 60)
print("DOWNLOAD COMPLETE")
print("=" * 60)

print()
print(
    "Model directory:",
    MODEL_DIR
)