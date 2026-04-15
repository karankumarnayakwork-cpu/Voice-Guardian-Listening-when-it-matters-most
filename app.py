
"""
VISIO Audio — Streamlit Real-Time Speech Detection Interface
Place this file in the same directory as the `visio_audio` package folder.
Run with: streamlit run app.py
"""

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import streamlit as st
import threading
import queue
import time
from datetime import datetime

# ── Page config (must be first Streamlit call) ──────────────────────────────
st.set_page_config(
    page_title="Code Red",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Rajdhani', sans-serif;
    background-color: #0a0c10;
    color: #c8d6e5;
}

.stApp { background-color: #0a0c10; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background-color: #0e1117;
    border-right: 1px solid #1e2d3d;
}

/* ── Header ── */
.visio-header {
    font-family: 'Share Tech Mono', monospace;
    font-size: 2.2rem;
    font-weight: 700;
    color: #ff2200;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 0;
    text-shadow: 0 0 20px rgba(255, 34, 0, 0.5);
}
.visio-subheader {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.75rem;
    color: #3a6073;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    margin-top: 2px;
    margin-bottom: 1.5rem;
}

/* ── Status badge ── */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 16px;
    border-radius: 4px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    border: 1px solid;
    margin-bottom: 1rem;
}
.status-active  { background:#001a0a; color:#00ff88; border-color:#00ff88; box-shadow:0 0 12px rgba(0,255,136,0.2); }
.status-idle    { background:#12141a; color:#5a6a7e; border-color:#2a3a4e; }
.status-waiting { background:#1a1200; color:#ffcc00; border-color:#ffcc00; box-shadow:0 0 12px rgba(255,204,0,0.2); }

/* ── Pulse dot ── */
.pulse-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: currentColor;
    animation: pulse 1.4s ease-in-out infinite;
}
@keyframes pulse {
    0%,100% { opacity: 1; transform: scale(1); }
    50%      { opacity: 0.4; transform: scale(0.7); }
}

/* ── Live transcript card ── */
.live-card {
    background: #0e1117;
    border: 1px solid #1e2d3d;
    border-left: 4px solid #00e5ff;
    border-radius: 6px;
    padding: 18px 22px;
    margin-bottom: 1rem;
    font-family: 'Share Tech Mono', monospace;
    position: relative;
}
.live-card-label {
    font-size: 0.65rem;
    letter-spacing: 0.25em;
    color: #3a6073;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.live-card-text {
    font-size: 1.2rem;
    color: #e0f0ff;
    word-break: break-word;
}
.live-card-text.empty { color: #2a3a4e; font-style: italic; }

/* ── Intent pill ── */
.intent-pill {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-top: 10px;
    border: 1px solid;
}
.intent-threat   { background:#1a0000; color:#ff4444; border-color:#ff4444; box-shadow:0 0 10px rgba(255,68,68,0.3); }
.intent-distress { background:#1a0800; color:#ff8800; border-color:#ff8800; box-shadow:0 0 10px rgba(255,136,0,0.3); }
.intent-command  { background:#001220; color:#00aaff; border-color:#00aaff; box-shadow:0 0 10px rgba(0,170,255,0.3); }
.intent-normal   { background:#001208; color:#00cc66; border-color:#00cc66; }
.intent-none     { background:#111; color:#3a4a5e; border-color:#2a3a4e; }

/* ── Alarm banner ── */
.alarm-banner {
    background: linear-gradient(90deg, #1a0000, #2a0000, #1a0000);
    border: 1px solid #ff2200;
    border-radius: 6px;
    padding: 14px 20px;
    text-align: center;
    font-family: 'Share Tech Mono', monospace;
    font-size: 1rem;
    color: #ff4444;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    box-shadow: 0 0 20px rgba(255, 34, 0, 0.25);
    animation: alarm-flash 0.8s ease-in-out infinite alternate;
    margin-bottom: 1rem;
}
@keyframes alarm-flash {
    from { opacity: 1; box-shadow: 0 0 20px rgba(255,34,0,0.25); }
    to   { opacity: 0.75; box-shadow: 0 0 35px rgba(255,34,0,0.5); }
}

/* ── History table ── */
.history-row {
    display: grid;
    grid-template-columns: 120px 1fr 110px;
    gap: 12px;
    align-items: center;
    padding: 10px 16px;
    border-bottom: 1px solid #12161c;
    font-size: 0.85rem;
    transition: background 0.15s;
}
.history-row:hover { background: #0e1117; }
.history-row:last-child { border-bottom: none; }
.history-time {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    color: #3a5060;
}
.history-text { color: #a0b8cc; }
.history-container {
    background: #0a0d12;
    border: 1px solid #1a2535;
    border-radius: 6px;
    overflow: hidden;
    max-height: 340px;
    overflow-y: auto;
}
.history-header {
    display: grid;
    grid-template-columns: 120px 1fr 110px;
    gap: 12px;
    padding: 8px 16px;
    background: #0e1117;
    border-bottom: 1px solid #1e2d3d;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    color: #3a5060;
    text-transform: uppercase;
}

/* ── Metric cards ── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin-bottom: 1.2rem;
}
.metric-card {
    background: #0e1117;
    border: 1px solid #1a2535;
    border-radius: 6px;
    padding: 14px 16px;
    text-align: center;
}
.metric-value {
    font-family: 'Share Tech Mono', monospace;
    font-size: 1.8rem;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 4px;
}
.metric-label {
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    color: #3a5060;
    text-transform: uppercase;
}
.metric-total   { color: #00e5ff; }
.metric-threat  { color: #ff4444; }
.metric-distress{ color: #ff8800; }
.metric-command { color: #00aaff; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0a0c10; }
::-webkit-scrollbar-thumb { background: #2a3a4e; border-radius: 2px; }

/* ── Streamlit overrides ── */
.stButton > button {
    font-family: 'Share Tech Mono', monospace;
    letter-spacing: 0.1em;
    border-radius: 4px;
    border: 1px solid;
    transition: all 0.2s;
    font-size: 0.85rem;
}
div[data-testid="stMetricValue"] { font-family: 'Share Tech Mono', monospace; }
.stSlider { color: #00e5ff; }
label[data-testid="stWidgetLabel"] {
    font-family: 'Rajdhani', sans-serif;
    color: #7a9ab0;
    font-size: 0.85rem;
    letter-spacing: 0.05em;
}
</style>
""", unsafe_allow_html=True)


# ── Session state init ─────────────────────────────────────────────────────
def _init_state():
    defaults = {
        "running": False,
        "history": [],           # list of {time, text, intent}
        "latest_text": "",
        "latest_intent": "none",
        "alarm_active": False,
        "worker_thread": None,
        "result_queue": queue.Queue(),
        "total": 0,
        "count_threat": 0,
        "count_distress": 0,
        "count_command": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()


# ── Background worker ──────────────────────────────────────────────────────
def _detection_worker(result_q: queue.Queue, duration: int, stop_event: threading.Event):
    """Runs in a background thread; imports heavy modules here to avoid blocking UI."""
    try:
        from code_red.mic import record_audio
        from code_red.stt import transcribe
        from code_red.intent import detect_intent
        from code_red.alarm import play_alarm
    except ImportError as e:
        result_q.put({"error": str(e)})
        return

    while not stop_event.is_set():
        try:
            audio = record_audio(duration)
            text = transcribe(audio)
            if not text:
                continue
            intent = detect_intent(text)
            if intent in ("threat", "distress"):
                try:
                    play_alarm()
                except Exception:
                    pass
            result_q.put({
                "time": datetime.now().strftime("%H:%M:%S"),
                "text": text,
                "intent": intent,
            })
        except Exception as ex:
            result_q.put({"error": str(ex)})
            time.sleep(1)


# ── Helpers ───────────────────────────────────────────────────────────────
INTENT_META = {
    "threat":   ("🔴", "intent-threat",   "THREAT"),
    "distress": ("🟠", "intent-distress", "DISTRESS"),
    "command":  ("🔵", "intent-command",  "COMMAND"),
    "normal":   ("🟢", "intent-normal",   "NORMAL"),
    "none":     ("⚪", "intent-none",     "SILENCE"),
}

def intent_pill(intent: str) -> str:
    _, css, label = INTENT_META.get(intent, ("⚪", "intent-none", intent.upper()))
    return f'<span class="intent-pill {css}">{label}</span>'


def drain_queue():
    """Pull all pending results from the queue into session state."""
    q: queue.Queue = st.session_state["result_queue"]
    changed = False
    while not q.empty():
        item = q.get_nowait()
        if "error" in item:
            st.session_state["latest_text"] = f"[ERROR] {item['error']}"
            st.session_state["latest_intent"] = "none"
            changed = True
            continue
        st.session_state["latest_text"] = item["text"]
        st.session_state["latest_intent"] = item["intent"]
        st.session_state["total"] += 1
        if item["intent"] == "threat":
            st.session_state["count_threat"] += 1
            st.session_state["alarm_active"] = True
        elif item["intent"] == "distress":
            st.session_state["count_distress"] += 1
            st.session_state["alarm_active"] = True
        elif item["intent"] == "command":
            st.session_state["count_command"] += 1
            st.session_state["alarm_active"] = False
        else:
            st.session_state["alarm_active"] = False
        st.session_state["history"].insert(0, item)
        if len(st.session_state["history"]) > 100:
            st.session_state["history"].pop()
        changed = True
    return changed


# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="visio-header">CODE RED</p>', unsafe_allow_html=True)
    st.markdown('<p class="visio-subheader">Audio Intelligence System</p>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**⚙️ Detection Settings**")

    chunk_duration = st.slider(
        "Recording chunk (seconds)", min_value=1, max_value=8, value=3,
        disabled=st.session_state["running"]
    )

    st.markdown("---")
    st.markdown("**🎯 Intent Triggers**")
    st.markdown("""
    <small style='color:#3a6073; font-family: Share Tech Mono, monospace; font-size:0.7rem; line-height:1.8'>
    🔴 THREAT — kill, attack, gun, fire, bomb<br>
    🟠 DISTRESS — help, save, please, emergency<br>
    🔵 COMMAND — open, close, lock, unlock<br>
    🟢 NORMAL — regular speech<br>
    ⚪ SILENCE — no speech / noise
    </small>
    """, unsafe_allow_html=True)

    st.markdown("---")

    if st.button("🔄  Reset Stats", use_container_width=True):
        st.session_state.update({
            "history": [], "total": 0,
            "count_threat": 0, "count_distress": 0, "count_command": 0,
            "latest_text": "", "latest_intent": "none", "alarm_active": False,
        })
        st.rerun()


# ── Main layout ───────────────────────────────────────────────────────────
st.markdown('<p class="visio-header">CODE RED</p>', unsafe_allow_html=True)
st.markdown('<p class="visio-subheader">Real-Time Speech Detection Interface</p>', unsafe_allow_html=True)

# Start / Stop buttons
col_start, col_stop, col_gap = st.columns([1, 1, 4])
with col_start:
    if st.button("▶  START", use_container_width=True, disabled=st.session_state["running"]):
        stop_event = threading.Event()
        q = queue.Queue()
        st.session_state["result_queue"] = q
        st.session_state["_stop_event"] = stop_event
        t = threading.Thread(
            target=_detection_worker,
            args=(q, chunk_duration, stop_event),
            daemon=True,
        )
        t.start()
        st.session_state["worker_thread"] = t
        st.session_state["running"] = True
        st.rerun()

with col_stop:
    if st.button("⏹  STOP", use_container_width=True, disabled=not st.session_state["running"]):
        if "_stop_event" in st.session_state:
            st.session_state["_stop_event"].set()
        st.session_state["running"] = False
        st.session_state["alarm_active"] = False
        st.rerun()

# Status badge
if st.session_state["running"]:
    st.markdown(
        '<div class="status-badge status-active">'
        '<div class="pulse-dot"></div>LISTENING — ACTIVE</div>',
        unsafe_allow_html=True,
    )
elif st.session_state["latest_text"]:
    st.markdown(
        '<div class="status-badge status-idle">■ STOPPED</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<div class="status-badge status-idle">■ IDLE — PRESS START</div>',
        unsafe_allow_html=True,
    )

# Alarm banner
if st.session_state["alarm_active"]:
    intent_label = st.session_state["latest_intent"].upper()
    st.markdown(
        f'<div class="alarm-banner">⚠  ALARM TRIGGERED — {intent_label} DETECTED  ⚠</div>',
        unsafe_allow_html=True,
    )

# Metric row
st.markdown(f"""
<div class="metric-grid">
  <div class="metric-card">
    <div class="metric-value metric-total">{st.session_state["total"]}</div>
    <div class="metric-label">Total Detections</div>
  </div>
  <div class="metric-card">
    <div class="metric-value metric-threat">{st.session_state["count_threat"]}</div>
    <div class="metric-label">Threats</div>
  </div>
  <div class="metric-card">
    <div class="metric-value metric-distress">{st.session_state["count_distress"]}</div>
    <div class="metric-label">Distress</div>
  </div>
  <div class="metric-card">
    <div class="metric-value metric-command">{st.session_state["count_command"]}</div>
    <div class="metric-label">Commands</div>
  </div>
</div>
""", unsafe_allow_html=True)

# Live transcript card
latest = st.session_state["latest_text"]
latest_intent = st.session_state["latest_intent"]
text_class = "" if latest else "empty"
text_display = latest if latest else "Waiting for speech..."

st.markdown(f"""
<div class="live-card">
  <div class="live-card-label">Live Transcript</div>
  <div class="live-card-text {text_class}">{text_display}</div>
  {intent_pill(latest_intent)}
</div>
""", unsafe_allow_html=True)


# ── Auto-refresh while running ────────────────────────────────────────────
if st.session_state["running"]:
    drain_queue()
    time.sleep(0.4)
    st.rerun()