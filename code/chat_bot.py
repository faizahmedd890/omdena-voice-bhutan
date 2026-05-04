from dotenv import load_dotenv
load_dotenv()

from langchain_mistralai import ChatMistralAI
from langchain_core.messages import SystemMessage, HumanMessage

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

messages = [
    SystemMessage(content=system_prompt)
]

while True:
    user_input = input("User: ")
    messages.append(HumanMessage(content=user_input))

    response = model.invoke(messages)
    print("Assistant:", response.content)

    messages.append(response)