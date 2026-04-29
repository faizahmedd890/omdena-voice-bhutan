# Architecture

## Overview

The Omdena Public Service Assistant is a Week 2 prototype for a voice-first public service assistant.

It supports:

- text input
- experimental voice input
- department routing
- Team 2-style conversation flows
- Mistral AI or fallback responses

This is not a production government system. It is an early prototype for testing the interaction flow and technical direction.

---

## High-Level Flow

```text
User Input
    ↓
Text or Microphone Input
    ↓
Conversation Flow Manager
    ↓
Department Routing
    ↓
Department Context
    ↓
Mistral AI or Fallback Response
    ↓
User-Friendly Answer