# ============================================================
# AEGIE TRANSCRIPTION LAYER
# ============================================================
#
# Purpose:
#
# Provide one safe Speech-to-Text interface for AEGIE.
#
# Current STT engine:
#     NVIDIA Parakeet TDT 0.6B V2 INT8
#     through Sherpa-ONNX
#
# Research safeguards:
#
# - Never fabricate a transcript.
# - Preserve the original participant audio when STT fails.
# - Return a clear machine-readable status.
# - Allow later batch transcription if the STT model
#   is unavailable during data collection.
#
# ============================================================

import os


# ============================================================
# PACKAGE-SAFE IMPORT
# ============================================================

try:

    from .parakeet_adapter import (
        transcribe_with_parakeet
    )

except ImportError:

    from parakeet_adapter import (
        transcribe_with_parakeet
    )


# ============================================================
# ENGINE NAME
# ============================================================

DEFAULT_ENGINE = (
    "parakeet-tdt-0.6b-v2-int8"
)


# ============================================================
# RESULT BUILDER
# ============================================================

def _result(
    success,
    status,
    transcript=None,
    engine=None,
    error=None
):

    return {

        "success":
            success,

        "status":
            status,

        "transcript":
            transcript,

        "engine":
            engine,

        "error":
            error
    }


# ============================================================
# CLASSIFY STT FAILURE
# ============================================================

def _classify_stt_error(
    error
):

    if not error:

        return (
            "TRANSCRIPTION_FAILED"
        )


    error_text = str(
        error
    ).lower()


    # --------------------------------------------------------
    # Parakeet model unavailable / incomplete
    # --------------------------------------------------------

    model_keywords = [

        "parakeet model",
        "model is not ready",
        "model is incomplete",
        "missing model",
        "encoder.int8.onnx",
        "decoder.int8.onnx",
        "joiner.int8.onnx",
        "tokens.txt"
    ]


    if any(

        keyword in error_text

        for keyword in model_keywords

    ):

        return (
            "STT_MODEL_UNAVAILABLE"
        )


    # --------------------------------------------------------
    # Sherpa-ONNX / runtime unavailable
    # --------------------------------------------------------

    engine_keywords = [

        "sherpa_onnx",
        "sherpa-onnx",
        "onnxruntime",
        "onnx runtime",
        "no module named",
        "provider"
    ]


    if any(

        keyword in error_text

        for keyword in engine_keywords

    ):

        return (
            "STT_ENGINE_UNAVAILABLE"
        )


    # --------------------------------------------------------
    # FFmpeg / conversion failure
    # --------------------------------------------------------

    conversion_keywords = [

        "ffmpeg",
        "audio conversion",
        "conversion failed",
        "converted wav",
        "16-bit pcm",
        "wav"
    ]


    if any(

        keyword in error_text

        for keyword in conversion_keywords

    ):

        return (
            "AUDIO_CONVERSION_FAILED"
        )


    # --------------------------------------------------------
    # Audio itself invalid
    # --------------------------------------------------------

    audio_keywords = [

        "contains no samples",
        "audio file does not exist",
        "audio path is empty"
    ]


    if any(

        keyword in error_text

        for keyword in audio_keywords

    ):

        return (
            "AUDIO_INVALID"
        )


    return (
        "TRANSCRIPTION_FAILED"
    )


# ============================================================
# MAIN TRANSCRIPTION FUNCTION
# ============================================================

