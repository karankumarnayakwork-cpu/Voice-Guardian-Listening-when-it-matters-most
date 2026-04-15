from faster_whisper import WhisperModel

# Load once (global for performance)
model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)


def transcribe(audio):
    """
    Convert audio numpy array → text.
    """
    segments, _ = model.transcribe(audio, language="en")

    text_parts = []
    for seg in segments:
        text_parts.append(seg.text)

    text = " ".join(text_parts).strip()
    return text