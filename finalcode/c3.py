# =============================================================================
# Bhutan Business Registration & Licensing Chatbot
# Voice + Text | RAG | Dzongkha/English | Workflow + Controller + Memory
# =============================================================================

import os
import uuid
import numpy as np
import sounddevice as sd
import whisper
from dotenv import load_dotenv
from deep_translator import GoogleTranslator

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate

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
# WHISPER
# =============================================================================

print("⏳ Loading Whisper model...")
_whisper_model = whisper.load_model("base")

def record_voice() -> str:
    fs = 16000
    input("\n🎤 Press ENTER to start speaking...")
    print("🔴 Recording... Press ENTER to stop.")
    chunks = []

    def cb(indata, frames, time, status):
        chunks.append(indata.copy())

    with sd.InputStream(samplerate=fs, channels=1, callback=cb):
        input()

    audio = np.concatenate(chunks, axis=0).flatten()
    result = _whisper_model.transcribe(audio, fp16=False)
    return result["text"].strip()

# =============================================================================
# TRANSLATION
# =============================================================================

def maybe_translate(text: str, dz: bool) -> str:
    if dz:
        return GoogleTranslator(source="auto", target="en").translate(text)
    return text

def detect_citizenship(text: str) -> bool:
    t = text.lower()
    return any(x in t for x in [
        "yes", "yeah", "yep",
        "bhutanese", "citizen of bhutan", "i am bhutanese"
    ])

# =============================================================================
# RAG
# =============================================================================

print("⏳ Loading RAG...")
_embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5")
_vectordb = Chroma(persist_directory="chroma_db", embedding_function=_embeddings)
_retriever = _vectordb.as_retriever(search_kwargs={"k": 4})
_llm = ChatMistralAI()

_prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "Context:\n{context}\n\nHistory:\n{history}\n\nUser: {question}")
])

_chain = _prompt | _llm

def retrieve_context(q: str) -> str:
    docs = _retriever.invoke(q)
    return "\n\n".join(d.page_content for d in docs)

# =============================================================================
# STATE (MEMORY)
# =============================================================================

class ConversationState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.session_id = f"BHU-{uuid.uuid4().hex[:8].upper()}"
        self.history = []
        self.slots = {"is_citizen": None, "business_type": None, "location": None}
        self.mode = "normal"
        self.step = 0

    def add(self, role, text):
        self.history.append({"role": role, "text": text})

    def format_history(self):
        lines = []
        for m in self.history[-12:]:
            r = "User" if m["role"] == "user" else "Assistant"
            lines.append(f"{r}: {m['text']}")
        return "\n".join(lines)

# =============================================================================
# RAG ANSWER
# =============================================================================

def rag_answer(state: ConversationState, question: str) -> str:
    state.add("user", question)
    context = retrieve_context(question)
    history = state.format_history()

    res = _chain.invoke({
        "context": context,
        "history": history,
        "question": question
    })

    ans = res.content.strip()
    state.add("ai", ans)
    return ans

# =============================================================================
# WORKFLOW
# =============================================================================

def workflow_handler(state: ConversationState, user_text: str) -> str:
    t = user_text.lower()

    if state.step == 1:
        if detect_citizenship(user_text):
            state.slots["is_citizen"] = True
            state.step = 2
            return "(Step 2 of 5)\nPlease tell me your age."
        return "(Step 1 of 5)\nAre you a Bhutanese citizen?"

    if state.step == 2:
        digits = "".join(c for c in user_text if c.isdigit())
        if digits and int(digits) >= 18:
            state.step = 3
            return "(Step 3 of 5)\nNew registration, renewal, documents, or tax help?"
        return "You must be at least 18 years old to register a business."

    if state.step == 3:
        state.step = 4
        return "(Step 4 of 5)\nWhat type of business do you plan to start?"

    if state.step == 4:
        state.slots["business_type"] = user_text
        state.step = 5
        return "(Step 5 of 5)\nWhere in Bhutan will you set up this business?"

    if state.step == 5:
        state.slots["location"] = user_text
        state.mode = "normal"
        state.step = 0
        q = f"Guide to register a {state.slots['business_type']} business in {state.slots['location']} Bhutan"
        return rag_answer(state, q)

# =============================================================================
# CONTROLLER
# =============================================================================

def controller(state: ConversationState, user_text: str) -> str:
    t = user_text.lower()

    if t == "restart":
        state.reset()
        return "🔁 Session restarted. How can I help you?"

    if state.mode == "workflow":
        return workflow_handler(state, user_text)

    if any(w in t for w in ["start", "open", "register"]):
        state.mode = "workflow"
        state.step = 1
        return "(Step 1 of 5)\nAre you a Bhutanese citizen?"

    return rag_answer(state, user_text)

# =============================================================================
# MAIN
# =============================================================================

def main():
    print("\n🇧🇹 Bhutan Business Chatbot\n")

    print("Select Language:")
    print("1. English")
    print("2. Dzongkha")
    lang = input("Enter choice: ").strip()
    dz = lang == "2"

    print("\nSelect Input Mode:")
    print("1. Text")
    print("2. Voice")
    mode = input("Enter choice: ").strip()
    voice = mode == "2"

    state = ConversationState()
    print(f"\n✅ Session: {state.session_id}")
    print("Type 'restart' to clear memory | 'exit' to quit\n")

    while True:

        if voice:
            raw = record_voice()
            print(f"💬 You: {raw}")
        else:
            raw = input("💬 You: ").strip()

        if raw.lower() in {"exit", "quit"}:
            break

        user = maybe_translate(raw, dz)

        if dz:
            print(f"🗣️ Translated to English: {user}")

        if detect_citizenship(user):
            state.slots["is_citizen"] = True

        print("\n🤖 Thinking...\n")
        reply = controller(state, user)
        print("OmdenaBHT:", reply, "\n")

if __name__ == "__main__":
    main()