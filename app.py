import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from streamlit_chat import message
from utils.prompts import SYSTEM_PROMPT
from utils.helpers import extract_info
from utils.db import save_candidate
from utils.db import get_candidate_by_email
from utils.helpers import validate_email, validate_phone

import time

st.set_page_config(
    page_title="TalentScout AI",
    page_icon="🧑💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')
mongo_uri = os.getenv("MONGODB_URI")
google_key = os.getenv("GOOGLE_API_KEY")

print("🔑 MONGODB_URI =", mongo_uri)
print("🔑 GOOGLE_API_KEY present?", bool(google_key))

        
def inject_css():
    with open("assets/styles.css", "r", encoding="utf-8") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

inject_css()


def init_session():
    defaults = {
        'convo_stage': 'greeting',
        'candidate_info': {
            'name': '', 'email': '', 'phone': '',
            'experience': '', 'position': '',
            'location': '', 'tech_stack': []
        },
        'chat_history': [],
        'tech_questions': []
    }
    for key, val in defaults.items():
        st.session_state.setdefault(key, val)

init_session()

def show_sidebar():
    with st.sidebar:
        st.markdown("""...""", unsafe_allow_html=True)

        with st.expander("👤 Personal Details", expanded=True):
            st.markdown(f"""
            <div class="detail-item">
                <i class="fas fa-signature"></i>
                <div>
                    <strong>Full Name</strong><br>
                    <span class="detail-value">{st.session_state.candidate_info['name'] or 'Not provided'}</span>
                </div>
            </div>
            <div class="detail-item">
                <i class="fas fa-at"></i>
                <div>
                    <strong>Email</strong><br>
                    <span class="detail-value">{st.session_state.candidate_info['email'] or 'Not provided'}</span>
                </div>
            </div>
            <div class="detail-item">
                <i class="fas fa-mobile-alt"></i>
                <div>
                    <strong>Phone</strong><br>
                    <span class="detail-value">{st.session_state.candidate_info['phone'] or 'Not provided'}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
                  
def chat_interface():
    st.markdown("""
    <div class="main-header">
        <div class="header-content">
            <h1>🧑💼 TalentScout AI Recruiter</h1>
            <p class="subheader">Your Intelligent Hiring Assistant</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="message-container">', unsafe_allow_html=True)
        for i, (msg, is_user) in enumerate(st.session_state.chat_history):
            role = "user" if is_user else "assistant"
            avatar = "🧑‍💼" if is_user else "🤖"
            alignment = "margin-left: auto;" if is_user else "margin-right: auto;"
            bg_class = "user" if is_user else "assistant"
            st.markdown(
                f"""
                <div class="stChatMessage {bg_class}" style="{alignment}">
                    <div style="display: flex; align-items: center;">
                        <div style="font-size: 1.2rem; margin-right: 0.5rem;">{avatar}</div>
                        <div>{msg}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="input-container">', unsafe_allow_html=True)
        with st.form("chat_form", clear_on_submit=True):
            cols = st.columns([5, 1])
            with cols[0]:
                user_input = st.text_input(
                    "Your Message:",
                    key="input",
                    placeholder="Type your message...",
                    label_visibility="collapsed"
                )
            with cols[1]:
                submitted = st.form_submit_button("Send ➡️")
        st.markdown('</div>', unsafe_allow_html=True)

        if submitted and user_input:
            handle_user_input(user_input)


def handle_user_input(text):
    st.session_state.chat_history.append((text, True))  

    extracted = extract_info(text)
    info = st.session_state.candidate_info
    

    for key, value in extracted.items():
    
        if key == "email" and not validate_email(value):
            print("❌ Invalid email:", value)
            continue
        elif key == "phone" and not validate_phone(value):
            print("❌ Invalid phone:", value)
            continue
        elif key == "tech_stack" and not isinstance(value, list):
            print("❌ Invalid tech_stack format")
            continue
        elif not value:
            print(f"❌ Empty value for key: {key}")
            continue

        info[key] = value

    st.session_state.chat_history.append(("Processing user data...", False))  
    required_fields = ['name', 'email', 'phone', 'experience', 'position', 'location', 'tech_stack']
    print(info,"info")
    if all(info.get(field) for field in required_fields):
        print(info,"save candiadte triggered")
        save_candidate(info) 
        print("✅ Candidate data saved:", info)
    else:
        print("❗Not all required fields are valid. Not saving.")

    generate_ai_response()

    if st.session_state.convo_stage == 'tech_stack':
        generate_technical_questions()
        st.session_state.convo_stage = 'assessment'

    st.rerun() 


def generate_ai_response():
    with st.spinner("Analyzing..."):
        try:
            response = model.generate_content(
                f"{SYSTEM_PROMPT}\n\nCurrent Conversation:\n{format_conversation()}"
            )
            ai_response = response.text
        except Exception as e:
            ai_response = f"Error: {str(e)}"

        st.session_state.chat_history.append((ai_response, False))  



def format_conversation():
    return "\n".join(
        f"{'User' if is_user else 'AI'}: {msg}"
        for msg, is_user in st.session_state.chat_history
    )


def generate_technical_questions():
    tech_stack = ', '.join(st.session_state.candidate_info['tech_stack'])
    if not tech_stack:
        st.warning("No tech stack provided. Please provide tech stack information.")
        return
    prompt = f"""
    Generate 5 technical interview questions covering: {tech_stack}
    Include questions about:
    - Basic concepts
    - Intermediate implementations
    - Advanced scenarios
    Format as a numbered list
    """
    try:
        response = model.generate_content(prompt)
        questions = [q.strip() for q in response.text.split('\n') if q.strip()]
        st.session_state.tech_questions = questions[:5]
    except Exception as e:
        st.error(f"Question generation failed: {str(e)}")


if __name__ == "__main__":
    show_sidebar()
    chat_interface()
