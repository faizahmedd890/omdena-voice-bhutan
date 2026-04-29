try:
    from streamlit_mic_recorder import speech_to_text
except Exception:
    speech_to_text = None


def is_voice_available() -> bool:
    return speech_to_text is not None


def capture_voice_text(key: str):
    if speech_to_text is None:
        return None

    return speech_to_text(
        language="en",
        start_prompt="🎙️",
        stop_prompt="⏹️",
        just_once=True,
        use_container_width=True,
        key=key
    )