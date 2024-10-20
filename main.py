import streamlit as st
from typing import Generator
from groq import Groq

# Custom settings
chatbot_name = "WetaAI"
assistant_avatar = "🤖"
user_avatar = "👨‍💻"
default_max_tokens = 8192  # Set default token limit for the model




# Page setup
st.set_page_config(page_icon="💬", layout="centered", page_title=f"{chatbot_name} Chatbot")


# HTML for a styled back icon
back_icon_html = '<a href="http://127.0.0.1:8000/" onclick="history.back();"><span style="font-size: 16px;color:grey">◀️ Back</span></a>'

# Display the back icon
st.markdown(back_icon_html, unsafe_allow_html=True)


# Function for custom page icon
def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(f'<span style="font-size: 78px; line-height: 1">{emoji}</span>', unsafe_allow_html=True)

# Display custom emoji icon
# icon("🏎️")




st.subheader(f"{chatbot_name} Chatbot", divider="gray", anchor=False)


# Set up the Groq client
client = Groq(api_key="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")

# Predefined model
model_option = "llama3-8b-8192"  # No need to let the user choose, it's fixed

# Initialize chat history if not already present
if "messages" not in st.session_state:
    st.session_state.messages = []

# Set a static value for max tokens, or remove the slider completely
max_tokens_range = default_max_tokens  # Fixed token limit for llama3-8b-8192
max_tokens = max_tokens_range  # Set to default

# Display chat messages from history
for message in st.session_state.messages:
    avatar = assistant_avatar if message["role"] == "assistant" else user_avatar
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Generate chat responses function
def generate_chat_responses(chat_completion) -> Generator[str, None, None]:
    """Yield chat response content from the Groq API response."""
    for chunk in chat_completion:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

# Initialize response storage
full_response = ""

# Accept user input
if prompt := st.chat_input(f"Ask {chatbot_name} anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user", avatar=user_avatar):
        st.markdown(prompt)

    # Fetch response from Groq API
    try:
        chat_completion = client.chat.completions.create(
            model=model_option,
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            max_tokens=max_tokens,
            stream=True  # Stream output in real-time
        )

        # Display WetaAI's response
        with st.chat_message("assistant", avatar=assistant_avatar):
            chat_responses_generator = generate_chat_responses(chat_completion)
            full_response = st.write_stream(chat_responses_generator)

    except Exception as e:
        st.error(e, icon="🚨")

    # Append WetaAI's response to the chat history
    if isinstance(full_response, str):
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    else:
        combined_response = "\n".join(str(item) for item in full_response)
        st.session_state.messages.append({"role": "assistant", "content": combined_response})


if st.button("Clear"):
    # Navigate back (clear messages) and attempt to close the window
    st.session_state.messages.clear()
    st.markdown(
        """
        <script>
            window.close();
        </script>
        """,
        unsafe_allow_html=True
    )