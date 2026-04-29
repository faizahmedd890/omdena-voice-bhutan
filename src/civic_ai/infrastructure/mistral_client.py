import streamlit as st
from langchain_mistralai import ChatMistralAI

from civic_ai.config import settings


@st.cache_resource
def get_mistral_client():
    if not settings.MISTRAL_API_KEY:
        return None

    try:
        return ChatMistralAI(
            model=settings.MISTRAL_MODEL,
            temperature=0
        )
    except Exception:
        return None