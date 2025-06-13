import base64
import os
import time

import speech_recognition as sr
import streamlit as st
from mutagen.wave import WAVE
from phi.agent import RunResponse
from src.agents import agent
from utils.voice import save


def play_audio(text):
    save(text)
    path = os.path.join(os.getcwd(), "data/output.wav")

    with open(path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode("utf-8")

    md = f"""
        <audio autoplay>
            <source src="data:audio/wav;base64,{b64}" type="audio/wav">
        </audio>
    """
    st.markdown(md, unsafe_allow_html=True)
    time.sleep(get_audio_duration(path))
    os.remove(path=path)


def get_audio_duration(file_path):
    audio = WAVE(file_path)
    return audio.info.length  # in seconds (float)


st.set_page_config(page_title="Scheduling Agent", page_icon="🗓️")
st.title("📅 Google Calendar Assistant")

# --- Initialize session state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Hello, how may I help you?"}
    ]

if "voice_mode" not in st.session_state:
    st.session_state.voice_mode = False  # False = off, True = on

# --- Toggle Button ---
if st.button(
    "🛑 Stop Voice" if st.session_state.voice_mode else "🎤 Voice Mode",
    use_container_width=True,
):
    st.session_state.voice_mode = not st.session_state.voice_mode
    st.rerun()

# --- Display chat history ---
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Text input (always available) ---
prompt = st.chat_input("Ask me to schedule or search events...")
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

# --- Voice Loop Logic ---
if st.session_state.voice_mode:
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        with st.spinner("🎙️ Listening..."):
            try:
                audio = recognizer.listen(
                    source,
                )
                voice_text = recognizer.recognize_google(audio)

                st.chat_message("user").markdown(voice_text)
                st.session_state.chat_history.append(
                    {"role": "user", "content": voice_text}
                )
            except sr.UnknownValueError:
                st.warning("Sorry, I couldn't understand you.")
                voice_text = None
            except sr.RequestError:
                st.error("Speech Recognition API error. Check your connection.")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")
        with st.spinner("🗣️ Speaking..."):
            with st.chat_message("assistant"):
                try:
                    response: RunResponse = agent.run(voice_text)
                    output = response.content
                    st.session_state.chat_history.append(
                    {"role": "assistant", "content": output}
                )
                    st.markdown(output)
                    play_audio(output)
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")


    st.rerun()
