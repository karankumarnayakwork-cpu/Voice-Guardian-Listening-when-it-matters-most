from .mic import record_audio
from .stt import transcribe
from .intent import detect_intent
from .alarm import play_alarm


def process_audio(duration=3):
    audio = record_audio(duration)
    text = transcribe(audio)

    if not text:
        return None, None

    intent = detect_intent(text)

    if intent in ["threat", "distress"]:
        play_alarm()

    return text, intent