import streamlit as st
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv()

st.set_page_config(page_title="Bhutan Public Service Assistant", page_icon="🇧🇹")

st.title("🇧🇹 Bhutan Public Service Assistant")
st.caption("Helping citizens access government services easily")

model = ChatMistralAI(
    model="mistral-small-2506",
    temperature=0
)

system_prompt = """
You are a Bhutan Public Service Assistant.

You ONLY help users with government related services like:
- Passport request
- NOC request
- Health information
- Permits
- Public services

If the user asks anything outside public services, politely refuse.

Always ask questions step by step to collect required information.
Keep answers simple for non-technical rural users.
"""

if "messages" not in st.session_state:
    st.session_state.messages = [SystemMessage(content=system_prompt)]

for msg in st.session_state.messages[1:]:
    if isinstance(msg, HumanMessage):
        st.chat_message("user").write(msg.content)
    elif isinstance(msg, AIMessage):
        st.chat_message("assistant").write(msg.content)

user_input = st.chat_input("Ask about passport, NOC, health info, permits...")

def classify_request(text):
    text = text.lower()
    if any(word in text for word in ["passport", "travel document"]):
        return "passport"
    elif "noc" in text:
        return "noc"
    elif "health" in text:
        return "health"
    elif any(word in text for word in ["permit", "license"]):
        return "permit"
    else:
        return "other"

if user_input:

    st.chat_message("user").write(user_input)
    st.session_state.messages.append(HumanMessage(content=user_input))

    intent = classify_request(user_input)

    if intent == "other":
        reply = "I can only help with public service requests like passport, NOC, health info, or permits."
        st.chat_message("assistant").write(reply)
        st.session_state.messages.append(AIMessage(content=reply))
    else:
  
        response = model.invoke(st.session_state.messages)
        st.chat_message("assistant").write(response.content)
        st.session_state.messages.append(AIMessage(content=response.content))