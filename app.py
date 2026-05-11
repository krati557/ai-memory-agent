import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

MEMORY_FILE = "memory.json"

# Load old memory
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r") as f:
        memory = json.load(f)
else:
    memory = []

st.title("🤖 AI Memory Agent")

user_input = st.text_input("Ask Something")

if st.button("Send"):

    old_context = "\n".join(memory)

    prompt = f"""
Previous Memory:
{old_context}

User Question:
{user_input}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an AI coding assistant with memory."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    ai_response = response.choices[0].message.content

    st.write(ai_response)

    # Save memory
    memory.append(f"User: {user_input}")
    memory.append(f"AI: {ai_response}")

    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)