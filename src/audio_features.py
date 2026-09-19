import subprocess
import os
import re


def get_audio_duration(audio_path):
    """Return audio duration in seconds using ffprobe."""

    if not os.path.exists(audio_path):
        return None

    command = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            return None

        return round(float(result.stdout.strip()), 2)

    except Exception as e:
        print("Duration extraction error:", e)
        return None


def get_pause_count(audio_path):
    """
    Count pauses using FFmpeg silencedetect.

    Current operational definition:
    silence >= 0.5 seconds and below -35 dB = one detected pause.

    These thresholds are provisional for development and
    must be validated before the final research experiment.
    """

    if not os.path.exists(audio_path):
        return None

    command = [
        "ffmpeg",
        "-hide_banner",
        "-i", audio_path,
        "-af", "silencedetect=noise=-35dB:d=0.5",
        "-f", "null",
        "-"
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=60
        )

        output = result.stderr

        pause_starts = re.findall(
            r"silence_start:\s*([0-9.]+)",
            output
        )

        return len(pause_starts)

    except Exception as e:
        print("Pause detection error:", e)
        return None


if __name__ == "__main__":

    path = input(
        "Enter audio file path: "
    ).strip().strip('"')

    duration = get_audio_duration(path)
    pause_count = get_pause_count(path)

    print(f"Audio duration: {duration} seconds")
    print(f"Pause count: {pause_count}")