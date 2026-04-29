# Voice Pipeline

## Overview

This document describes the voice-first direction of the Omdena Public Service Assistant.

The current Week 2 prototype includes experimental microphone input. It works best in English and is used to test how voice can enter the same pipeline as text.

---

## Current Voice Flow

```text
User speaks
    ↓
Microphone input
    ↓
Speech-to-text
    ↓
Transcribed text
    ↓
Conversation flow manager
    ↓
Department routing
    ↓
LLM or fallback response
    ↓
Text answer in chat