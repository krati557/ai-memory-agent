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

