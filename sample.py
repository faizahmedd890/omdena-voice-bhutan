import streamlit as st
from groq import Groq
import os

# Initialize client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="Voice Assistant", page_icon="🎤")

st.title("🎤 Voice-First Public Service Assistant (Prototype)")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Intent classification
def classify_intent(query):
    query = query.lower()
    if "passport" in query:
        return "passport"
    elif "license" in query:
        return "driving_license"
    elif "cid" in query:
        return "cid"
    else:
        return "general"

# Chat input
user_input = st.chat_input("Ask your query (e.g., How to check passport status?)")

if user_input:
    try:
        # 1. Store + show user message
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        # 2. Detect intent
        intent = classify_intent(user_input)
        st.caption(f"Intent detected: {intent}")

        # 3. Call LLM
        with st.spinner("Processing..."):
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": f"""
                        You are a helpful assistant for Bhutan public services.

                        Focus on {intent} related queries.
                        Give simple, step-by-step answers.
                        Keep responses short and easy to understand.
                        """
                    }
                ] + st.session_state.messages
            )

            answer = response.choices[0].message.content

        # 4. Store + show assistant response
        st.session_state.messages.append({"role": "assistant", "content": answer})

        with st.chat_message("assistant"):
            st.markdown(answer)

    except Exception as e:
        import traceback
        st.error("Something went wrong:")
        st.text(str(e))
        st.text(traceback.format_exc())