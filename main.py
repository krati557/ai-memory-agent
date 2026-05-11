from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

MEMORY_FILE = "memory.json"

# Load memory
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r") as f:
        memory = json.load(f)
else:
    memory = []

print("🤖 AI Agent Started")

while True:

    user = input("\nYou: ")

    if user == "exit":
        break

    old_context = "\n".join(memory)

    prompt = f"""
Previous Memory:
{old_context}

User Question:
{user}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a coding assistant with memory."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    ai_response = response.choices[0].message.content

    print("\nAI:")
    print(ai_response)

    # Save memory
    memory.append(f"User: {user}")
    memory.append(f"AI: {ai_response}")

    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)