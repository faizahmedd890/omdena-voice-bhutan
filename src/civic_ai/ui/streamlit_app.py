import os

import streamlit as st

from civic_ai.services.flow_manager import (
    create_initial_flow_state,
    handle_flow_turn,
)
from civic_ai.services.response_generator import generate_response
from civic_ai.services.router import route_department
from civic_ai.services.voice_service import capture_voice_text, is_voice_available
from civic_ai.ui.components import render_footer, render_header, render_voice_box
from civic_ai.ui.styles import PREMIUM_MINIMAL_CSS


def init_session_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "input_counter" not in st.session_state:
        st.session_state.input_counter = 0

    if "last_voice_transcript" not in st.session_state:
        st.session_state.last_voice_transcript = ""

    if "flow_state" not in st.session_state:
        st.session_state.flow_state = create_initial_flow_state()


def reset_conversation() -> None:
    st.session_state.messages = []
    st.session_state.input_counter += 1
    st.session_state.last_voice_transcript = ""
    st.session_state.flow_state = create_initial_flow_state()
    st.rerun()


def render_chat_history() -> None:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def process_user_input(user_input: str) -> None:
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    flow_result = handle_flow_turn(
        user_message=user_input,
        state=st.session_state.flow_state,
    )

    st.session_state.flow_state = flow_result["state"]

    if flow_result["should_answer"]:
        answer_input = flow_result.get("answer_input") or user_input
        route = route_department(answer_input)

        with st.spinner("Thinking..."):
            bot_reply = generate_response(answer_input, route)
    else:
        bot_reply = flow_result["message"]

    st.session_state.messages.append(
        {"role": "assistant", "content": bot_reply}
    )

    st.session_state.input_counter += 1
    st.rerun()


def render_input_area() -> None:
    st.markdown(
        '<div class="section-note">Type your question or tap the mic icon to record.</div>',
        unsafe_allow_html=True,
    )

    user_input = None

    input_col, mic_col, send_col = st.columns([8.8, 1.1, 1.1])

    with input_col:
        typed_text = st.text_input(
            "Message",
            placeholder="Ask about public services...",
            label_visibility="collapsed",
            key=f"draft_message_{st.session_state.input_counter}",
        )

    with mic_col:
        if not is_voice_available():
            st.button("🎙️", disabled=True, help="Install streamlit-mic-recorder")
        else:
            captured_voice = capture_voice_text(
                key=f"voice_input_{st.session_state.input_counter}"
            )

            if captured_voice:
                user_input = captured_voice.strip()
                st.session_state.last_voice_transcript = user_input
                render_voice_box(user_input)

    with send_col:
        send_clicked = st.button("➤", use_container_width=True)

    if send_clicked and typed_text.strip():
        user_input = typed_text.strip()

    if user_input:
        process_user_input(user_input)


def render_sidebar() -> None:
    with st.sidebar:
        st.subheader("Prototype Controls")

        if st.button("New conversation", use_container_width=True):
            reset_conversation()

        st.divider()

        st.caption("Current flow features")
        st.markdown(
            """
            - Open-ended user input
            - Department classification
            - Classification confirmation
            - Slot-filling question
            - Department-aware response
            - Fallback path for unclear requests
            """
        )

        st.divider()

        st.caption("Future work")
        st.markdown(
            """
            - Dzongkha STT/TTS
            - Translation API
            - RAG over official documents
            - Human handoff
            - Status tracking
            """
        )


def run_app() -> None:
    st.set_page_config(
        page_title="Omdena Public Service Assistant",
        page_icon="🤖",
        layout="centered",
        initial_sidebar_state="collapsed",
    )

    st.markdown(PREMIUM_MINIMAL_CSS, unsafe_allow_html=True)
    init_session_state()

    api_key_exists = bool(os.getenv("MISTRAL_API_KEY", "").strip())
    voice_ready = is_voice_available()

    llm_status = "Mistral connected" if api_key_exists else "Fallback mode"
    voice_status = "Voice ready" if voice_ready else "Voice unavailable"

    render_sidebar()
    render_header(llm_status, voice_status)
    render_chat_history()
    render_input_area()
    render_footer()