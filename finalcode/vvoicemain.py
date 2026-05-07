# ===================== IMPORTS =====================
import os
import numpy as np
import sounddevice as sd
import whisper
import imageio_ffmpeg
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
from deep_translator import GoogleTranslator   # ✅ changed

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

# ===================== WHISPER (Speech → Text) =====================
whisper_model = whisper.load_model("base")

def live_voice_input():
    fs = 16000

    input("🎤 Press ENTER to start speaking...")
    print("🔴 Recording... Press ENTER to stop.")

    recording = []

    def callback(indata, frames, time, status):
        recording.append(indata.copy())

    with sd.InputStream(samplerate=fs, channels=1, callback=callback):
        input()

    audio = np.concatenate(recording, axis=0).flatten()

    print("🧠 Converting speech to text...")
    result = whisper_model.transcribe(audio, fp16=False)
    text = result["text"]

    print("📝 You said:", text)
    return text


# ===================== TRANSLATION (FIXED - SIMPLE) =====================
def translate_if_needed(text, lang_choice):
    if lang_choice == "2":
        print("🌐 Translating Dzongkha → English...")
        translated = GoogleTranslator(source='auto', target='en').translate(text)
        return translated
    return text


# ===================== EMBEDDINGS =====================
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en-v1.5"
)

# ===================== LOAD CHROMA DB =====================
db = Chroma(
    persist_directory="chroma_db",
    embedding_function=embeddings
)

retriever = db.as_retriever(search_kwargs={"k": 4})

# ===================== LLM =====================
llm = ChatMistralAI(model="open-mistral-7b")

# ===================== PROMPT =====================
prompt = ChatPromptTemplate.from_messages([
    ("system",
     """You are a friendly AI assistant for citizens of Bhutan, specialized in Business Registration and Licensing.

Rules:

1) If user greets (hello, hi, good morning), greet back. Do NOT use document.

2) User may speak English or Dzongkha. Always reply in English.

3) For Business Registration/Licensing questions:
   - First use Context from document.
   - If not found in Context, answer from your own knowledge.

4) If unrelated to this topic, politely say you only help with this.

5) Keep answers simple and citizen-friendly.
"""
     ),
    ("human",
     """Context:
{context}

User Question:
{question}
"""
     )
])


# ===================== RAG FUNCTION =====================
def ask_rag(question):
    docs = retriever.invoke(question)
    context = "\n\n".join([doc.page_content for doc in docs])

    chain = prompt | llm
    try:
        response = chain.invoke({
            "context": context,
            "question": question
        })
        return response.content
    except Exception as e:
        return f"⚠️ Error: I'm currently unable to process requests due to a service error ({e}). Please try again later."


# ===================== MAIN LOOP =====================
print("✅ Voice + Text RAG Chatbot Ready")

while True:

    # -------- Language --------
    print("\nSelect language:")
    print("1. English")
    print("2. Dzongkha")
    print("0. Exit")

    lang = input("Enter choice: ")
    if lang == "0":
        break

    # -------- Mode --------
    print("\nChoose input mode:")
    print("1. Voice (live microphone)")
    print("2. Text")

    mode = input("Enter choice: ")

    # -------- Input --------
    if mode == "1":
        user_text = live_voice_input()
    elif mode == "2":
        user_text = input("Type your message: ")
    else:
        continue

    # ✅ SIMPLE TRANSLATION (NO ASYNC, NO ERROR)
    user_text = translate_if_needed(user_text, lang)

    # -------- RAG --------
    print("\n🤖 Thinking...\n")
    answer = ask_rag(user_text)

    print("AI:", answer)
    print("\n👉 Do you have any other question?\n")