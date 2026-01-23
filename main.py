import streamlit as st
from rag_system import rag_system
import time
# ye .env nu load karda api lan lai
from dotenv import load_dotenv

load_dotenv()

st.title("Welcome to the Chai Dashboard")
st.subheader("Ask your questions !")

def chat_stream(prompt):
    response = rag_system.get_response(prompt)
    for char in response:
        yield char
        time.sleep(0.02)


def save_feedback(index):
    st.session_state.history[index]["feedback"] = st.session_state[f"feedback_{index}"]


if "history" not in st.session_state:
    st.session_state.history = []

for i, message in enumerate(st.session_state.history):
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message["role"] == "assistant":
            feedback = message.get("feedback", None)
            st.session_state[f"feedback_{i}"] = feedback
            st.feedback(
                "thumbs",
                key=f"feedback_{i}",
                disabled=feedback is not None,
                on_change=save_feedback,
                args=[i],
            )


if prompt := st.chat_input(placeholder="Your message", key="input"):#key input ki aa   
    with st.chat_message("user"):
        st.write(prompt)
        
    st.session_state.history.append({"role": "user", "content": prompt})
    # get response from RAG system sida vo accept hi nhi kar raha   smj gya
    with st.spinner(text="In progress...", show_time=False):
        time.sleep(2)  # Simulate processing time
    # 
    response = f'to ap bol rahe hai {prompt}'
    with st.chat_message(f"assistant"):
        
        response = st.write_stream(chat_stream(prompt))
        
        st.feedback(
            "thumbs",
            key=f"feedback_{len(st.session_state.history)}",
            on_change=save_feedback,
            args=[len(st.session_state.history)],
        )
    st.session_state.history.append({"role": "assistant", "content": response})
    # tum gaye nahi  asha 
