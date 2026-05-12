````python
import streamlit as st
from openai import OpenAI
import subprocess
import tempfile
from duckduckgo_search import DDGS
import pandas as pd

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

# MEMORY
if "messages" not in st.session_state:
    st.session_state.messages = []

# TITLE
st.title("🤖 Autonomous AI Agent")

# SIDEBAR
with st.sidebar:

    st.title("💬 Menu")

    # NEW CHAT
    if st.button("➕ New Chat"):

        st.session_state.messages = []

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

    if st.session_state.messages:

        for i, msg in enumerate(
            st.session_state.messages
        ):

            if msg["role"] == "user":

                preview = msg["content"][:30]

                st.write(f"💬 {preview}")

    else:

        st.write("No chats yet")

    st.divider()

    # MORE
    st.subheader("⚙ More")

    st.write("👤 Profile")
    st.write("🌙 Dark Mode")
    st.write("⚡ Settings")

st.caption(
    "Chat • Generate Code • Run Code • Take User Input"
)

# AUTONOMOUS AI AGENT
def autonomous_agent(task):

    autonomous_prompt = f"""
You are an advanced autonomous AI agent.

Your job:
1. Understand the user's task
2. Break the task into steps
3. Think step-by-step
4. Research if needed
5. Give final detailed answer

USER TASK:
{task}

IMPORTANT:
- Be autonomous
- Think carefully
- Give detailed output
- If coding is needed, generate complete executable code
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

# SHOW OLD CHATS
for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# USER INPUT
prompt = st.chat_input("Ask anything...")

# WEB SEARCH MODE
if prompt and "search" in prompt.lower():

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

        with st.chat_message("assistant"):

            st.markdown(final_result)

    st.stop()

if prompt:

    # AUTONOMOUS MODE
    if "research" in prompt.lower():

        with st.spinner("AI Agent Thinking..."):

            result = autonomous_agent(prompt)

            st.write(result)

        st.stop()

    # SAVE USER MESSAGE
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # SHOW USER MESSAGE
    with st.chat_message("user"):
        st.markdown(prompt)

    system_prompt = """
You are an autonomous AI coding agent.

IMPORTANT:
- Always generate executable code
- Always give complete code
- Always take input from user using input()
- Never hardcode values

- Never say:
    - run locally
    - use your IDE
    - I cannot run code

- Always put code inside triple backticks

If user asks normal questions or translations,
respond normally without code.

Generate code ONLY when user explicitly asks:
- create code
- write program
- build app
- coding task
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
                            input=user_input,
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
                            input=user_input,
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
                            input=user_input,
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
````
