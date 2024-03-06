import streamlit as st
from openai import OpenAI

st.title("ChatGPT 🤖🗨️")

# Set OpenAI API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Define sidebar where user can select model and temperature
with st.sidebar:
    st.image("./static/Universitaet-st-gallen.svg")
    
    #add some vertical space here
    st.write("")
    
    # create a button to clear the chat history
    if st.button("Chat löschen"):
        st.session_state.messages = []
        st.experimental_rerun()
        
    # create a button to download the chat history
    st.download_button(
        "Chatverlauf herunterladen",
        "\n".join(f"{m['role']}: {m['content']}" for m in st.session_state.messages),
        file_name="chat.txt",
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
    


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

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
    
    
