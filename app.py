import streamlit as st
from openai import OpenAI

import subprocess
import tempfile
import json
import os
import time
import base64

from datetime import datetime
from PIL import Image

from duckduckgo_search import DDGS

from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC







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

    chat_data = {
        "project": st.session_state.current_project,
        "messages": st.session_state.messages
    }

    with open(filename, "w") as f:
        json.dump(chat_data, f, indent=2)

# =========================
# LOAD CHATS
# =========================
def load_chats():

    chats = []

    if os.path.exists(CHAT_FOLDER):

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
# SMART MEMORY
# =========================
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
def analyze_image(uploaded_file, user_prompt):

    image_bytes = uploaded_file.read()

    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
    )

    return response.choices[0].message.content

# =========================

# =========================

       

# =========================
# ADVANCED AI AGENT
# =========================
def browser_agent(task):

    options = Options()

    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    result = ""
    attempt_logs = []

    try:

        # OPEN GOOGLE
        driver.get("https://www.google.com")

        time.sleep(2)

        # SEARCH BOX
        search_box = driver.find_element(By.NAME, "q")

        search_box.send_keys(task)

        search_box.send_keys(Keys.RETURN)

        time.sleep(3)

        # CLICK FIRST RESULT
        links = driver.find_elements(By.TAG_NAME, "h3")

        if links:

            links[0].click()

            time.sleep(3)

        # AUTO BUTTON CLICK
        buttons = driver.find_elements(By.TAG_NAME, "button")

        for btn in buttons[:3]:

            try:

                btn.click()

                time.sleep(1)

            except:
                pass

        # AUTO FORM FILL
        inputs = driver.find_elements(By.TAG_NAME, "input")

        for inp in inputs:

            try:

                inp.send_keys("AI Agent")

            except:
                pass

        # SCREENSHOT
        driver.save_screenshot("browser.png")

        # PAGE DATA
        result = driver.page_source[:7000]


        driver.save_screenshot("browser.png")



    except Exception as e:

        result = str(e)

    driver.quit()

    return result



# TOOL ROUTER
# =========================
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

# =========================
# AUTONOMOUS EXECUTION
# =========================
def autonomous_execution_agent(task):

    planner_prompt = f"""
Break the user's task into executable steps.

TASK:
{task}
"""

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

    return f"""
# 🧠 PLAN

{plan}
"""

# =========================
# DAILY REPORT
# =========================
def generate_daily_report():

    all_text = ""

    for msg in st.session_state.messages:

        role = msg["role"]
        content = msg["content"]

        all_text += f"{role}: {content}\n"

    report_prompt = f"""
Analyze today's chat history.

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

# =========================
# TITLE
# =========================
st.title("🤖 Autonomous AI Agent")

# =========================
# SIDEBAR
# =========================
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

# =========================
# CAPTION
# =========================
st.caption(
    "Chat • Autonomous AI • Memory • Code Runner • Web Search"
)

# =========================
# SHOW CHATS
# =========================
for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        st.markdown(msg["content"])


# =========================
# FILE UPLOADER
# =========================
uploaded_file = st.file_uploader(
    "Upload Image or File",
    type=["png", "jpg", "jpeg", "pdf", "txt", "py", "java", "js"]
)
# USER INPUT
# =========================
prompt = st.chat_input("Ask anything...")

# =========================
# MAIN LOGIC
# =========================
if prompt:

    if uploaded_file is not None:

        file_type = uploaded_file.type

        if "image" in file_type:

            st.image(uploaded_file, width=300)

            result = analyze_image(
                uploaded_file,
                prompt
            )

            st.write(result)

            st.stop()

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

    # =========================
   
# =========================
# REAL BROWSER AGENT
# =========================
if prompt and any(x in prompt.lower() for x in [

    "open website",
    "login",
    "fill form",
    "upload file",
    "browser",
    "search website",
    "click website"

]):

    with st.spinner("AI Browser Agent Running..."):

        browser_result = browser_agent(prompt)

        st.session_state.messages.append({
            "role": "assistant",
            "content": browser_result
        })

        with st.chat_message("assistant"):

            st.markdown(browser_result)

    st.stop()


    # =========================
# BROWSER TASK
# =========================
if prompt and (
    "open browser" in prompt.lower()
    or
    "search website" in prompt.lower()
):

    with st.spinner("Browser Agent Running..."):

        browser_result = browser_agent(prompt)

        st.write(browser_result)

    st.stop()
    # DAILY REPORT
    # =========================
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

    # =========================
    # WEB SEARCH
    # =========================
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

    # =========================
    # AUTONOMOUS EXECUTION
    # =========================
    elif selected_tool == "autonomous_execution":

        with st.spinner("AI Autonomous Execution..."):

            result = autonomous_execution_agent(prompt)

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
    system_prompt = """
You are an autonomous AI coding assistant.

IMPORTANT:
- Always generate executable code
- Always generate complete code
- Use input() for user input
- Never hardcode values
- Put code inside triple backticks
"""

    memories = retrieve_project_memory(prompt)

    memory_context = "\n".join(memories)

    # =========================
    # AI RESPONSE
    # =========================
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

    # =========================
    # SHOW RESPONSE
    # =========================
    with st.chat_message("assistant"):

        st.markdown(reply)

        # =========================
        # CODE DETECTION
        # =========================
        if reply and "```" in reply:

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

                    # =========================
                    # PYTHON
                    # =========================
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

                    # =========================
                    # JAVASCRIPT
                    # =========================
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

                    # =========================
                    # JAVA
                    # =========================
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

                    else:
                        output = "Language not supported yet"

                    st.markdown("### Output")

                    st.code(output)

            except Exception as e:

                st.error(str(e))