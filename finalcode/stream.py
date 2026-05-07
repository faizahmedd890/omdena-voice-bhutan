# =============================================================================
# Bhutan Business Registration Chatbot
# Voice + Text | RAG | Dzongkha/English | Workflow + Controller
# CLEAN MIC UI VERSION (No WebRTC)
# =============================================================================

import os
import uuid
import tempfile
import logging
import whisper
import streamlit as st
import imageio_ffmpeg
import edge_tts
import asyncio
import base64
import re

# Add ffmpeg to PATH for whisper
import shutil
ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
ffmpeg_dir = os.path.dirname(ffmpeg_exe)
ffmpeg_symlink = os.path.join(ffmpeg_dir, "ffmpeg.exe")
if not os.path.exists(ffmpeg_symlink):
    try:
        shutil.copy(ffmpeg_exe, ffmpeg_symlink)
    except Exception:
        pass
os.environ["PATH"] += os.pathsep + ffmpeg_dir

from dotenv import load_dotenv
from deep_translator import GoogleTranslator

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader

from streamlit_mic_recorder import mic_recorder

# Silence transformers noise if any
logging.getLogger("transformers").setLevel(logging.ERROR)

load_dotenv()

# =============================================================================
# SYSTEM PROMPT
# =============================================================================

SYSTEM_PROMPT = """
You are a strict assistant representing Bhutanese Government Services.

RULES:
- Answer ONLY about Bhutanese government services (including business registration, licensing, documents, citizen services, and tax).
- If the user asks an unrelated question, politely refuse.
- By default, give SHORT, CLEAR answers (max 6–8 lines).
- If the user explicitly asks for a detailed or long explanation, you may provide a longer answer.
- If the user greets you (e.g., 'hi', 'hello'), greet them back simply. Do NOT provide lists or examples of services.
- Ask ONLY ONE question at a time in the workflow.
- NEVER repeat questions already answered.
- Use the provided full conversation history to remember previous turns and context.
- Do NOT restart the workflow unless the user types 'restart'.
- Always reply in English.
- The user may give input in English or Dzongkha. Dzongkha input will be translated to English before reaching you.
- Use retrieved context first before answering.
"""

# =============================================================================
# CACHE MODELS
# =============================================================================

@st.cache_resource
def load_whisper():
    return whisper.load_model("base")

@st.cache_resource
def load_rag():
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5")
    vectordb = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
    retriever = vectordb.as_retriever(search_kwargs={"k": 4})

    llm = ChatMistralAI(model="open-mistral-7b")

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "Context:\n{context}\n\nHistory:\n{history}\n\nUser: {question}")
    ])

    chain = prompt | llm
    return vectordb, retriever, chain

whisper_model = load_whisper()
vectordb, retriever, chain = load_rag()

# =============================================================================
# SESSION STATE
# =============================================================================

if "state" not in st.session_state:
    st.session_state.state = {
        "history": [],
        "mode": "normal",
        "step": 0,
        "slots": {}
    }

state = st.session_state.state

# =============================================================================
# HELPERS
# =============================================================================

def get_audio_base64(text, voice="en-US-AriaNeural"):
    async def _generate():
        communicate = edge_tts.Communicate(text, voice)
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return base64.b64encode(audio_data).decode()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_generate())
    finally:
        loop.close()

def add(role, text):
    state["history"].append({"role": role, "text": text})

def history_text():
    return "\n".join(
        f"{m['role']}: {m['text']}"
        for m in state["history"]
    )

def retrieve_context(q):
    docs = retriever.invoke(q)
    return "\n\n".join(d.page_content for d in docs)

def rag_answer(q):
    add("User", q)
    return chain.stream({
        "context": retrieve_context(q),
        "history": history_text(),
        "question": q
    })

def translate(text, dz):
    if dz:
        return GoogleTranslator(source="auto", target="en").translate(text)
    return text

# =============================================================================
# WORKFLOW
# =============================================================================

def workflow(text):
    t = text.lower()

    if state["step"] == 1:
        if "yes" in t or "bhutanese" in t:
            state["step"] = 2
            return "Step 2/5: Your age?"
        return "Step 1/5: Are you a Bhutanese citizen?"

    if state["step"] == 2:
        digits = "".join(c for c in t if c.isdigit())
        if digits and int(digits) >= 18:
            state["step"] = 3
            return "Step 3/5: Registration / Renewal / Tax help?"
        return "You must be 18+."

    if state["step"] == 3:
        state["step"] = 4
        return "Step 4/5: Business type?"

    if state["step"] == 4:
        state["slots"]["type"] = text
        state["step"] = 5
        return "Step 5/5: Location in Bhutan?"

    if state["step"] == 5:
        state["slots"]["loc"] = text
        state["mode"] = "normal"
        state["step"] = 0
        q = f"How to register {state['slots']['type']} in {state['slots']['loc']} Bhutan"
        return rag_answer(q)

