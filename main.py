import streamlit as st
from rag_system import rag_system
import time
import pickle
import os
# ye .env nu load karda api lan lai
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()

# st.snow()
# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
# Initialize session state for current chat ID
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
# Initialize session state for saved chats
if "saved_chats" not in st.session_state:
    st.session_state.saved_chats = {}


# Load saved chats from file on startup
def load_saved_chats():
    try:
        # it finds the file saved_chats.pkl te ohde vichon data load karda
        if os.path.exists("saved_chats.pkl"):
            with open("saved_chats.pkl", "rb") as f:
                st.session_state.saved_chats = pickle.load(f)
    except:
        st.session_state.saved_chats = {}
# Call the function to load saved chats
load_saved_chats()


# Add this function delete chat with confirmation
def delete_chat_with_confirmation(chat_id, chat_name):
    """Delete chat with confirmation"""
    if st.session_state.get(f"confirm_delete_{chat_id}", False):
        # Second click - actually delete
        if chat_id in st.session_state.saved_chats:
            del st.session_state.saved_chats[chat_id]
            save_chats_to_file()
            st.success(f"Deleted '{chat_name}'")
            # Clear the confirmation flag
            st.session_state.pop(f"confirm_delete_{chat_id}", None)
            time.sleep(0.5)
            st.rerun()
    else:
        # First click - ask for confirmation
        st.session_state[f"confirm_delete_{chat_id}"] = True
        st.rerun()


# Save chats to file
def save_chats_to_file():
    try:
        with open("saved_chats.pkl", "wb") as f:
            pickle.dump(st.session_state.saved_chats, f)
    except Exception as e:
        st.error(f"Error saving chats: {e}")

with st.sidebar:
    st.title("TICS Dashboard")
    st.write("Powered by RAG • GurpreetTech ")
    #how to save a color picke if the site is refresh or closed then also the color is saved
    st.markdown("---")
    st.write("chat with AI")
    # Theme Selection
    st.subheader('Theme')
    
    # Check if data exists in URL
    if "data" in st.query_params:
        # Load from URL
        st.session_state.user_data = json.loads(st.query_params["data"])
        background = st.session_state.user_data['back']
        theme_color = st.session_state.user_data['color']
    else:
        # Set defaults
        background = '#000000'
        theme_color = '#FF0000'

    # Create columns for color pickers
    col1, col2 = st.columns(2)

    with col1:
        background = st.color_picker('Back', value=background)
    with col2:
        theme_color = st.color_picker('Circle', value=theme_color)

    # Save to session state and URL
    st.session_state.user_data = {"back": background, "color": theme_color}
    st.query_params["data"] = json.dumps(st.session_state.user_data)

    
    st.markdown("---")
    
    # New Chat Button
    if st.button("🆕 New Chat", use_container_width=True, type="primary"):
        # Save current chat if it has messages
        if st.session_state.chat_history:
            st.session_state.saved_chats[st.session_state.current_chat_id] = {
                "name": f"Chat_{len(st.session_state.saved_chats) + 1}",
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "messages": st.session_state.chat_history.copy()
            }
            save_chats_to_file()
        
        # Start new chat
        st.session_state.chat_history = []
        st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.rerun()
        
    # Save Current oh te mai dasda eh shoha
    # if st.button("💾 Save Current Chat", use_container_width=True):
    if st.session_state.chat_history:
        chat_name = f"Chat_{len(st.session_state.saved_chats) + 1}"
        st.session_state.saved_chats[st.session_state.current_chat_id] = {
            "name": chat_name,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "messages": st.session_state.chat_history.copy(),
            # "background": background,
            # "theme_color": theme_color
        }
        save_chats_to_file()
        st.success(f"Chat '{chat_name}' saved!")
    else:
        st.warning("No messages to save!")
    
    # Load Saved Chats 
    st.divider()
    st.subheader("📂 Saved Chats")
    
    # List saved chats with load and delete options
    if st.session_state.saved_chats:
        for chat_id, chat_info in st.session_state.saved_chats.items():
            
            # In your saved chats loop:
            with st.container(border=True):
                chat_name = chat_info.get('name', 'Chat')
                chat_date = chat_info.get('date', '')
                
            
                if st.button(f"📝 {chat_date}", 
                           key=f"load_{chat_id}", 
                           use_container_width=True):
                    st.session_state.chat_history = chat_info.get("messages", [])
                    st.session_state.current_chat_id = chat_id
                    st.rerun()
                if st.button("❌", key=f"confirm_{chat_id}", use_container_width=True):
                        if chat_id in st.session_state.saved_chats:
                            del st.session_state.saved_chats[chat_id]
                            save_chats_to_file()
                            st.session_state.pop(f"confirm_delete_{chat_id}", None)
                            st.rerun()
    else:
        st.write("No saved chats yet")
    
    # Chat Statistics
    st.divider()
    st.subheader("📊 Statistics")
    st.write(f"Current Chat: {len(st.session_state.chat_history)} messages")
    st.write(f"Saved Chats: {len(st.session_state.saved_chats)}")
    
    # Export Chat as JSON
    if st.session_state.chat_history:
        st.divider()
        chat_json = json.dumps({
            "chat_id": st.session_state.current_chat_id,
            "timestamp": datetime.now().isoformat(),
            "messages": st.session_state.chat_history
        }, indent=2)
        
        st.download_button(
            label="📥 Export Chat",
            data=chat_json,
            file_name=f"chat_{st.session_state.current_chat_id}.json",
            mime="application/json",
            use_container_width=True
        )

    # st.button("Search chats", use_container_width=True)
    # st.button("Images", use_container_width=True)
    # st.button("Apps", use_container_width=True)
    # st.button("Projects", use_container_width=True)


    st.markdown("---") 
    
    
    st.subheader("Made by Gurman_Team ")
   
    st.markdown("© 2026 MyWebsite")
      
    
