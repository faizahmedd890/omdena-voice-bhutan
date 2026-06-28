<div align="center">

# 🇧🇹 OmdenaBHT — AI Agent for Bhutan Public Services

### _Talk to your government. In your language. With your voice._

<br/>

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Mistral AI](https://img.shields.io/badge/Mistral-AI%20LLM-FF7000?style=for-the-badge)](https://mistral.ai)
[![Whisper](https://img.shields.io/badge/OpenAI-Whisper%20STT-412991?style=for-the-badge&logo=openai&logoColor=white)](https://github.com/openai/whisper)
[![LangChain](https://img.shields.io/badge/LangChain-RAG-1C3C3C?style=for-the-badge)](https://langchain.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

</div>

---

## 💡 What Is This?

Imagine a farmer in Paro who wants to register a small business — but has no idea which forms to fill, which office to visit, or what fees to pay. He speaks Dzongkha. He's never used a government portal before.

**OmdenaBHT changes that.**

This is an AI-powered conversational agent that speaks the language of the people — literally. Built for Bhutan's citizens, it lets anyone ask questions about government services in **English or Dzongkha**, using **their voice or text**, and get back clear, accurate answers drawn from real official documents — **spoken aloud** in response.

No jargon. No confusing portals. Just a conversation.

> _Built by the Omdena Bhutan Chapter as part of the AI for Public Good initiative._

---

## 🔥 What It Can Do

| | Capability |
|:---:|---|
| 🎙️ | **Speak to it** — full live microphone support via OpenAI Whisper |
| 💬 | **Type to it** — clean, responsive chat interface |
| 🌐 | **Dzongkha + English** — speaks your language, answers in English |
| 🔊 | **Talks back** — Text-to-Speech responses via Microsoft Edge TTS |
| 📄 | **Knows the law** — answers backed by real Bhutanese government PDFs |
| 🧠 | **Remembers context** — full conversation memory across your session |
| 📋 | **Guides you step by step** — structured workflow for business registration |
| 🏛️ | **Stays on topic** — strictly focused on Bhutanese public services |

---

## 🧭 How It Works

```
You speak or type (English or Dzongkha)
           │
           ▼
    🌐 Dzongkha? → Auto-translated to English
           │
           ▼
    🧠 Controller checks your intent
     ┌─────┴──────┐
     │            │
  Guided       Free Q&A
  Workflow  →  RAG Engine
  (5 steps)        │
               📄 ChromaDB (Official Gov. Docs)
               🔍 HuggingFace Embeddings
               🤖 Mistral AI (open-mistral-7b)
                    │
                    ▼
         Answer — shown as text + 🔊 spoken aloud
```

Every response is **grounded in real Bhutanese government documents** — not hallucinated. The agent retrieves the most relevant passages first, then formulates a citizen-friendly reply.

---

## 🗂️ Knowledge Base

The agent's brain is powered by three official documents:

| 📄 Document | What It Covers |
|---|---|
| `bhutan business.pdf` | Step-by-step business registration procedures |
| `doing business.pdf` | World Bank's Doing Business in Bhutan report |
| `rules and regulation.pdf` | Licensing laws, compliance, and regulatory rules |

These are chunked, vectorized, and stored in **ChromaDB** for instant semantic retrieval.

---

## 🚀 Getting Started

### What You Need

- Python **3.10+**
- A free **[Mistral AI API Key](https://console.mistral.ai/)**
- A microphone (for voice mode)

### Setup in 4 Steps

**1. Clone & enter the project**
```bash
git clone https://github.com/<your-org>/omdena-voice-bhutan.git
cd omdena-voice-bhutan
```

**2. Create a virtual environment & install dependencies**
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# or: source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

> ⚠️ `openai-whisper` needs PyTorch. For GPU support, grab the right version from [pytorch.org](https://pytorch.org) first.

**3. Add your API key**

Create a `.env` file in the project root:
```env
MISTRAL_API_KEY=your_key_here
```

**4. Launch the app**
```bash
streamlit run finalcode/stream.py
```

The Streamlit UI opens in your browser automatically. That's it — you're live. 🎉

---

## 🎬 Using the Agent

### Voice or Text — Your Choice

When the app opens, pick your **language** (English / Dzongkha) and **input mode** (Voice / Text). Then just start talking.

- Ask anything about Bhutanese government services
- Say **"register"** or **"start"** to kick off the guided business registration flow
- Say **"restart"** anytime to clear your session and start fresh

### 🗺️ The Business Registration Flow

Type `register` and the agent walks you through everything:

```
Step 1 → Are you a Bhutanese citizen?
Step 2 → What is your age?
Step 3 → New registration, renewal, documents, or tax help?
Step 4 → What type of business do you plan to start?
Step 5 → Where in Bhutan will you set up this business?
         ↓
   🎯 Personalized registration guide — sourced from official docs
```

### 🖥️ Prefer the Terminal?

```bash
# Full-featured CLI with memory + workflow
python finalcode/c3.py

# Voice-first terminal agent
python finalcode/vvoicemain.py
```

---

## 📁 Project Structure

```
omdena-voice-bhutan/
│
├── 📂 Document/            # Official Gov. PDFs — the agent's knowledge base
├── 📂 chroma_db/           # Vector embeddings (auto-generated)
│
├── 📂 finalcode/           # ✅ Production code
│   ├── stream.py           # Main Streamlit app (Voice + Text + RAG + TTS)
│   ├── c3.py               # CLI agent with memory + workflow
│   └── vvoicemain.py       # Voice-first CLI agent
│
├── 📂 code/                # Week 1 prototype (historical)
│
├── .env                    # Your API keys (never commit this)
├── requirements.txt
└── LICENSE
```

---

## 🛠️ Tech Stack

| Layer | Tech |
|---|---|
| UI | Streamlit + streamlit-mic-recorder |
| Speech → Text | OpenAI Whisper (base model) |
| Text → Speech | Microsoft Edge TTS |
| Translation | deep-translator (Google Translate) |
| LLM | Mistral AI — open-mistral-7b |
| Embeddings | BAAI/bge-base-en-v1.5 (HuggingFace) |
| Vector Store | ChromaDB |
| RAG Framework | LangChain |
| Audio | sounddevice · numpy · ffmpeg |

---

## 👥 Team

Built with ❤️ by **Omdena Bhutan Chapter — Team 3 (Voice & Chat)**
---

<div align="center">
  <br/>
  <strong>🇧🇹 Built for the people of the Land of the Thunder Dragon 🇧🇹</strong>
  <br/>
  <sub>An <a href="https://omdena.com">Omdena</a> Bhutan Chapter initiative · AI for Public Good</sub>
</div>
