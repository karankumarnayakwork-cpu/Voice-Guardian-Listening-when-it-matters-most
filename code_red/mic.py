import sounddevice as sd
import numpy as np

SAMPLE_RATE = 16000


def record_audio(duration=3):
    """
    Record audio from default microphone.
    Returns mono float32 numpy array.
    """
    audio = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
    )
    sd.wait()
    return audio.flatten()