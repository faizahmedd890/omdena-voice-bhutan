import os
import uuid
import random
import re
import numpy as np
import sounddevice as sd
import whisper
import pyttsx3

from dotenv import load_dotenv
from deep_translator import GoogleTranslator

from database import (
    save_chat,
    load_chat_history,
    load_all_sessions
)

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

SYSTEM_PROMPT = """
You are a STRICT Bhutan Business Registration assistant.

Rules:
- Answer ONLY about Bhutan business registration, licensing, permits, taxation, renewal, and related Bhutan business topics.
- Keep answers short, professional, and clear.
- Ask only ONE question at a time during conversational flows.
- Never repeat questions.
- Use retrieved PDF context first.
- Use conversation history.
- If answer is not found in context, use your own knowledge naturally.
- Continue active flows correctly.
- If user changes topic naturally, answer naturally.
- Always answer in English.
"""

ABUSIVE_WORDS = [
    "idiot",
    "stupid",
    "dumb",
    "fuck",
    "bastard",
    "shit"
]

FALLBACK_RESPONSES = [
    "Please clarify your request.",
    "I didn't understand that.",
    "Can you rephrase your request?"
]

KNOWN_LOCATIONS = [
    "thimphu",
    "paro",
    "phuentsholing",
    "punakha",
    "wangdue",
    "bumthang",
    "mongar",
    "trashigang",
    "samtse",
    "gelephu",
    "haa"
]

print("⏳ Loading Whisper model...")
_whisper_model = whisper.load_model("base")

print("⏳ Initializing TTS...")
_tts = pyttsx3.init()
_tts.setProperty("rate", 165)

print("⏳ Loading RAG...")

_embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en-v1.5"
)

_vectordb = Chroma(
    persist_directory="chroma_db",
    embedding_function=_embeddings
)

_retriever = _vectordb.as_retriever(
    search_kwargs={"k": 4}
)

_llm = ChatGroq(
    model_name="llama-3.1-8b-instant",
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

_prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    (
        "human",
        "Context:\n{context}\n\nHistory:\n{history}\n\nUser:{question}"
    )
])

_chain = _prompt | _llm


def normalize(text):

    return text.lower().strip()


def is_greeting(text):

    greetings = [
        "hi",
        "hello",
        "hey",
        "good morning",
        "good evening",
        "good afternoon"
    ]

    return normalize(text) in greetings


def is_abusive(text):

    t = normalize(text)

    return any(x in t for x in ABUSIVE_WORDS)


def is_fallback(text):

    t = normalize(text)

    if len(t) <= 1:
        return True

    bad = [
        "asdf",
        "zzz",
        "???"
    ]

    return t in bad


def maybe_translate(text, dz):

    if not dz:
        return text

    try:

        return GoogleTranslator(
            source="auto",
            target="en"
        ).translate(text)

    except Exception:

        return text


def detect_intent(text):

    t = normalize(text)

    strong_new_patterns = [
        "i want to start a business",
        "i want to open a business",
        "i want to register a business",
        "help me start a business",
        "help me register a business",
        "open a company",
        "register my business"
    ]

    renewal_patterns = [
        "renew my business",
        "renew my license",
        "renew license",
        "renew business",
        "license renewal",
        "i want to renew my business",
        "i want to renewal my business"
    ]

    for x in strong_new_patterns:

        if x in t:
            return "new"

    for x in renewal_patterns:

        if x in t:
            return "renewal"

    return None


def extract_age(text):

    digits = "".join(
        c for c in text if c.isdigit()
    )

    if digits:
        return int(digits)

    return None


def extract_location(text):

    t = normalize(text)

    for loc in KNOWN_LOCATIONS:

        if loc in t:
            return loc.title()

    return text.title()


def speak_text(text):

    try:

        _tts.say(text)
        _tts.runAndWait()

    except Exception as e:

        print("⚠️ TTS Error:", e)


def record_voice():

    fs = 16000

    input("\n🎤 Press ENTER to start...")
    print("🔴 Recording... Press ENTER to stop.")

    chunks = []

    def callback(indata, frames, time, status):

        chunks.append(indata.copy())

    try:

        with sd.InputStream(
            samplerate=fs,
            channels=1,
            callback=callback
        ):
            input()

        audio = np.concatenate(
            chunks,
            axis=0
        ).flatten()

        result = _whisper_model.transcribe(
            audio,
            fp16=False
        )

        return result["text"].strip()

    except Exception as e:

        print("⚠️ Voice Error:", e)

        return ""


def retrieve_context(question):

    try:

        docs = _retriever.invoke(question)

        if not docs:
            return ""

        return "\n\n".join(
            d.page_content for d in docs
        )

    except Exception as e:

        print("⚠️ Retrieval Error:", e)

        return ""


class ConversationState:

    def __init__(self):

        self.reset()

    def reset(self):

        self.session_id = (
            f"BHU-{uuid.uuid4().hex[:8].upper()}"
        )

        self.history = []

        self.intent = None

        self.slots = {
            "citizenship": None,
            "age": None,
            "business_type": None,
            "location": None,
            "license_status": None
        }

    def add(self, role, text):

        self.history.append({
            "role": role,
            "text": text
        })

    def format_history(self):

        return "\n".join(
            f"{m['role']}: {m['text']}"
            for m in self.history[-10:]
        )


