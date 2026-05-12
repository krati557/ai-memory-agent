import streamlit as st
from openai import OpenAI
import subprocess
import tempfile
from duckduckgo_search import DDGS
import json
import os
from datetime import datetime

# OPENAI CLIENT
client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

# PAGE
st.set_page_config(
    page_title="AI Agent",
    page_icon="🤖",
    layout="wide"
)

# CHAT STORAGE
CHAT_FOLDER = "chats"

if not os.path.exists(CHAT_FOLDER):
    os.makedirs(CHAT_FOLDER)

# SESSION
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_id" not in st.session_state:
    st.session_state.chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")

# SAVE CHAT
def save_chat():

    filename = f"{CHAT_FOLDER}/{st.session_state.chat_id}.json"

    with open(filename, "w") as f:

        json.dump(
            st.session_state.messages,
            f,
            indent=2
        )

# LOAD CHATS
def load_chats():

    chats = []

    if os.path.exists(CHAT_FOLDER):

        for file in os.listdir(CHAT_FOLDER):

            if file.endswith(".json"):

                chats.append(file)

    return sorted(chats, reverse=True)

# LOAD SINGLE CHAT
def load_chat_file(filename):

    with open(f"{CHAT_FOLDER}/{filename}", "r") as f:

        return json.load(f)

# AUTONOMOUS AI AGENT
def autonomous_agent(task):

    autonomous_prompt = f"""
You are an advanced autonomous AI agent.

Your job:
1. Understand the user's task
2. Break the task into steps
3. Think step-by-step
4. Research if needed
5. Give detailed final answer

USER TASK:
{task}

IMPORTANT:
- Be autonomous
- Think carefully
- Give detailed output
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an autonomous AI agent."
            },
            {
                "role": "user",
                "content": autonomous_prompt
            }
        ]
    )

    return response.choices[0].message.content

# DAILY REPORT FUNCTION
def generate_daily_report():

    all_text = ""

    for msg in st.session_state.messages:

        role = msg["role"]

        content = msg["content"]

        all_text += f"{role}: {content}\n"

    report_prompt = f"""
You are an AI productivity assistant.

Analyze today's chat history and generate a professional daily work report.

Include:
- Tasks completed
- Features implemented
- Problems solved
- Technologies used
- Progress summary

CHAT HISTORY:
{all_text}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "You generate professional work reports."
            },
            {
                "role": "user",
                "content": report_prompt
            }
        ]
    )

    return response.choices[0].message.content

# TITLE
st.title("🤖 Autonomous AI Agent")

# SIDEBAR
with st.sidebar:

    st.title("💬 Menu")

    # NEW CHAT
    if st.button("➕ New Chat"):

        st.session_state.messages = []

        st.session_state.chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        st.rerun()

    st.divider()

    # SEARCH
    search = st.text_input(
        "🔍 Search Chats"
    )

    st.divider()

    # PROJECTS
    st.subheader("📁 Projects")

    st.write("• AI Assistant")
    st.write("• Code Runner")
    st.write("• Java Compiler")

    st.divider()

    # PREVIOUS CHATS
    st.subheader("🕘 Previous Chats")

    all_chats = load_chats()

    filtered_chats = [
        c for c in all_chats
        if search.lower() in c.lower()
    ]

    if filtered_chats:

        for chat_file in filtered_chats:

            chat_name = chat_file.replace(".json", "")

            if st.button(chat_name):

                st.session_state.messages = load_chat_file(chat_file)

                st.session_state.chat_id = chat_name

                st.rerun()

    else:

        st.write("No chats found")

    st.divider()

    # MORE
    st.subheader("⚙ More")

    st.write("👤 Profile")
    st.write("🌙 Dark Mode")
    st.write("⚡ Settings")

st.caption(
    "Chat • Generate Code • Run Code • Web Search • Daily Reports"
)

# SHOW OLD CHATS
for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# USER INPUT
prompt = st.chat_input("Ask anything...")

