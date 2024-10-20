import os
import json

import streamlit as st
from groq import Groq


# streamlit page conf

st.set_page_config(
    page_title= "Geoffrey Weta Ai Chatbot",
    page_icon= "😋",
    layout= "wide"
)


working_dir = os.path.dirname(os.path.abspath(__file__))
config_data = json.load(open(f"{working_dir}/config.json"))

GROQ_API_KEY = config_data["GROQ_API_KEY"]



# Save the api key in the environment variable

os.environ["GROQ_API_KEY"] = GROQ_API_KEY

client = Groq()


# Initialise the Chat history as Streamlit session

if "chat_history" not in st.session_state :
    st.session_state.chat_histor = []

# Streamlit page title
