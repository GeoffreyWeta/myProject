import streamlit as st
import requests
import os


HUGGINGFACE_TOKEN="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"


# Hugging Face API URL and Headers
API_URL = "https://api-inference.huggingface.co/models/facebook/musicgen-small"
headers = {"Authorization": "Bearer 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"}
# Function to query the model
def query_musicgen(prompt):
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
    if response.status_code == 200:
        return response.content
    else:
        st.error(f"Error {response.status_code}: {response.json()['error']}")
        return None

# Streamlit app UI
st.title("Music Generation AI")
# st.write("Generate music by entering a description.")

# Text input for prompt
prompt = st.text_input("Describe the music you'd like to generate:", 
                       value="afrobeats loop with amapiano drums")

# Generate button
if st.button("Generate Music"):
    with st.spinner("Generating audio..."):
        audio_bytes = query_musicgen(prompt)
        
        if audio_bytes:
            # Play audio using Streamlit
            st.audio(audio_bytes, format="audio/wav")