st.title("Welcome to the TICS  Dashboard")
st.subheader("Ask your questions !")

st.markdown(f'''
            
            <style>
.stApp{{
    # background: linear-gradient( {theme_color}, {background});
        background:radial-gradient(circle at 130% 40%, {theme_color} 25%, {background} 75%);
    
}}
.stAppHeader {{   
    background-color: transparent;
}}

 /* Style the entire sidebar */
    [data-testid="stSidebar"    ] {{
        background:radial-gradient(circle at -120% 70%, {theme_color} 25%, {background} 75%);
        # radial-gradient(circle at -130%, #17d405 25%, {background} 75%)
        /* kida kam kardi aa eh line shape left-right top-bottom, color */
        
        /*radial-gradient(circle at 130%, {theme_color}25%, #000 75%)*/
        padding-top: 0;
        box-shadow: 0 0 30px {theme_color};
    }}
     /* Style the entire heading */
   .st-emotion-cache-2fgyt4 {{
        background: radial-gradient(circle at -50% 130%, white 25%, {theme_color} 75%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 18px;
        font-weight: bold;
    }}
    /*
    .st-emotion-cache-18kf3ut{{ 
        display: none;
    }} 
*/
.navbar {{
    background-color: #222;
    color: white;
    justify-content: space-between;
    align-items: center;
    padding: 15px 40px;
}}
.logo {{
    font-size: 22px;
    font-weight: bold;
    color: #00ffcc;
}}

.nav-links {{
    list-style: none;
}}

.nav-links li {{
    margin-left: 25px;
}}

.nav-links a {{
    text-decoration: none;
    color: white;
    font-size: 16px;
    transition: 0.3s;
}}

.nav-links a:hover {{
    color: #00ffcc;
}}
.stLogo {{
    height: 8rem;
}}
.e1td4qo63 {{
     background: transparent;
    }}

</style>

            ''',unsafe_allow_html=True)
# st.logo('<img src='' />',size="medium", link=None, icon_image=None) magic pta c menu use karnda mn te thodi aya jithe u dikhan dya hmm mtlb untracked new file eh jithe m likhya modified files te jehdi fikki eh test chall reha eh git de rules ne asha jehdi fikki eh oh ignore hundi jive.env   asha hun karde a main style bnao radio side bar c


HORIZONTAL_RED = "check.png"
ICON_RED = "logo.png"

st.logo(HORIZONTAL_RED, icon_image=ICON_RED,size="large")


def chat_stream(prompt):
    with st.spinner("Thinking...", show_time=True):
        response = rag_system.get_response(prompt)
    # response = f"This is a simulated response to your prompt: {prompt}"
        for char in response:
            yield char
            time.sleep(0.02)


def save_feedback(index):
    st.session_state.history[index]["feedback"] = st.session_state[f"feedback_{index}"]

# Display chat history
chat_container = st.container()
with chat_container:
    for i, message in enumerate(st.session_state.chat_history):
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if message["role"] == "assistant":
                feedback = message.get("feedback", None)
                st.session_state[f"feedback_{i}"] = feedback
                # Show timestamp if available
                if "timestamp" in message:
                    st.caption(f"Sent at: {message['timestamp']}")
                
                # Show feedback option
                st.feedback(
                    "thumbs",
                    key=f"feedback_{i}",
                    disabled=feedback is not None,
                    on_change=save_feedback,
                    args=[i],
                )
# Chat input
if prompt := st.chat_input("Say something"):
    # Add user message to history
    with st.chat_message("user"):
        st.write(prompt)
    
    st.session_state.chat_history.append({
        "role": "user", 
        "content": prompt,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })
    
    # Generate assistant response
  
    
    with st.chat_message("assistant"):
        response = st.write_stream(chat_stream(prompt))
        # Add feedback option
        st.feedback(
            "thumbs",
            key=f"feedback_{len(st.session_state.chat_history)}",
            on_change=save_feedback,
            args=[len(st.session_state.chat_history)],
        )
    
    # Add assistant message to history
    st.session_state.chat_history.append({
        "role": "assistant", 
        "content": response,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })
    
    # Auto-save chat after 5 messages
    if len(st.session_state.chat_history) > 0 and len(st.session_state.chat_history) % 5 == 0:
        if st.session_state.current_chat_id not in st.session_state.saved_chats:
            st.session_state.saved_chats[st.session_state.current_chat_id] = {
                "name": f"AutoSave_{len(st.session_state.saved_chats) + 1}",
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "messages": st.session_state.chat_history.copy()
            }
            save_chats_to_file()

