DISTRESS_WORDS = ["help", "save", "please", "emergency"]
THREAT_WORDS = ["kill", "attack", "gun", "fire", "bomb", "code red"]
COMMAND_WORDS = ["open", "close", "unlock", "lock", "security"]


def is_noise(text: str) -> bool:
    """
    Detect meaningless STT outputs.
    """
    if not text:
        return True

    t = text.strip()

    # only punctuation or very short
    if len(t) < 2:
        return True

    if all(c in ".!?," for c in t):
        return True

    return False


def detect_intent(text: str) -> str:
    if is_noise(text):
        return "none"

    t = text.lower()

    if any(w in t for w in DISTRESS_WORDS):
        return "distress"

    if any(w in t for w in THREAT_WORDS):
        return "threat"

    if any(w in t for w in COMMAND_WORDS):
        return "command"

    return "normal"