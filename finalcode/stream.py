# =============================================================================
# Bhutan Business Registration Chatbot
# Voice + Text | RAG | Dzongkha/English | Workflow + Controller
# FIXED REAL MICROPHONE VOICE VERSION
# =============================================================================

import os
import uuid
import tempfile
import numpy as np
import whisper
import streamlit as st
import av
import soundfile as sf

from dotenv import load_dotenv
from deep_translator import GoogleTranslator

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate

from langchain_community.document_loaders import PyPDFLoader
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase

load_dotenv()

# =============================================================================
# SYSTEM PROMPT
# =============================================================================

SYSTEM_PROMPT = """
You are a STRICT Bhutan Business Registration assistant.

RULES:
- Answer ONLY about Bhutan business registration, licensing, documents, and tax.
- By default, give SHORT, CLEAR answers (max 6–8 lines).
- If the user explicitly asks for a detailed or long explanation, you may provide a longer answer.
- If the user asks an unrelated question, politely refuse.
- Ask ONLY ONE question at a time in the workflow.
- NEVER repeat questions already answered.
- Use conversation history as memory.
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

    llm = ChatMistralAI()

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "Context:\n{context}\n\nHistory:\n{history}\n\nUser: {question}")
    ])

    chain = prompt | llm
    return embeddings, vectordb, retriever, chain

whisper_model = load_whisper()
embeddings, vectordb, retriever, chain = load_rag()

# =============================================================================
# STATE
# =============================================================================

if "state" not in st.session_state:
    st.session_state.state = {
        "session_id": f"BHU-{uuid.uuid4().hex[:8].upper()}",
        "history": [],
        "slots": {"is_citizen": None, "business_type": None, "location": None},
        "mode": "normal",
        "step": 0
    }

state = st.session_state.state

# =============================================================================
# HELPERS
# =============================================================================

def add(role, text):
    state["history"].append({"role": role, "text": text})

def format_history():
    return "\n".join(
        f"{'User' if m['role']=='user' else 'Assistant'}: {m['text']}"
        for m in state["history"][-12:]
    )

def translate(text, dz):
    if dz:
        return GoogleTranslator(source="auto", target="en").translate(text)
    return text

def detect_citizenship(text):
    t = text.lower()
    return any(x in t for x in ["bhutanese", "citizen", "yes", "i am bhutanese"])

def retrieve_context(q):
    docs = retriever.invoke(q)
    return "\n\n".join(d.page_content for d in docs)

def rag_answer(question):
    add("User", question)

    context = retrieve_context(question)
    history = format_history()

    res = chain.invoke({
        "context": context,
        "history": history,
        "question": question
    })

    ans = res.content.strip()
    add("Assistant", ans)
    return ans

# =============================================================================
# WORKFLOW
# =============================================================================

def workflow(user_text):
    t = user_text.lower()

    if state["step"] == 1:
        if detect_citizenship(user_text):
            state["slots"]["is_citizen"] = True
            state["step"] = 2
            return "Step 2/5: Please tell your age."
        return "Step 1/5: Are you a Bhutanese citizen?"

    if state["step"] == 2:
        digits = "".join(c for c in user_text if c.isdigit())
        if digits and int(digits) >= 18:
            state["step"] = 3
            return "Step 3/5: Registration / Renewal / Tax help?"
        return "You must be 18+."

    if state["step"] == 3:
        state["step"] = 4
        return "Step 4/5: What type of business?"

    if state["step"] == 4:
        state["slots"]["business_type"] = user_text
        state["step"] = 5
        return "Step 5/5: Location in Bhutan?"

    if state["step"] == 5:
        state["slots"]["location"] = user_text
        state["step"] = 0
        state["mode"] = "normal"

        q = f"How to register {state['slots']['business_type']} in {state['slots']['location']} Bhutan"
        return rag_answer(q)

# =============================================================================
# CONTROLLER
# =============================================================================

def controller(user_text):
    t = user_text.lower()

    if t == "restart":
        st.session_state.state = {
            "session_id": f"BHU-{uuid.uuid4().hex[:8].upper()}",
            "history": [],
            "slots": {},
            "mode": "normal",
            "step": 0
        }
        return "Session restarted."

    if state["mode"] == "workflow":
        return workflow(user_text)

    if any(w in t for w in ["start", "register"]):
        state["mode"] = "workflow"
        state["step"] = 1
        return "Step 1/5: Are you a Bhutanese citizen?"

    return rag_answer(user_text)

# =============================================================================
# PDF INGEST
# =============================================================================

def ingest_pdf(file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file.read())
        tmp_path = tmp.name

    loader = PyPDFLoader(tmp_path)
    docs = loader.load()

    vectordb.add_documents(docs)
    vectordb.persist()

    return "PDF added to knowledge base!"

# =============================================================================
# AUDIO PROCESSOR (REAL MIC)
# =============================================================================

class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.frames = []

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        self.frames.append(frame.to_ndarray())
        return frame

# =============================================================================
# UI
# =============================================================================

st.title("🇧🇹 Bhutan Business Registration Chatbot")

lang = st.radio("Language", ["English", "Dzongkha"])
dz = lang == "Dzongkha"

mode = st.radio("Input Mode", ["Text", "Voice"])

pdf = st.file_uploader("Upload PDF (optional)", type=["pdf"])
if pdf:
    st.success(ingest_pdf(pdf))

st.divider()

# =============================================================================
# INPUT LOGIC
# =============================================================================

user_input = ""

# ---------------- TEXT MODE ----------------
if mode == "Text":
    user_input = st.text_input("Type your message")

# ---------------- VOICE MODE (FIXED) ----------------
else:
    st.write("🎤 Click START and speak")

    ctx = webrtc_streamer(
        key="voice-input",
        audio_processor_factory=AudioProcessor,
        media_stream_constraints={"audio": True, "video": False},
    )

    if ctx.audio_processor and len(ctx.audio_processor.frames) > 0:

        audio_data = np.concatenate(ctx.audio_processor.frames, axis=1)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            sf.write(f.name, audio_data.T, 16000)
            audio_path = f.name

        result = whisper_model.transcribe(audio_path)
        user_input = result["text"]

        st.success("🗣️ You said: " + user_input)

# =============================================================================
# PROCESS
# =============================================================================

if user_input:
    user_text = translate(user_input, dz)

    st.write("🤖 Thinking...")

    reply = controller(user_text)

    st.success(reply)

    st.divider()

    st.write("### 🧠 Chat History")
    for m in state["history"][-10:]:
        st.write(f"**{m['role']}**: {m['text']}")