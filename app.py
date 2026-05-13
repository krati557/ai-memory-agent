# =========================
# IMPORTS
# =========================
import streamlit as st
from openai import OpenAI

import subprocess
import tempfile
import json
import os
import time
import base64

from datetime import datetime

from duckduckgo_search import DDGS

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


# =========================
# OPENAI CLIENT
# =========================
client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Autonomous AI Agent",
    page_icon="🤖",
    layout="wide"
)

# =========================
# CHAT STORAGE
# =========================
CHAT_FOLDER = "chats"

if not os.path.exists(CHAT_FOLDER):
    os.makedirs(CHAT_FOLDER)

# =========================
# SESSION STATE
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_id" not in st.session_state:
    st.session_state.chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")

if "current_project" not in st.session_state:
    st.session_state.current_project = "general"

# =========================
# SAVE CHAT
# =========================
def save_chat():

    filename = f"{CHAT_FOLDER}/{st.session_state.chat_id}.json"

    data = {
        "project": st.session_state.current_project,
        "messages": st.session_state.messages
    }

    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

# =========================
# LOAD CHATS
# =========================
def load_chats():

    chats = []

    for file in os.listdir(CHAT_FOLDER):

        if file.endswith(".json"):
            chats.append(file)

    return sorted(chats, reverse=True)

# =========================
# LOAD SINGLE CHAT
# =========================
def load_chat_file(filename):

    with open(f"{CHAT_FOLDER}/{filename}", "r") as f:

        data = json.load(f)

    if isinstance(data, dict):
        return data.get("messages", [])

    return data

# =========================
# MEMORY
# =========================
def retrieve_project_memory(prompt):

    memories = []

    keywords = prompt.lower().split()

    for file in load_chats():

        try:

            msgs = load_chat_file(file)

            for msg in msgs:

                content = msg["content"].lower()

                score = 0

                for word in keywords:

                    if word in content:
                        score += 1

                if score >= 2:
                    memories.append(msg["content"])

        except:
            pass

    return memories[-10:]

