import streamlit as st
from openai import OpenAI
from datetime import datetime
import os
import json

### DEFINE FUNCTIONS ###
def disable():
    """Rerun the Streamlit app and disable user input."""
    if not st.session_state.disabled:
        st.session_state.disabled = True
    
def download_chat() -> str:
    """Return chat history as a string."""
    try:
        history = "\n\n".join(f"{m['role']}: {m['content']}" for m in st.session_state.messages)
        
        prefix = f"Chat with {st.session_state.name}\n\n"
        model = f"Model: {st.session_state['openai_model']}\n"
        temperature = f"Temperature: {st.session_state['openai_temperature']}\n\n"
        
        return prefix + model + temperature + "##################\n\n" + history
    except AttributeError:
        return ""
    
def create_chat_name_download(base_name="Chat") -> str:
    """Return a unique filename for a chat download."""
    return f"{base_name} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.txt"

def save_chat_history(path = "chats"):
    """Save chat history to a text file."""
    path = os.path.join(os.getcwd(), path)
    
    if not os.path.exists(path):
        os.makedirs(path)
    
    with open(os.path.join(path, st.session_state.name + ".txt"), "w") as f:
        f.write(download_chat())
        
    print(f"Chat history saved to {os.path.join(path, st.session_state.name + '.txt')}")

### INITIALIZE APP ###

# read config file
config = json.load(open(".streamlit/config.json"))

# Set OpenAI API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Initialize session state variables
if 'name' not in st.session_state:
    st.session_state.name = None
if 'disabled' not in st.session_state:
    st.session_state.disabled = False
if 'messages' not in st.session_state:
    st.session_state.messages = []

### DEFINE APP LAYOUT ###
st.title("ChatGPT 🤖🗨️")

### DEFINE APP BEHAVIOR ###

# A text input where the user can input its name
st.session_state.name = st.text_input("What's your name?",
                                        value="",
                                        disabled=st.session_state.disabled,
                                        on_change=disable)
        
# Display chat messages from history on app rerun
if st.session_state.name and st.session_state.disabled:
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input(f"Hello {st.session_state.name}! 👋", disabled=False):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
            
    # Display assistant response in chat message container
        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                temperature=st.session_state["openai_temperature"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True
            )
            response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
            save_chat_history()


# Define sidebar where user can select model and temperature
if config["sidebar_show"]:
    with st.sidebar:
        st.image("./static/Universitaet-st-gallen.svg")
        
        #add some vertical space here
        st.write("")
        
        # create a button to clear the chat history
        if st.button("Delete Chat"):
            st.session_state.messages = []
            st.rerun()
            
        st.download_button(
            "Download Chat History",
            data=download_chat(),
            file_name=create_chat_name_download(),
            mime="text/plain"
        )
        
        st.subheader("Model")
        st.session_state["openai_model"] = st.selectbox(
            "Choose a GPT Model:",
            ["gpt-3.5-turbo", "gpt-4"]
        )
        
        st.subheader("Temperatur")
        st.session_state["openai_temperature"] = st.slider(
            "How 'creative' should the AI be? 🎨",
            **config["temperature"]
        )
        
else:
    st.session_state["openai_model"] = config["gpt_model_default"]
    st.session_state["openai_temperature"] = config["temperature"]["value"]
