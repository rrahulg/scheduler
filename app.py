import streamlit as st
from phi.agent import RunResponse

from src.agents import agent  # your configured agent instance

st.set_page_config(page_title="Scheduling Agent", page_icon="🗓️")
st.title("📅 Google Calendar Assistant")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Input box at bottom
prompt = st.chat_input("Ask me to schedule or search events...")

# Display existing chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle new user input
if prompt:
    st.chat_message("user").markdown(prompt)
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        try:
            response: RunResponse = agent.run(prompt)
            output = response.content
        except Exception as e:
            output = f"❌ Error: {str(e)}"
        st.markdown(output)
        st.session_state.chat_history.append({"role": "assistant", "content": output})
