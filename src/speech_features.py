import re


FILLER_PATTERNS = [
    r"\bum\b",
    r"\buh\b",
    r"\ber\b",
    r"\bah\b",
    r"\bhmm\b",
    r"\blike\b",
    r"\byou know\b",
    r"\bi mean\b"
]


def get_word_count(transcript):
    if not transcript:
        return 0

    words = re.findall(
        r"\b[\w'-]+\b",
        transcript
    )

    return len(words)


def get_wpm(word_count, duration_sec):
    if duration_sec is None:
        return None

    try:
        duration_sec = float(duration_sec)
        word_count = int(word_count)
    except (ValueError, TypeError):
        return None

    if duration_sec <= 0:
        return None

    minutes = duration_sec / 60

    wpm = word_count / minutes

    return round(wpm, 2)


def get_filler_count(transcript):
    if not transcript:
        return 0

    text = transcript.lower()

    total = 0

    for pattern in FILLER_PATTERNS:
        matches = re.findall(
            pattern,
            text
        )

        total += len(matches)

    return total


def extract_speech_features(
    transcript,
    duration_sec
):
    word_count = get_word_count(
        transcript
    )

    wpm = get_wpm(
        word_count,
        duration_sec
    )

    filler_count = get_filler_count(
        transcript
    )

    return {
        "word_count": word_count,
        "wpm": wpm,
        "filler_count": filler_count
    }


if __name__ == "__main__":

    transcript = input(
        "Enter test transcript: "
    )

    duration = input(
        "Enter duration in seconds: "
    )

    features = extract_speech_features(
        transcript,
        duration
    )

    print()
    print("AEGIE Speech Features")
    print("----------------------")
    print(
        "Word count:",
        features["word_count"]
    )
    print(
        "WPM:",
        features["wpm"]
    )
    print(
        "Filler count:",
        features["filler_count"]
    )