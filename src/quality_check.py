def check_audio_quality(duration_sec, pause_count=None):
    """
    Development-stage quality control for AEGIE.

    IMPORTANT:
    The thresholds used here are provisional.
    They must be validated before final research data collection.
    """

    result = {
        "usable": True,
        "status": "PASS",
        "reason": "Audio passed basic quality checks."
    }

    # -----------------------------------------
    # Missing duration
    # -----------------------------------------

    if duration_sec is None or duration_sec == "":
        return {
            "usable": False,
            "status": "FAIL",
            "reason": "Audio duration could not be measured."
        }

    try:
        duration = float(duration_sec)
    except (TypeError, ValueError):
        return {
            "usable": False,
            "status": "FAIL",
            "reason": "Invalid audio duration."
        }

    # -----------------------------------------
    # Empty / corrupted recording
    # -----------------------------------------

    if duration <= 0:
        return {
            "usable": False,
            "status": "FAIL",
            "reason": "Audio recording has zero duration."
        }

    # -----------------------------------------
    # Very short response
    #
    # DEVELOPMENT RULE ONLY.
    # 2 seconds is NOT yet a final research
    # threshold.
    # -----------------------------------------

    if duration < 2:
        return {
            "usable": False,
            "status": "REVIEW",
            "reason": "Recording is extremely short and requires review."
        }

    # -----------------------------------------
    # Validate pause count when available
    # -----------------------------------------

    if pause_count not in (None, ""):

        try:
            pauses = int(pause_count)

            if pauses < 0:
                return {
                    "usable": False,
                    "status": "FAIL",
                    "reason": "Invalid negative pause count."
                }

        except (TypeError, ValueError):
            return {
                "usable": False,
                "status": "FAIL",
                "reason": "Invalid pause count."
            }

    return result


if __name__ == "__main__":

    print("=" * 45)
    print("AEGIE AUDIO QUALITY CHECK")
    print("=" * 45)

    duration = input(
        "Enter test duration in seconds: "
    )

    pauses = input(
        "Enter pause count: "
    )

    result = check_audio_quality(
        duration,
        pauses
    )

    print()
    print("Status:", result["status"])
    print("Usable:", result["usable"])
    print("Reason:", result["reason"])