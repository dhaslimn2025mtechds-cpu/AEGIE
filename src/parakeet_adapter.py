# ============================================================
# AEGIE PARAKEET STT ADAPTER
# ============================================================
#
# Engine:
#   NVIDIA Parakeet TDT 0.6B V2 INT8
#   through Sherpa-ONNX
#
# Purpose:
#   Browser WebM
#       ↓
#   FFmpeg 16 kHz mono WAV
#       ↓
#   Parakeet TDT
#       ↓
#   Genuine transcript
#
# Research safeguards:
# - No transcript fabrication
# - Original participant audio is never modified/deleted
# - Temporary WAV is deleted after processing
# - Model is loaded lazily and cached
# ============================================================

import os
import subprocess
import tempfile
import threading
import time
import wave

import numpy as np
import sherpa_onnx


# ============================================================
# PATHS
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

ENCODER_PATH = os.path.join(
    MODEL_DIR,
    "encoder.int8.onnx"
)

DECODER_PATH = os.path.join(
    MODEL_DIR,
    "decoder.int8.onnx"
)

JOINER_PATH = os.path.join(
    MODEL_DIR,
    "joiner.int8.onnx"
)

TOKENS_PATH = os.path.join(
    MODEL_DIR,
    "tokens.txt"
)


# ============================================================
# MODEL CACHE
# ============================================================

_RECOGNIZER = None

_MODEL_LOCK = threading.Lock()

_DECODE_LOCK = threading.Lock()


# ============================================================
# MODEL VALIDATION
# ============================================================

def check_parakeet_model():

    required_files = {

        "encoder":
            ENCODER_PATH,

        "decoder":
            DECODER_PATH,

        "joiner":
            JOINER_PATH,

        "tokens":
            TOKENS_PATH
    }

    missing = []

    for name, path in required_files.items():

        if not os.path.exists(path):

            missing.append(
                f"{name}: {path}"
            )

    if missing:

        return {
            "ready": False,
            "missing": missing
        }

    return {
        "ready": True,
        "missing": []
    }


# ============================================================
# CREATE / GET CACHED RECOGNIZER
# ============================================================

def get_recognizer():

    global _RECOGNIZER

    if _RECOGNIZER is not None:

        return _RECOGNIZER


    with _MODEL_LOCK:

        if _RECOGNIZER is not None:

            return _RECOGNIZER


        model_status = (
            check_parakeet_model()
        )


        if not model_status["ready"]:

            raise FileNotFoundError(

                "Parakeet STT model is incomplete. "
                "Missing: "
                + " | ".join(
                    model_status["missing"]
                )
            )


        print()

        print(
            "Loading Parakeet TDT "
            "0.6B V2 INT8 STT model..."
        )


        _RECOGNIZER = (
            sherpa_onnx
            .OfflineRecognizer
            .from_transducer(

                encoder=
                    ENCODER_PATH,

                decoder=
                    DECODER_PATH,

                joiner=
                    JOINER_PATH,

                tokens=
                    TOKENS_PATH,

                num_threads=2,

                decoding_method=
                    "greedy_search",

                provider=
                    "cpu",

                model_type=
                    "nemo_transducer",

                debug=False
            )
        )


        print(
            "Parakeet STT model loaded."
        )


    return _RECOGNIZER


# ============================================================
# AUDIO CONVERSION
# ============================================================