if prompt:

    # SAVE USER MESSAGE
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    save_chat()

    # SHOW USER MESSAGE
    with st.chat_message("user"):
        st.markdown(prompt)

    # DAILY REPORT MODE
    if "what did i do today" in prompt.lower() or "aaj mene kya kiya" in prompt.lower():

        with st.spinner("Generating Daily Report..."):

            report = generate_daily_report()

            st.session_state.messages.append({
                "role": "assistant",
                "content": report
            })

            save_chat()

            with st.chat_message("assistant"):
                st.markdown(report)

        st.stop()

    # AUTONOMOUS MODE
    elif "research" in prompt.lower():

        with st.spinner("AI Agent Thinking..."):

            result = autonomous_agent(prompt)

            st.session_state.messages.append({
                "role": "assistant",
                "content": result
            })

            save_chat()

            with st.chat_message("assistant"):
                st.markdown(result)

        st.stop()

    # WEB SEARCH MODE
    elif "search" in prompt.lower():

        with st.spinner("Searching Web..."):

            results = []

            with DDGS() as ddgs:

                for r in ddgs.text(prompt, max_results=5):

                    results.append(
                        f"### {r['title']}\n"
                        f"{r['body']}\n"
                        f"{r['href']}\n"
                    )

            final_result = "\n\n".join(results)

            st.session_state.messages.append({
                "role": "assistant",
                "content": final_result
            })

            save_chat()

            with st.chat_message("assistant"):
                st.markdown(final_result)

        st.stop()

    # NORMAL AI CHAT
    system_prompt = """
You are an autonomous AI coding assistant.

IMPORTANT:
- Always generate executable code
- Always give complete code
- Always take input from user using input()
- Never hardcode values
- Never say run locally or use your IDE
- Put code inside triple backticks

If user asks normal questions,
respond normally.
"""

    # AI RESPONSE
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            *st.session_state.messages
        ]
    )

    reply = response.choices[0].message.content

    # SAVE AI MESSAGE
    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })

    save_chat()

    # SHOW AI MESSAGE
    with st.chat_message("assistant"):

        st.markdown(reply)

    
        # CODE DETECT
        if "```" in reply:

            try:

                block = reply.split("```")[1]

                language = block.split("\n")[0].strip()

                code = block.split("\n", 1)[1]

                code = code.rsplit("```", 1)[0]

                st.code(code, language=language)

                # INPUT BOX
                user_input = st.text_input(
                    "Enter Input",
                    key="input_box"
                )

                # RUN BUTTON
                if st.button("▶ Run Code"):

                    output = ""

                    # PYTHON
                    if language == "python":

                        with tempfile.NamedTemporaryFile(
                            suffix=".py",
                            delete=False,
                            mode="w"
                        ) as f:

                            f.write(code)

                            filename = f.name

                        result = subprocess.run(
                            ["python3", filename],
                            input=user_input + "\n",
                            capture_output=True,
                            text=True
                        )

                        output = result.stdout + result.stderr

                    # JAVA
                    elif language == "java":

                        with open("Main.java", "w") as f:
                            f.write(code)

                        subprocess.run(
                            ["javac", "Main.java"]
                        )

                        result = subprocess.run(
                            ["java", "Main"],
                            input=user_input + "\n",
                            capture_output=True,
                            text=True
                        )

                        output = result.stdout + result.stderr

                    # JAVASCRIPT
                    elif language in ["javascript", "js"]:

                        with open("temp.js", "w") as f:
                            f.write(code)

                        result = subprocess.run(
                            ["node", "temp.js"],
                            input=user_input + "\n",
                            capture_output=True,
                            text=True
                        )

                        output = result.stdout + result.stderr

                    else:

                        output = "Language not supported yet"

                    # SHOW OUTPUT
                    st.markdown("### Output")

                    st.code(output)

            except Exception as e:

                st.error(str(e))

