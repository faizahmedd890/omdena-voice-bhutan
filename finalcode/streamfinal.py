import streamlit as st
import tempfile
import os
import asyncio
import nest_asyncio
import edge_tts

from groq import Groq
from dotenv import load_dotenv

from c8sud2 import (
    ConversationState,
    controller,
    maybe_translate
)

from database import (
    save_chat,
    load_chat_history,
    load_all_sessions,
    delete_session
)

nest_asyncio.apply()

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


st.set_page_config(
    page_title="OmdenaBHT",
    page_icon="🇧🇹",
    layout="wide"
)


def transcribe_audio(audio_bytes):

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".wav"
        ) as tmp:

            tmp.write(audio_bytes)

            tmp_path = tmp.name

        with open(tmp_path, "rb") as file:

            transcription = client.audio.transcriptions.create(
                file=file,
                model="whisper-large-v3-turbo"
            )

        os.unlink(tmp_path)

        return transcription.text.strip()

    except Exception as e:

        st.error(f"Transcription Error: {e}")

        return ""

async def generate_tts(text):

    communicate = edge_tts.Communicate(
        text=text,
        voice="en-US-AriaNeural"
    )

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp3"
    ) as tmp:

        output_path = tmp.name

    await communicate.save(output_path)

    return output_path

def speak_text(text):

    try:

        audio_path = asyncio.run(
            generate_tts(text)
        )

        with open(audio_path, "rb") as f:

            audio_bytes = f.read()

        os.unlink(audio_path)

        return audio_bytes

    except Exception as e:

        st.error(f"TTS Error: {e}")

        return None

if "state" not in st.session_state:
    st.session_state.state = ConversationState()

if "chat_id" not in st.session_state:
    st.session_state.chat_id = st.session_state.state.session_id

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_voice" not in st.session_state:
    st.session_state.pending_voice = ""

if "audio_cache" not in st.session_state:
    st.session_state.audio_cache = {}

if "playing_audio" not in st.session_state:
    st.session_state.playing_audio = None

if "language" not in st.session_state:
    st.session_state.language = "English"

if "input_mode" not in st.session_state:
    st.session_state.input_mode = "Text"

def start_new_chat():

    st.session_state.state = ConversationState()

    st.session_state.chat_id = st.session_state.state.session_id

    st.session_state.messages = []

    st.session_state.pending_voice = ""

    st.session_state.audio_cache = {}

    st.session_state.playing_audio = None

def load_session(chat_id):

    history = load_chat_history(chat_id)

    messages = []

    for row in history:

        messages.append({
            "role": row["role"],
            "content": row["message"]
        })

    st.session_state.messages = messages

    st.session_state.chat_id = chat_id

    st.session_state.state = ConversationState()

    st.session_state.state.session_id = chat_id

    st.session_state.playing_audio = None

def get_chat_title(chat_id):

    history = load_chat_history(chat_id)

    for row in history:

        if row["role"] == "user":

            text = row["message"]

            if len(text) > 35:
                return text[:35] + "..."

            return text

    return "New Chat"

with st.sidebar:

    st.title("🇧🇹 OmdenaBHT")

    if st.button(
        "➕ New Chat",
        use_container_width=True
    ):

        start_new_chat()

        st.rerun()

    st.divider()

    st.subheader("Language")

    st.session_state.language = st.radio(
        "Select Language",
        ["English", "Dzongkha"]
    )

    st.divider()

    st.subheader("Chat History")

    sessions = load_all_sessions()

    for session_id in sessions[::-1]:

        title = get_chat_title(session_id)

        col1, col2 = st.columns([4, 1])

        with col1:

            if st.button(
                title,
                key=f"load_{session_id}",
                use_container_width=True
            ):

                load_session(session_id)

                st.rerun()

        with col2:

            if st.button(
                "🗑",
                key=f"delete_{session_id}"
            ):

                delete_session(session_id)

                if st.session_state.chat_id == session_id:
                    start_new_chat()

                st.rerun()

st.title("🇧🇹 OmdenaBHT")

st.caption(
    "Bhutan Business Assistant"
)

st.session_state.input_mode = st.radio(
    "Input Mode",
    ["Text", "Voice"],
    horizontal=True
)

for i, msg in enumerate(st.session_state.messages):

    avatar = "🧑" if msg["role"] == "user" else "🤖"

    with st.chat_message(
        msg["role"],
        avatar=avatar
    ):

        st.markdown(msg["content"])

        if msg["role"] == "assistant":

            col1, col2 = st.columns(2)


            with col1:

                if st.button(
                    "🔊 Read",
                    key=f"read_{i}"
                ):

                    audio_bytes = speak_text(
                        msg["content"]
                    )

                    if audio_bytes:

                        st.session_state.audio_cache[i] = audio_bytes

                        st.session_state.playing_audio = i

            with col2:

                if st.button(
                    "⏹ Stop",
                    key=f"stop_{i}"
                ):

                    if st.session_state.playing_audio == i:

                        st.session_state.playing_audio = None

                        st.rerun()

            if st.session_state.playing_audio == i:

                if i in st.session_state.audio_cache:

                    st.audio(
                        st.session_state.audio_cache[i],
                        format="audio/mp3",
                        autoplay=True
                    )

user_input = None

if st.session_state.input_mode == "Text":

    user_input = st.chat_input(
        "Ask about Bhutan business registration, renewal, licensing..."
    )

else:

    st.subheader("🎤 Voice Input")

    audio = st.audio_input(
        "Record Voice"
    )

    if audio:

        audio_bytes = audio.read()

        with st.spinner("Transcribing..."):

            transcribed_text = transcribe_audio(
                audio_bytes
            )

        if transcribed_text:

            st.session_state.pending_voice = transcribed_text

        else:

            st.error(
                "Could not understand audio"
            )

    if st.session_state.pending_voice:

        st.info(
            f"You said: {st.session_state.pending_voice}"
        )

        if st.button(
            "✅ Send",
            use_container_width=True
        ):

            user_input = st.session_state.pending_voice

            st.session_state.pending_voice = ""

if user_input:

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    is_dzongkha = (
        st.session_state.language == "Dzongkha"
    )

    user_english = maybe_translate(
        user_input,
        is_dzongkha
    )

    with st.spinner("Thinking..."):

        reply = controller(
            st.session_state.state,
            user_english
        )

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })

    save_chat(
        st.session_state.chat_id,
        "user",
        user_input
    )

    save_chat(
        st.session_state.chat_id,
        "assistant",
        reply
    )

    st.rerun()

st.divider()

st.caption(
    "OmdenaBHT may make mistakes. Verify important information with official Bhutan government sources."
)