def convert_audio_to_wav(
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


    try:

        result = subprocess.run(

            command,

            capture_output=True,

            text=True,

            timeout=120
        )

    except FileNotFoundError:

        raise RuntimeError(
            "FFmpeg executable was not found."
        )


    if result.returncode != 0:

        raise RuntimeError(

            "FFmpeg audio conversion failed. "
            + result.stderr.strip()
        )


# ============================================================
# WAV READER
# ============================================================

def read_wav(
    wav_path
):

    with wave.open(
        wav_path,
        "rb"
    ) as wav_file:

        channels = (
            wav_file.getnchannels()
        )

        sample_width = (
            wav_file.getsampwidth()
        )

        sample_rate = (
            wav_file.getframerate()
        )

        frame_count = (
            wav_file.getnframes()
        )

        raw_audio = (
            wav_file.readframes(
                frame_count
            )
        )


    if sample_width != 2:

        raise RuntimeError(
            "Converted WAV must be "
            "16-bit PCM audio."
        )


    samples = np.frombuffer(

        raw_audio,

        dtype=np.int16

    ).astype(
        np.float32
    )


    samples /= 32768.0


    if channels > 1:

        samples = samples.reshape(
            -1,
            channels
        )

        samples = samples.mean(
            axis=1
        )


    return (
        samples.astype(
            np.float32
        ),
        sample_rate
    )


# ============================================================
# MAIN TRANSCRIPTION
# ============================================================

def transcribe_with_parakeet(
    audio_path
):

    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    if not audio_path:

        return {

            "success":
                False,

            "transcript":
                None,

            "engine":
                "parakeet-tdt-0.6b-v2-int8",

            "error":
                "Audio path is empty."
        }


    audio_path = str(
        audio_path
    ).strip()


    if not os.path.exists(
        audio_path
    ):

        return {

            "success":
                False,

            "transcript":
                None,

            "engine":
                "parakeet-tdt-0.6b-v2-int8",

            "error":
                "Audio file does not exist."
        }


    # --------------------------------------------------------
    # Validate model
    # --------------------------------------------------------

    model_status = (
        check_parakeet_model()
    )


    if not model_status["ready"]:

        return {

            "success":
                False,

            "transcript":
                None,

            "engine":
                "parakeet-tdt-0.6b-v2-int8",

            "error":
                (
                    "Parakeet model is not ready. "
                    + " | ".join(
                        model_status[
                            "missing"
                        ]
                    )
                )
        }


    # --------------------------------------------------------
    # DEVELOPMENT PERFORMANCE TIMER
    # --------------------------------------------------------
    # Diagnostic only. It does not change the audio,
    # recognizer settings, decoding method, or transcript.

    parakeet_total_start = time.perf_counter()

    timing_conversion = None
    timing_wav_read = None
    timing_recognizer = None
    timing_stream_prepare = None
    timing_decode = None
    timing_result_extract = None


    # --------------------------------------------------------
    # Temporary WAV
    # --------------------------------------------------------

    temp_file = (
        tempfile.NamedTemporaryFile(

            suffix=".wav",

            delete=False
        )
    )


    wav_path = (
        temp_file.name
    )


    temp_file.close()


    try:

        # ----------------------------------------------------
        # Browser audio -> 16 kHz mono WAV
        # ----------------------------------------------------

        conversion_start = time.perf_counter()

        convert_audio_to_wav(

            audio_path,

            wav_path
        )

        timing_conversion = (
            time.perf_counter()
            - conversion_start
        )


        # ----------------------------------------------------
        # Read WAV
        # ----------------------------------------------------

        wav_read_start = time.perf_counter()

        samples, sample_rate = (
            read_wav(
                wav_path
            )
        )

        timing_wav_read = (
            time.perf_counter()
            - wav_read_start
        )


        if len(samples) == 0:

            return {

                "success":
                    False,

                "transcript":
                    None,

                "engine":
                    "parakeet-tdt-0.6b-v2-int8",

                "error":
                    "Converted audio contains no samples."
            }


        # ----------------------------------------------------
        # Recognizer
        # ----------------------------------------------------

        recognizer_start = time.perf_counter()

        recognizer = (
            get_recognizer()
        )

        timing_recognizer = (
            time.perf_counter()
            - recognizer_start
        )


        stream_prepare_start = time.perf_counter()

        stream = (
            recognizer
            .create_stream()
        )


        stream.accept_waveform(

            sample_rate,

            samples
        )

        timing_stream_prepare = (
            time.perf_counter()
            - stream_prepare_start
        )


        # ----------------------------------------------------
        # Decode
        #
        # Lock avoids concurrent access to the same cached
        # recognizer in the Flask development server.
        # ----------------------------------------------------

        decode_start = time.perf_counter()

        with _DECODE_LOCK:

            recognizer.decode_stream(
                stream
            )

        timing_decode = (
            time.perf_counter()
            - decode_start
        )


        result_extract_start = time.perf_counter()

        transcript = (

            stream
            .result
            .text
            .strip()
        )

        timing_result_extract = (
            time.perf_counter()
            - result_extract_start
        )


        # ----------------------------------------------------
        # DEVELOPMENT PERFORMANCE SUMMARY
        # ----------------------------------------------------

        parakeet_total_elapsed = (
            time.perf_counter()
            - parakeet_total_start
        )

        print()
        print("=" * 55)
        print("PARAKEET STT PERFORMANCE")
        print("=" * 55)

        print(
            "FFmpeg WebM -> WAV:",
            f"{timing_conversion:.3f} sec"
        )

        print(
            "WAV loading:",
            f"{timing_wav_read:.3f} sec"
        )

        print(
            "Recognizer retrieval / model load:",
            f"{timing_recognizer:.3f} sec"
        )

        print(
            "Stream preparation:",
            f"{timing_stream_prepare:.3f} sec"
        )

        print(
            "Parakeet decode:",
            f"{timing_decode:.3f} sec"
        )

        print(
            "Result extraction:",
            f"{timing_result_extract:.3f} sec"
        )

        print("-" * 55)

        print(
            "TOTAL PARAKEET ADAPTER:",
            f"{parakeet_total_elapsed:.3f} sec"
        )

        print("=" * 55)


        # ----------------------------------------------------
        # Empty transcript
        # ----------------------------------------------------

        if not transcript:

            return {

                "success":
                    False,

                "transcript":
                    None,

                "engine":
                    "parakeet-tdt-0.6b-v2-int8",

                "error":
                    (
                        "Parakeet completed "
                        "but returned an empty transcript."
                    )
            }


        # ----------------------------------------------------
        # Success
        # ----------------------------------------------------

        return {

            "success":
                True,

            "transcript":
                transcript,

            "engine":
                "parakeet-tdt-0.6b-v2-int8",

            "error":
                None
        }


    except Exception as error:

        return {

            "success":
                False,

            "transcript":
                None,

            "engine":
                "parakeet-tdt-0.6b-v2-int8",

            "error":
                str(error)
        }


    finally:

        # ----------------------------------------------------
        # Delete temporary WAV only.
        #
        # Original WebM recording is preserved.
        # ----------------------------------------------------

        if os.path.exists(
            wav_path
        ):

            try:

                os.remove(
                    wav_path
                )

            except Exception:

                pass


# ============================================================
# DEVELOPMENT TEST
# ============================================================

def main():

    print("=" * 72)

    print(
        "AEGIE PARAKEET STT ADAPTER TEST"
    )

    print("=" * 72)


    audio_path = input(
        "Enter audio path: "
    ).strip().strip('"')


    result = (
        transcribe_with_parakeet(
            audio_path
        )
    )


    print()

    print(
        "Success:",
        result[
            "success"
        ]
    )

    print(
        "Engine:",
        result[
            "engine"
        ]
    )

    print(
        "Transcript:",
        result[
            "transcript"
        ]
    )

    print(
        "Error:",
        result[
            "error"
        ]
    )


    print()

    if result[
        "success"
    ]:

        print(
            "PASS: PARAKEET ADAPTER "
            "GENERATED A TRANSCRIPT."
        )

    else:

        print(
            "FAIL: PARAKEET ADAPTER "
            "DID NOT GENERATE A TRANSCRIPT."
        )


    print("=" * 72)


if __name__ == "__main__":

    main()