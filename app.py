import streamlit as st
from openai import OpenAI
import subprocess
import tempfile
from duckduckgo_search import DDGS
import json
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup


# OPENAI CLIENT
client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

# PAGE CONFIG
st.set_page_config(
    page_title="Autonomous AI Agent",
    page_icon="🤖",
    layout="wide"
)

# CHAT STORAGE
CHAT_FOLDER = "chats"

if not os.path.exists(CHAT_FOLDER):
    os.makedirs(CHAT_FOLDER)

# SESSION STATE
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_id" not in st.session_state:
    st.session_state.chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")

if "current_project" not in st.session_state:
    st.session_state.current_project = "general"


    # SAVE CHAT
def save_chat():

        filename = f"{CHAT_FOLDER}/{st.session_state.chat_id}.json"

        chat_data = {
            "project": st.session_state.current_project,
            "messages": st.session_state.messages
        }

        with open(filename, "w") as f:

            json.dump(
                chat_data,
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

            data = json.load(f)

        if isinstance(data, dict):

            return data.get("messages", [])

        return data

    # SMART MEMORY
def retrieve_project_memory(prompt):

        relevant_memories = []

        all_chats = load_chats()

        keywords = prompt.lower().split()

        for chat_file in all_chats:

            try:

                chat_data = load_chat_file(chat_file)

                for msg in chat_data:

                    content = msg["content"].lower()

                    score = 0

                    for word in keywords:

                        if word in content:

                            score += 1

                    if score >= 2:

                        relevant_memories.append(msg["content"])

            except:
                pass

        return relevant_memories[-10:]

    # AUTONOMOUS AGENT
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

    # TOOL ROUTER
def decide_tool(prompt):

        router_prompt = f"""
    You are an AI tool selector.

    Available tools:
    1. web_search
    2. autonomous_execution
    3. normal_chat

    Rules:
    - If internet/latest info needed → web_search
    - If complex multi-step task → autonomous_execution
    - Otherwise → normal_chat

    USER PROMPT:
    {prompt}

    Return ONLY:
    web_search
    OR
    autonomous_execution
    OR
    normal_chat
    """

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a tool routing AI."
                },
                {
                    "role": "user",
                    "content": router_prompt
                }
            ]
        )

        return response.choices[0].message.content.strip()

    # TRUE AUTONOMOUS EXECUTION
def autonomous_execution_agent(task):

        planner_prompt = f"""
    You are an autonomous AI planner.

    Break the user's task into executable steps.

    TASK:
    {task}
    """

        # PLAN
        plan_response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI planner."
                },
                {
                    "role": "user",
                    "content": planner_prompt
                }
            ]
        )

        plan = plan_response.choices[0].message.content

        # EXECUTION
        execution_prompt = f"""
    Execute this plan carefully.

    PLAN:
    {plan}

    Provide:
    - reasoning
    - implementation
    - final answer
    """

        execute_response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a powerful AI executor."
                },
                {
                    "role": "user",
                    "content": execution_prompt
                }
            ]
        )

        final_output = execute_response.choices[0].message.content

        # REVIEW LOOP
        review_prompt = f"""
    Review this result.

    TASK:
    {task}

    RESULT:
    {final_output}

    Improve if needed.
    """

        review_response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI reviewer."
                },
                {
                    "role": "user",
                    "content": review_prompt
                }
            ]
        )

        reviewed_output = review_response.choices[0].message.content

        return f"""
    # 🧠 PLAN

    {plan}

    ---

    # ⚡ EXECUTION

    {reviewed_output}
    """

    # DAILY REPORT
def generate_daily_report():

        all_text = ""

        for msg in st.session_state.messages:

            role = msg["role"]
            content = msg["content"]

            all_text += f"{role}: {content}\n"

        report_prompt = f"""
    Analyze today's chat history.

    Generate:
    - Tasks completed
    - Features implemented
    - Problems solved
    - Technologies used
    - Summary

    CHAT HISTORY:
    {all_text}
    """

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You generate work reports."
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
        search = st.text_input("🔍 Search Chats")

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

                col1, col2 = st.columns([5, 1])

                # OPEN CHAT
                with col1:

                    if st.button(f"💬 {chat_name}", key=chat_name):

                        st.session_state.messages = load_chat_file(chat_file)

                        st.session_state.chat_id = chat_name

                        st.rerun()

                # DELETE CHAT
                with col2:

                    if st.button("❌", key=f"delete_{chat_name}"):

                        os.remove(f"{CHAT_FOLDER}/{chat_file}")

                        st.rerun()

        else:

            st.write("No chats found")

    # CAPTION
        st.caption(
        "Chat • Autonomous AI • Memory • Code Runner • Web Search"
    )

    # SHOW CHATS
        for msg in st.session_state.messages:

          with st.chat_message(msg["role"]):

            st.markdown(msg["content"])

    # USER INPUT
        prompt = st.chat_input("Ask anything...")

        if prompt:

        # PROJECT DETECTION
         detect_prompt = f"""
    Detect the project/topic name.

    PROMPT:
    {prompt}

    Return short project name only.
    """

        detect_response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You detect project names."
                },
                {
                    "role": "user",
                    "content": detect_prompt
                }
            ]
        )

        st.session_state.current_project = (
            detect_response
            .choices[0]
            .message
            .content
            .strip()
        )

        # SAVE USER MESSAGE
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        save_chat()

        # SHOW USER MESSAGE
        with st.chat_message("user"):

            st.markdown(prompt)

        # TOOL DECISION
        selected_tool = decide_tool(prompt)

        # DAILY REPORT
        if "what did i do today" in prompt.lower():

            with st.spinner("Generating report..."):

                report = generate_daily_report()

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": report
                })

                save_chat()

                with st.chat_message("assistant"):

                    st.markdown(report)

            st.stop()

        # WEB SEARCH
        if selected_tool == "web_search":

            with st.spinner("Searching web..."):

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

        # AUTONOMOUS EXECUTION
        elif selected_tool == "autonomous_execution":

            with st.spinner("AI Autonomous Execution..."):

                thinking_box = st.empty()

                thinking_box.info("🧠 Planning...")

                thinking_box.info("🌐 Researching...")

                thinking_box.info("⚡ Executing...")

                result = autonomous_execution_agent(prompt)

                thinking_box.success("✅ Completed")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result
                })

                save_chat()

                with st.chat_message("assistant"):

                    st.markdown(result)

            st.stop()

        # NORMAL CHAT
        system_prompt = """
    You are an autonomous AI coding assistant.

    IMPORTANT:
    - Always generate executable code
    - Always generate complete code
    - Use input() for user input
    - Never hardcode values
    - Put code inside triple backticks

    You can:
    - research
    - solve problems
    - generate code
    - think step-by-step
    """

        # MEMORY
        memories = retrieve_project_memory(prompt)

        memory_context = "\n".join(memories)

        

# AI RESPONSE
        response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "system",
            "content": f"""
Previous project memories:

{memory_context}

Use these memories while responding.
"""
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

# SHOW RESPONSE
        with st.chat_message("assistant"):

         st.markdown(reply)

    

# CODE DETECTION
if "```" in reply:

    try:

        block = reply.split("```")[1]

        language = block.split("\n")[0].strip()

        code = block.split("\n", 1)[1]

        code = code.rsplit("```", 1)[0]

        st.code(code, language=language)

        user_input = st.text_input(
            "Enter Input",
            key=f"input_{language}"
        )

        run_btn = st.button(
            "▶ Run Code",
            key=f"run_{language}"
        )

        if run_btn:

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

            st.markdown("### Output")

            st.code(output)

    except Exception as e:

        st.error(str(e))

