import streamlit as st
from main import ask_llm


st.set_page_config(
    page_title="AI Tool-Calling Demo",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 AI Tool-Calling Assistant")
st.caption(
    "Weather • News • Crypto • Forex • Fun Facts • Jokes • Advice • Memes • Dictionary • IP Info • Cats & Dogs"
)

# Keep chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


def render_message(role, content):
    """Render user or assistant messages without nesting chat_message blocks."""
    msg = st.chat_message(role)

    if isinstance(content, dict):
        # Handle image tools
        if "image_url" in content:
            msg.image(content["image_url"], caption=content.get("title", None))

        # Show details (JSON)
        msg.json(content)

    elif isinstance(content, list):
        msg.json(content)

    else:
        msg.markdown(str(content))


# REPLAY ALL PAST MESSAGES
for msg in st.session_state.messages:
    render_message(msg["role"], msg["content"])

# USER INPUT
user_input = st.chat_input("Ask me anything...")

if user_input:
    # Save + show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    render_message("user", user_input)

    # Process assistant reply
    with st.spinner("Thinking..."):
        result = ask_llm(user_input)

    st.session_state.messages.append({"role": "assistant", "content": result})

    # Render assistant output
    render_message("assistant", result)