# =============================================================================
# CONTROLLER
# =============================================================================

def controller(text):
    t = text.lower()

    if t == "restart":
        st.session_state.state = {
            "history": [],
            "mode": "normal",
            "step": 0,
            "slots": {}
        }
        return "Session restarted."

    if state["mode"] == "workflow":
        return workflow(text)

    if "register" in t or "start" in t:
        state["mode"] = "workflow"
        state["step"] = 1
        return "Step 1/5: Are you a Bhutanese citizen?"

    return rag_answer(text)

# =============================================================================
# UI
# =============================================================================

PLAYER_HTML = """
<div style="display: flex; height: 100%; align-items: center; justify-content: flex-end; padding-top: 25px;">
    <button id="mute-btn" onclick="toggleMute()" style="border: none; background: none; font-size: 20px; cursor: pointer;" title="Mute/Unmute Audio">🔊</button>
</div>
<script>
    if (!window.audioQueueInitialized) {
        window.audioQueueInitialized = true;
        window.audioQueue = [];
        window.isPlaying = false;
        window.isMuted = false;

        window.playNext = function() {
            if (window.audioQueue.length > 0) {
                window.isPlaying = true;
                let src = window.audioQueue.shift();
                let audio = new Audio(src);
                audio.muted = window.isMuted;
                window.currentAudio = audio;

                audio.onended = function() {
                    window.currentAudio = null;
                    window.playNext();
                };
                audio.play().catch(e => {
                    console.error("Audio playback failed", e);
                    window.playNext();
                });
            } else {
                window.isPlaying = false;
            }
        };

        window.parent.enqueueAudio = function(src) {
            window.audioQueue.push(src);
            if (!window.isPlaying) {
                window.playNext();
            }
        };

        window.toggleMute = function() {
            window.isMuted = !window.isMuted;
            if (window.currentAudio) {
                window.currentAudio.muted = window.isMuted;
            }
            let btn = document.getElementById('mute-btn');
            if(btn) btn.innerText = window.isMuted ? '🔇' : '🔊';
        };
    }
</script>
"""

st.title("🇧🇹 Bhutan Business Registration Chatbot")

lang = st.radio("Language", ["English", "Dzongkha"])
dz = lang == "Dzongkha"

mode = st.radio("Input Mode", ["Text", "Voice"])

st.divider()

user_input = ""

col1, col2 = st.columns([10, 1])

with col1:
    if mode == "Text":
        user_input = st.text_input("Type your message")
    else:
        st.write("🎤 Speak")
        audio = mic_recorder(start_prompt="Start Recording",
                             stop_prompt="Stop Recording",
                             key="mic")

        if audio:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                f.write(audio["bytes"])
                path = f.name

            result = whisper_model.transcribe(path)
            user_input = result["text"]
            st.success("🗣️ You said: " + user_input)

with col2:
    st.components.v1.html(PLAYER_HTML, height=70)

# =============================================================================
# PROCESS
# =============================================================================

if user_input:
    text = translate(user_input, dz)

    st.write("🤖 Thinking...")
    reply = controller(text)

    if isinstance(reply, str):
        b64 = get_audio_base64(reply)
        st.components.v1.html(
            f"<script id='{uuid.uuid4().hex}'>window.parent.enqueueAudio('data:audio/mp3;base64,{b64}');</script>",
            height=0, width=0
        )
        st.success(reply)
    else:
        placeholder = st.empty()
        full_response = ""
        sentence_buffer = ""
        
        try:
            for chunk in reply:
                text_chunk = chunk.content
                full_response += text_chunk
                sentence_buffer += text_chunk
                placeholder.success(full_response + "▌")
                
                match = re.search(r'([.!?])(\s+|$)', sentence_buffer)
                if match:
                    end_idx = match.end(1)
                    sentence = sentence_buffer[:end_idx].strip()
                    remainder = sentence_buffer[end_idx:]
                    
                    if sentence:
                        b64 = get_audio_base64(sentence)
                        st.components.v1.html(
                            f"<script id='{uuid.uuid4().hex}'>window.parent.enqueueAudio('data:audio/mp3;base64,{b64}');</script>",
                            height=0, width=0
                        )
                    sentence_buffer = remainder
                    
            if sentence_buffer.strip():
                b64 = get_audio_base64(sentence_buffer.strip())
                st.components.v1.html(
                    f"<script id='{uuid.uuid4().hex}'>window.parent.enqueueAudio('data:audio/mp3;base64,{b64}');</script>",
                    height=0, width=0
                )
                
            placeholder.success(full_response)
            add("Assistant", full_response.strip())
        except Exception as e:
            placeholder.error(f"⚠️ API Error from Mistral: {e}")
            add("Assistant", "I'm sorry, I'm having trouble connecting to the AI service right now. Please try again later.")

    st.divider()
    st.write("### Chat History")
    for m in state["history"]:
        st.write(f"**{m['role']}**: {m['text']}")
