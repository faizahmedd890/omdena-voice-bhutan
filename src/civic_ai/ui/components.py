import html
import streamlit as st


def render_header(llm_status: str, voice_status: str):
    st.markdown(
        f"""
        <div class="hero-card">
            <h1>🤖 Omdena Public Service Assistant</h1>
            <div class="hero-subtitle">Prototype – Team 3 | Voice & Chat Prototyping</div>
            
        </div>
        """,
        unsafe_allow_html=True
    )


def render_voice_box(transcript: str):
    safe_text = html.escape(transcript)

    st.markdown(
        f"""
        <div class="voice-box">
            <div class="voice-icon">🎙️</div>
            <div>
                <div class="voice-title">Voice captured</div>
                <div class="voice-text">{safe_text}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_footer():
    st.markdown(
        """
        <div class="footer-note">
            Experimental Week 2 prototype. Voice input currently works best in English.
        </div>
        """,
        unsafe_allow_html=True
    )