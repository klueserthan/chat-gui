import streamlit as st
from openai import OpenAI
from datetime import datetime

### DEFINE FUNCTIONS ###
def download_chat() -> str:
    """Return chat history as a string."""
    try:
        history = "\n".join(f"{m['role']}: {m['content']}" for m in st.session_state.messages)
        return history
    except AttributeError:
        return ""
    
def create_chat_name_download(base_name="Chat") -> str:
    """Return a unique filename for a chat download."""
    return f"{base_name} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.txt"

### INITIALIZE APP ###
# Set OpenAI API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

### DEFINE APP LAYOUT ###
st.title("ChatGPT 🤖🗨️")

### DEFINE APP BEHAVIOR ###

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Hallo! 👋"):
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
            stream=True,
        )
        response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})


# Define sidebar where user can select model and temperature
with st.sidebar:
    st.image("./static/Universitaet-st-gallen.svg")
    
    #add some vertical space here
    st.write("")
    
    # create a button to clear the chat history
    if st.button("Chat löschen"):
        st.session_state.messages = []
        st.rerun()
        
    st.download_button(
        "Chatverlauf herunterladen",
        data=download_chat(),
        file_name=create_chat_name_download(),
        mime="text/plain",
    )
    
    st.subheader("Modell")
    st.session_state["openai_model"] = st.selectbox(
        "Wählen Sie ein Modell aus:",
        ["gpt-3.5-turbo", "gpt-4"]
    )
    
    st.subheader("Temperatur")
    st.session_state["openai_temperature"] = st.slider(
        "Wie 'kreativ' soll die Antwort sein?",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
    )
