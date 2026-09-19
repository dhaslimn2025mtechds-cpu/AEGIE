import os
import subprocess
import tempfile
import time
import wave

import numpy as np
import sherpa_onnx


# ============================================================
# AEGIE - PARAKEET TDT 0.6B V2 INT8 REAL RECORDING TEST
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODEL_DIR = os.path.join(
    PROJECT_ROOT,
    "models",
    "sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8"
)

ENCODER = os.path.join(
    MODEL_DIR,
    "encoder.int8.onnx"
)

DECODER = os.path.join(
    MODEL_DIR,
    "decoder.int8.onnx"
)

JOINER = os.path.join(
    MODEL_DIR,
    "joiner.int8.onnx"
)

TOKENS = os.path.join(
    MODEL_DIR,
    "tokens.txt"
)

DEFAULT_AUDIO = os.path.join(
    PROJECT_ROOT,
    "audio",
    "development",
    "pilot_test_archive",
    "PL001",
    "AEGIE_PL001_DS_E01_20260918_141431_667873.webm"
)


# ============================================================
# WEBM -> WAV
# ============================================================

def convert_to_wav(
    input_path,
    output_path
):

    command = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        input_path,
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "pcm_s16le",
        output_path
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=120
    )

    if result.returncode != 0:

        raise RuntimeError(
            "FFmpeg conversion failed: "
            + result.stderr
        )


# ============================================================
# READ WAV
# ============================================================

def read_wav(
    path
):

    with wave.open(
        path,
        "rb"
    ) as wav_file:

        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        sample_rate = wav_file.getframerate()

        frames = wav_file.readframes(
            wav_file.getnframes()
        )

    if sample_width != 2:

        raise RuntimeError(
            "Expected 16-bit PCM WAV."
        )

    samples = np.frombuffer(
        frames,
        dtype=np.int16
    ).astype(
        np.float32
    )

    samples /= 32768.0

    if channels > 1:

        samples = samples.reshape(
            -1,
            channels
        ).mean(
            axis=1
        )

    return (
        samples.astype(np.float32),
        sample_rate
    )


# ============================================================
# CREATE PARAKEET RECOGNIZER
# ============================================================

def create_recognizer():

    return (
        sherpa_onnx
        .OfflineRecognizer
        .from_transducer(

            encoder=ENCODER,

            decoder=DECODER,

            joiner=JOINER,

            tokens=TOKENS,

            num_threads=2,

            decoding_method=
                "greedy_search",

            provider="cpu",

            model_type=
                "nemo_transducer",

            debug=False
        )
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 72)
    print("AEGIE PARAKEET TDT REAL VOICE TEST")
    print("=" * 72)

    audio_path = input(
        "Enter AEGIE audio path "
        "(press Enter for default test recording): "
    ).strip().strip('"')

    if not audio_path:
        audio_path = DEFAULT_AUDIO

    print()
    print("Input audio:")
    print(audio_path)

    if not os.path.exists(
        audio_path
    ):

        print()
        print(
            "FAIL: Audio file does not exist."
        )

        print("=" * 72)
        return


    required_files = [
        ENCODER,
        DECODER,
        JOINER,
        TOKENS
    ]


    for path in required_files:

        if not os.path.exists(
            path
        ):

            print()
            print(
                "FAIL: Missing model file:"
            )

            print(path)
            print("=" * 72)
            return


    print()
    print("Model files: PASS")


    temp_file = tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False
    )

    wav_path = temp_file.name
    temp_file.close()


    try:

        # ----------------------------------------------------
        # Convert browser audio
        # ----------------------------------------------------

        print()
        print(
            "Converting browser WebM audio "
            "to 16 kHz mono WAV..."
        )

        conversion_start = (
            time.perf_counter()
        )

        convert_to_wav(
            audio_path,
            wav_path
        )

        conversion_time = (
            time.perf_counter()
            - conversion_start
        )

        print("Conversion: PASS")

        print(
            "Conversion time:",
            round(
                conversion_time,
                2
            ),
            "seconds"
        )


        # ----------------------------------------------------
        # Load WAV
        # ----------------------------------------------------

        samples, sample_rate = read_wav(
            wav_path
        )

        duration = (
            len(samples)
            / sample_rate
        )

        print()
        print(
            "Sample rate:",
            sample_rate
        )

        print(
            "Audio duration:",
            round(
                duration,
                2
            ),
            "seconds"
        )


        # ----------------------------------------------------
        # Load recognizer
        # ----------------------------------------------------

        print()
        print(
            "Loading Parakeet TDT 0.6B V2 INT8..."
        )

        load_start = (
            time.perf_counter()
        )

        recognizer = (
            create_recognizer()
        )

        load_time = (
            time.perf_counter()
            - load_start
        )

        print(
            "Load time:",
            round(
                load_time,
                2
            ),
            "seconds"
        )


        # ----------------------------------------------------
        # Decode
        # ----------------------------------------------------

        stream = (
            recognizer
            .create_stream()
        )

        stream.accept_waveform(
            sample_rate,
            samples
        )

        print()
        print(
            "Transcribing genuine "
            "AEGIE recording..."
        )

        decode_start = (
            time.perf_counter()
        )

        recognizer.decode_stream(
            stream
        )

        decode_time = (
            time.perf_counter()
            - decode_start
        )

        transcript = (
            stream
            .result
            .text
            .strip()
        )


        # ----------------------------------------------------
        # Result
        # ----------------------------------------------------

        print()
        print("=" * 72)
        print("PARAKEET TRANSCRIPT")
        print("-" * 72)

        print(
            transcript
            if transcript
            else "[EMPTY]"
        )

        print("-" * 72)

        print(
            "Audio duration:",
            round(
                duration,
                2
            ),
            "seconds"
        )

        print(
            "Decode time:",
            round(
                decode_time,
                3
            ),
            "seconds"
        )

        if duration > 0:

            rtf = (
                decode_time
                / duration
            )

            print(
                "Real-time factor:",
                round(
                    rtf,
                    4
                )
            )

        print()

        if transcript:

            print(
                "PASS: PARAKEET TRANSCRIBED "
                "THE REAL AEGIE RECORDING."
            )

        else:

            print(
                "CHECK: Parakeet returned "
                "an empty transcript."
            )

        print()
        print(
            "No dataset row was modified."
        )

        print(
            "No human label was generated."
        )

        print("=" * 72)


    finally:

        if os.path.exists(
            wav_path
        ):

            try:
                os.remove(
                    wav_path
                )
            except Exception:
                pass


if __name__ == "__main__":
    main()