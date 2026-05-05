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

def add(role, text):
    state["history"].append({"role": role, "text": text})

def history_text():
    return "\n".join(
        f"{m['role']}: {m['text']}"
        for m in state["history"][-10:]
    )

def retrieve_context(q):
    docs = retriever.invoke(q)
    return "\n\n".join(d.page_content for d in docs)

def rag_answer(q):
    add("User", q)
    res = chain.invoke({
        "context": retrieve_context(q),
        "history": history_text(),
        "question": q
    })
    ans = res.content.strip()
    add("Assistant", ans)
    return ans

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

st.title("🇧🇹 Bhutan Business Registration Chatbot")

lang = st.radio("Language", ["English", "Dzongkha"])
dz = lang == "Dzongkha"

mode = st.radio("Input Mode", ["Text", "Voice"])

st.divider()

user_input = ""

# ---------------- TEXT ----------------
if mode == "Text":
    user_input = st.text_input("Type your message")

# ---------------- VOICE (CLEAN) ----------------
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

# =============================================================================
# PROCESS
# =============================================================================

if user_input:
    text = translate(user_input, dz)

    st.write("🤖 Thinking...")
    reply = controller(text)

    st.success(reply)

    st.divider()
    st.write("### Chat History")
    for m in state["history"]:
        st.write(f"**{m['role']}**: {m['text']}")