# =========================
# IMAGE ANALYSIS
# =========================
def analyze_image(uploaded_file, prompt):

    image_bytes = uploaded_file.read()

    base64_image = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    response = client.chat.completions.create(

        model="gpt-4.1-mini",

        messages=[
            {
                "role": "user",
                "content": [

                    {
                        "type": "text",
                        "text": prompt
                    },

                    {
                        "type": "image_url",
                        "image_url": {
                            "url":
                            f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
    )

    return response.choices[0].message.content

# =========================
# TOOL ROUTER
# =========================
def decide_tool(prompt):

    router_prompt = f"""
You are an AI tool selector.

Tools:
1. web_search
2. autonomous_execution
3. normal_chat

Rules:
- latest info → web_search
- complex task → autonomous_execution
- otherwise → normal_chat

Prompt:
{prompt}

Return only:
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
                "content": "Tool router"
            },
            {
                "role": "user",
                "content": router_prompt
            }
        ]
    )

    return response.choices[0].message.content.strip()

# =========================
# AUTONOMOUS EXECUTION
# =========================
def autonomous_execution_agent(task):

    response = client.chat.completions.create(

        model="gpt-4.1-mini",

        messages=[
            {
                "role": "system",
                "content": "You are autonomous AI planner."
            },
            {
                "role": "user",
                "content": task
            }
        ]
    )

    return response.choices[0].message.content

# =========================
# DAILY REPORT
# =========================
def generate_daily_report():

    history = ""

    for msg in st.session_state.messages:

        history += (
            f"{msg['role']}: "
            f"{msg['content']}\n"
        )

    response = client.chat.completions.create(

        model="gpt-4.1-mini",

        messages=[
            {
                "role": "system",
                "content": "Generate work summary."
            },
            {
                "role": "user",
                "content": history
            }
        ]
    )

    return response.choices[0].message.content

# =========================
# BROWSER AGENT
# =========================
def browser_agent(task):

    options = Options()

    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    result = ""

    try:

        driver.get("https://www.google.com")

        time.sleep(2)

        search_box = driver.find_element(
            By.NAME,
            "q"
        )

        search_box.send_keys(task)

        search_box.send_keys(Keys.RETURN)

        time.sleep(3)

        links = driver.find_elements(
            By.TAG_NAME,
            "h3"
        )

        if links:

            links[0].click()

            time.sleep(3)

        buttons = driver.find_elements(
            By.TAG_NAME,
            "button"
        )

        for btn in buttons[:3]:

            try:
                btn.click()
                time.sleep(1)
            except:
                pass

        inputs = driver.find_elements(
            By.TAG_NAME,
            "input"
        )

        for inp in inputs:

            try:
                inp.send_keys("AI Agent")
            except:
                pass

        driver.save_screenshot("browser.png")

        result = driver.page_source[:7000]

    except Exception as e:

        result = str(e)

    driver.quit()

    return result

# =========================
# TITLE
# =========================
st.title("🤖 Autonomous AI Agent")

# =========================
# SIDEBAR
# =========================
with st.sidebar:

    st.title("💬 Menu")

    if st.button("➕ New Chat"):

        st.session_state.messages = []

        st.session_state.chat_id = (
            datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )
        )

        st.rerun()

    st.divider()

    search = st.text_input(
        "🔍 Search Chats"
    )

    st.divider()

    st.subheader("🕘 Previous Chats")

    all_chats = load_chats()

    filtered_chats = [

        c for c in all_chats

        if search.lower() in c.lower()
    ]

    if filtered_chats:

        for chat_file in filtered_chats:

            chat_name = (
                chat_file.replace(".json", "")
            )

            if st.button(
                f"💬 {chat_name}"
            ):

                st.session_state.messages = (
                    load_chat_file(chat_file)
                )

                st.session_state.chat_id = (
                    chat_name
                )

                st.rerun()

    else:

        st.write("No chats found")

# =========================
# CAPTION
# =========================
st.caption(
    "Chat • Memory • Browser Agent • Code Runner"
)

# =========================
# SHOW CHATS
# =========================
for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        st.markdown(msg["content"])

# =========================
# FILE UPLOAD
# =========================
uploaded_file = st.file_uploader(

    "Upload Image or File",

    type=[
        "png",
        "jpg",
        "jpeg",
        "pdf",
        "txt",
        "py",
        "java",
        "js"
    ]
)

# =========================
# USER INPUT
# =========================
prompt = st.chat_input(
    "Ask anything..."
)

# =========================
# MAIN
# =========================
if prompt:

    # IMAGE ANALYSIS
    if uploaded_file is not None:

        if "image" in uploaded_file.type:

            st.image(uploaded_file, width=300)

            image_result = analyze_image(
                uploaded_file,
                prompt
            )

            with st.chat_message("assistant"):

                st.markdown(image_result)

            st.session_state.messages.append({
                "role": "assistant",
                "content": image_result
            })

            save_chat()

            st.stop()

    # PROJECT DETECTION
    st.session_state.current_project = (
        prompt.split()[0]
    )

    # SAVE USER MESSAGE
    st.session_state.messages.append({

        "role": "user",
        "content": prompt
    })

    save_chat()

    # SHOW USER
    with st.chat_message("user"):

        st.markdown(prompt)

    # =========================
    # BROWSER AGENT
    # =========================
    if any(x in prompt.lower() for x in [

        "open website",
        "browser",
        "login",
        "fill form",
        "search website",
        "click website",
        "open browser"

    ]):

        with st.spinner(
            "Browser Agent Running..."
        ):

            browser_result = browser_agent(
                prompt
            )

            st.session_state.messages.append({

                "role": "assistant",
                "content": browser_result
            })

            save_chat()

            with st.chat_message("assistant"):

                st.markdown(browser_result)

                if os.path.exists(
                    "browser.png"
                ):

                    st.image("browser.png")

        st.stop()

    # =========================
    # DAILY REPORT
    # =========================
    if "what did i do today" in prompt.lower():

        report = generate_daily_report()

        st.session_state.messages.append({

            "role": "assistant",
            "content": report
        })

        save_chat()

        with st.chat_message("assistant"):

            st.markdown(report)

        st.stop()

    # =========================
    # TOOL ROUTER
    # =========================
    selected_tool = decide_tool(prompt)

    # =========================
    # WEB SEARCH
    # =========================
    if selected_tool == "web_search":

        results = []

        with DDGS() as ddgs:

            for r in ddgs.text(
                prompt,
                max_results=5
            ):

                results.append(

                    f"### {r['title']}\n"
                    f"{r['body']}\n"
                    f"{r['href']}"
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

    # =========================
    # AUTONOMOUS EXECUTION
    # =========================
    elif (
        selected_tool
        ==
        "autonomous_execution"
    ):

        result = autonomous_execution_agent(
            prompt
        )

        st.session_state.messages.append({

            "role": "assistant",
            "content": result
        })

        save_chat()

        with st.chat_message("assistant"):

            st.markdown(result)

        st.stop()

    # =========================
    # NORMAL CHAT
    # =========================
    memories = retrieve_project_memory(
        prompt
    )

    memory_context = "\n".join(memories)

    system_prompt = f"""
You are an autonomous AI coding assistant.

Previous Memories:
{memory_context}

Rules:
- Generate complete code
- Use executable code
- Use triple backticks
"""

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

    reply = (
        response
        .choices[0]
        .message
        .content
    )

    # SAVE AI
    st.session_state.messages.append({

        "role": "assistant",
        "content": reply
    })

    save_chat()

    # SHOW AI
    with st.chat_message("assistant"):

        st.markdown(reply)

        # =========================
        # CODE RUNNER
        # =========================
        if "```" in reply:

            try:

                block = reply.split(
                    "```"
                )[1]

                language = (
                    block.split("\n")[0]
                    .strip()
                )

                code = (
                    block.split(
                        "\n",
                        1
                    )[1]
                )

                code = code.rsplit(
                    "```",
                    1
                )[0]

                st.code(
                    code,
                    language=language
                )

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

                        output = (
                            result.stdout
                            +
                            result.stderr
                        )

                    # JAVASCRIPT
                    elif language in [
                        "javascript",
                        "js"
                    ]:

                        with open(
                            "temp.js",
                            "w"
                        ) as f:

                            f.write(code)

                        result = subprocess.run(

                            ["node", "temp.js"],

                            input=user_input + "\n",

                            capture_output=True,

                            text=True
                        )

                        output = (
                            result.stdout
                            +
                            result.stderr
                        )

                    # JAVA
                    elif language == "java":

                        with open(
                            "Main.java",
                            "w"
                        ) as f:

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

                        output = (
                            result.stdout
                            +
                            result.stderr
                        )

                    else:

                        output = (
                            "Language not supported yet"
                        )

                    st.markdown("### Output")

                    st.code(output)

            except Exception as e:

                st.error(str(e))