def rag_answer(state, question):

    state.add("user", question)

    context = retrieve_context(question)

    history = state.format_history()

    try:

        if context.strip():

            response = _chain.invoke({
                "context": context,
                "history": history,
                "question": question
            })

            answer = response.content.strip()

        else:

            response = _llm.invoke(
                f"""
                Conversation History:
                {history}

                User Question:
                {question}

                Answer naturally about Bhutan business registration.
                Keep answer short and clear.
                """
            )

            answer = response.content.strip()

    except Exception as e:

        print("⚠️ LLM Error:", e)

        answer = "Sorry, I am having trouble answering right now."

    state.add("assistant", answer)

    return answer


def handle_new_flow(state, user_text):

    if not state.slots["citizenship"]:

        t = normalize(user_text)

        if "bhutan" in t:

            state.slots["citizenship"] = "bhutanese"

        elif "foreign" in t:

            state.slots["citizenship"] = "foreigner"

        else:

            return (
                "Please tell me whether you are "
                "a Bhutanese citizen or a foreigner."
            )

        return "What is your age?"

    if not state.slots["age"]:

        age = extract_age(user_text)

        if not age:
            return "Please enter your age."

        if age < 18:
            return "You must be at least 18 years old."

        state.slots["age"] = age

        return "What type of business do you want to register?"

    if not state.slots["business_type"]:

        state.slots["business_type"] = user_text

        return "Which location in Bhutan will the business operate in?"

    if not state.slots["location"]:

        state.slots["location"] = extract_location(user_text)

        question = (
            f"How to register a "
            f"{state.slots['business_type']} "
            f"business in Bhutan"
        )

        state.intent = None

        return rag_answer(state, question)

    return "Please clarify your request."


def handle_renewal_flow(state, user_text):

    if not state.slots["business_type"]:

        state.slots["business_type"] = user_text

        return (
            "Is your business license active "
            "or expired?"
        )

    if not state.slots["license_status"]:

        state.slots["license_status"] = user_text

        question = (
            f"How to renew a "
            f"{state.slots['business_type']} "
            f"business license in Bhutan "
            f"with status "
            f"{state.slots['license_status']}"
        )

        state.intent = None

        return rag_answer(state, question)

    return "Please clarify your request."


def controller(state, user_text):

    t = normalize(user_text)

    if t == "restart":

        state.reset()

        return "🔁 Chat restarted."

    if is_greeting(user_text):

        return (
            "Hello! How can I help you with "
            "business registration or renewal in Bhutan?"
        )

    if is_abusive(user_text):

        return "Please use respectful language."

    if is_fallback(user_text):

        return random.choice(FALLBACK_RESPONSES)

    if state.intent == "new":

        return handle_new_flow(
            state,
            user_text
        )

    if state.intent == "renewal":

        return handle_renewal_flow(
            state,
            user_text
        )

    intent = detect_intent(user_text)

    if intent == "new":

        state.intent = "new"

        state.slots = {
            "citizenship": None,
            "age": None,
            "business_type": None,
            "location": None,
            "license_status": None
        }

        return (
            "Are you a Bhutanese citizen or a foreigner?"
        )

    if intent == "renewal":

        state.intent = "renewal"

        state.slots["business_type"] = None
        state.slots["license_status"] = None

        return (
            "What type of business license "
            "do you want to renew?"
        )

    return rag_answer(state, user_text)


def show_previous_sessions():

    sessions = load_all_sessions()

    if not sessions:
        return

    print("\n📁 Previous Sessions:")

    for i, s in enumerate(sessions[-10:], start=1):

        print(f"{i}. {s}")

    print()


def main():

    print("\n🇧🇹 Bhutan Business Chatbot\n")

    show_previous_sessions()

    print("Select Language:")
    print("1. English")
    print("2. Dzongkha")

    dz = input("Enter choice: ").strip() == "2"

    print("\nSelect Input Mode:")
    print("1. Text")
    print("2. Voice")

    voice = input("Enter choice: ").strip() == "2"

    state = ConversationState()

    print(f"\n✅ Session: {state.session_id}")

    print("Type 'restart' or 'exit'\n")

    while True:

        if voice:

            raw = record_voice()

            if not raw.strip():

                print("⚠️ Empty voice input.\n")

                continue

            print(f"💬 You: {raw}")

        else:

            raw = input("💬 You: ").strip()

        if normalize(raw) in {
            "exit",
            "quit"
        }:
            break

        user = maybe_translate(raw, dz)

        print("\n🤖 Thinking...\n")

        reply = controller(state, user)

        save_chat(
            state.session_id,
            "user",
            user[:2000]
        )

        save_chat(
            state.session_id,
            "assistant",
            reply[:2000]
        )

        print("OmdenaBHT:", reply, "\n")

        if voice:

            choice = input(
                "🔊 Type 'read' to hear answer "
                "or press ENTER to continue: "
            ).strip().lower()

            if choice == "read":

                speak_text(reply)


if __name__ == "__main__":

    main()