def transcribe_audio(
    audio_path
):
    """
    Main Speech-to-Text interface used by AEGIE.

    Returns:

        {
            "success": bool,
            "status": str,
            "transcript": str | None,
            "engine": str | None,
            "error": str | None
        }

    No transcript is ever fabricated.
    """


    # --------------------------------------------------------
    # Validate audio path
    # --------------------------------------------------------

    if not audio_path:

        return _result(

            success=False,

            status=
                "AUDIO_PATH_MISSING",

            transcript=None,

            engine=None,

            error=
                "Audio path is empty."
        )


    audio_path = str(
        audio_path
    ).strip()


    if not audio_path:

        return _result(

            success=False,

            status=
                "AUDIO_PATH_MISSING",

            transcript=None,

            engine=None,

            error=
                "Audio path is empty."
        )


    # --------------------------------------------------------
    # Audio file must exist
    # --------------------------------------------------------

    if not os.path.exists(
        audio_path
    ):

        return _result(

            success=False,

            status=
                "AUDIO_FILE_NOT_FOUND",

            transcript=None,

            engine=None,

            error=
                "Audio file does not exist."
        )


    # --------------------------------------------------------
    # Run Parakeet safely
    # --------------------------------------------------------

    try:

        stt_result = (
            transcribe_with_parakeet(
                audio_path
            )
        )

    except Exception as error:

        return _result(

            success=False,

            status=
                "TRANSCRIPTION_EXCEPTION",

            transcript=None,

            engine=
                DEFAULT_ENGINE,

            error=
                str(error)
        )


    # --------------------------------------------------------
    # Validate adapter response
    # --------------------------------------------------------

    if not isinstance(
        stt_result,
        dict
    ):

        return _result(

            success=False,

            status=
                "INVALID_STT_RESPONSE",

            transcript=None,

            engine=
                DEFAULT_ENGINE,

            error=(
                "Parakeet adapter returned "
                "an invalid response."
            )
        )


    engine = stt_result.get(
        "engine",
        DEFAULT_ENGINE
    )


    # --------------------------------------------------------
    # Successful Parakeet execution
    # --------------------------------------------------------

    if stt_result.get(
        "success",
        False
    ):

        transcript = (
            stt_result.get(
                "transcript"
            )
        )


        # ----------------------------------------------------
        # STT claimed success but transcript missing
        # ----------------------------------------------------

        if transcript is None:

            return _result(

                success=False,

                status=
                    "TRANSCRIPT_MISSING",

                transcript=None,

                engine=
                    engine,

                error=(
                    "STT reported success "
                    "but returned no transcript."
                )
            )


        transcript = str(
            transcript
        ).strip()


        # ----------------------------------------------------
        # Empty transcript is NOT success
        # ----------------------------------------------------

        if not transcript:

            return _result(

                success=False,

                status=
                    "TRANSCRIPT_EMPTY",

                transcript=None,

                engine=
                    engine,

                error=(
                    "Speech-to-text completed "
                    "but produced an empty transcript."
                )
            )


        # ----------------------------------------------------
        # Genuine transcript ready
        # ----------------------------------------------------

        return _result(

            success=True,

            status=
                "TRANSCRIPTION_READY",

            transcript=
                transcript,

            engine=
                engine,

            error=None
        )


    # --------------------------------------------------------
    # STT unavailable / failed
    #
    # IMPORTANT:
    #
    # Original participant audio is NOT deleted.
    # Transcript remains None.
    # This allows later batch transcription.
    # --------------------------------------------------------

    error = stt_result.get(
        "error",
        "Unknown transcription error."
    )


    status = _classify_stt_error(
        error
    )


    return _result(

        success=False,

        status=
            status,

        transcript=None,

        engine=
            engine,

        error=
            error
    )


# ============================================================
# DEVELOPMENT TEST
# ============================================================

def main():

    print("=" * 72)

    print(
        "AEGIE TRANSCRIPTION LAYER TEST"
    )

    print("=" * 72)


    print()

    print(
        "STT Engine:"
    )

    print(
        "NVIDIA Parakeet TDT "
        "0.6B V2 INT8"
    )


    audio_path = input(
        "\nEnter audio file path: "
    ).strip().strip('"')


    print()

    print(
        "Processing audio..."
    )


    result = transcribe_audio(
        audio_path
    )


    print()

    print("=" * 72)


    print(
        "Success:",
        result[
            "success"
        ]
    )


    print(
        "Status:",
        result[
            "status"
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


    print("=" * 72)


    # --------------------------------------------------------
    # Research safety message
    # --------------------------------------------------------

    if result[
        "success"
    ]:

        print(
            "PASS: Genuine Parakeet STT "
            "transcript was generated."
        )

        print(
            "Original participant audio "
            "was preserved."
        )

    else:

        print(
            "STT transcript was not generated."
        )

        print(
            "Original participant audio "
            "must be preserved."
        )

        print(
            "No transcript was fabricated."
        )


    print("=" * 72)


# ============================================================
# RUN DEVELOPMENT TEST
# ============================================================

if __name__ == "__main__":

    main()