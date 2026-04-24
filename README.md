Omdena Team 3 — Voice & Chat Prototype (Week 1)
Project Overview

This is a simple chat prototype made for the Omdena Bhutan project.

In Week 1, our goal was:

To build a basic chat UI
To connect an AI model
To test simple message input and response

Right now, this is only a basic prototype. It does not have advanced features yet.

Tech Stack
Python
Streamlit
LangChain
Mistral AI API
python-dotenv
Project Structure
omdena-team3-prototype/
 ├── chatbot.py
 ├── requirements.txt
 ├── tool_comparison.md
 ├── architecture.md
 ├── team_log.md
 └── README.md
How to Run the Project
1. Install requirements
pip install -r requirements.txt
2. Add API key

Create a .env file and add:

MISTRAL_API_KEY=your_api_key_here
3. Run the app
streamlit run chatbot.py
What This Project Does (Week 1)
Shows a simple chat screen
Takes user message
Sends message to AI model
Shows AI response on screen
What This Project Does NOT Have Yet
No conversation flow
No smart routing or classifier
No voice input
No advanced AI logic
What We Will Do Next
Week 2
Use conversation design from Team 2
Make chatbot replies more structured
Improve prompts
Week 3
Connect classifier from Team 4
Make full working system
Improve UI for demo
What We Learned

In Week 1, we learned:

How to build a simple chat app
How to connect AI to a web UI
How to test basic input and output
How to prepare project structure for future work
