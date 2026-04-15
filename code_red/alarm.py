import winsound
from pathlib import Path

ALARM_PATH = Path(__file__).resolve().parent.parent / "assets" / "alarm.wav"


def play_alarm():
    """
    Play alarm sound using Windows native API.
    Non-blocking.
    """
    
    try:
        winsound.PlaySound(str(ALARM_PATH), winsound.SND_FILENAME | winsound.SND_ASYNC)
    except Exception as e:
        print("Alarm error:", e)