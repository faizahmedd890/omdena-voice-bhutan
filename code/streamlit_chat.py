import streamlit as st
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI

load_dotenv()

st.set_page_config(
    page_title="Omdena Public Service Assistant",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Omdena Public Service Assistant")
st.caption("Prototype – Team 3 | Voice & Chat Prototyping")

model = ChatMistralAI(
    model="mistral-small-2506",
    temperature=0
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask about public services...")

if user_input:
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.spinner("Thinking..."):
        response = model.invoke(user_input)
        bot_reply = response.content

    st.chat_message("assistant").markdown(bot_reply)
    st.session_state.messages.append(
        {"role": "assistant", "content": bot_reply}
    )