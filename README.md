# Omdena Public Service Assistant

A Week 2 prototype for a voice-first public service assistant developed by Team 3 for the Omdena Bhutan Local Chapter project.

The prototype supports text input, experimental microphone input, internal department routing, Team 2-style conversation flows, and Mistral-powered responses.

---

## Overview

This app helps users ask public-service questions through text or voice. It detects the likely service area, confirms it with the user, asks one follow-up question when needed, and generates a user-friendly response.

This is not a production government system. It is an early prototype for testing voice-first and agent-ready public service interaction.

---

## Features

- Text chat interface
- Experimental microphone input
- Internal department routing
- Lightweight department-based agent structure
- Team 2-style flow: classify → confirm → ask detail → answer
- Mistral AI response generation
- Safe fallback mode without API access
- Clean modular code structure

---

## Architecture

```text
User input
    ↓
Text or voice capture
    ↓
Conversation flow manager
    ↓
Department routing
    ↓
Department-specific context
    ↓
Mistral AI or fallback response
    ↓
User-facing answer
```

---

## Supported Domains

- Business registration
- Tax services
- Immigration and documents
- Health services
- Education services
- General public services

---

## Project Structure

```text
app.py
src/civic_ai/
    domain/
    infrastructure/
    services/
    ui/
docs/
legacy/
```

---

## Setup

```bash
git clone https://github.com/faizahmedd890/omdena-voice-bhutan.git
cd omdena-voice-bhutan

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
copy .env.example .env

python -m streamlit run app.py
```

Add your Mistral key inside `.env`:

```env
MISTRAL_API_KEY=your_mistral_api_key_here
MISTRAL_MODEL=mistral-small-2506
APP_ENV=development
```

---

## Demo Questions

```text
I want to register a new business.
I need to pay company tax.
I want to renew my passport.
I need a hospital appointment.
I need information about school admission.
I registered a business and now I need to pay tax.
```

---

## Voice Input

Voice input is experimental and currently works best in English.

Current flow:

```text
Voice input → Speech-to-text → Routing → Response
```

Dzongkha STT/TTS and translation are future work.

---

## Limitations

The prototype does not yet include:

- Dzongkha speech-to-text
- Dzongkha text-to-speech
- Translation API
- RAG over official government documents
- Real government API integration
- Human handoff
- Application status tracking
- Production security

---

## Week 2 Contribution

This update moves the app from a simple chatbot to a cleaner public-service assistant prototype with voice input, internal routing, lightweight agent-style behavior, Team 2 conversation flows, fallback mode, and modular architecture.