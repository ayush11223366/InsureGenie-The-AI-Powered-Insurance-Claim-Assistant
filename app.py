import streamlit as st
import os
import tempfile
# Assuming you have these files from your original setup
from ingest.document_loader import DocumentLoader
from retrieval.vector_store import SimpleVectorStore
from llm.gemini_api import GeminiLLM
import re

# --- Page Configuration ---
st.set_page_config(page_title="Insure Genie", layout="wide")

# --- Custom CSS for Gemini-like UI ---
st.markdown("""
    <style>
    /* General Body and App Styling */
    body, .stApp {
        background-color: #131314 !important;
        color: #e3e3e3;
    }

    /* Hide Streamlit Header/Footer */
    .st-emotion-cache-16txtl3, .st-emotion-cache-12fmjuu {
        display: none;
    }
    
    .small-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #e3e3e3;
        padding: 0.75rem 0;
        position: sticky;
        top: 0;
        background-color: #131314; /* Match body background */
        z-index: 50;
        max-width: 800px;
        margin: 0 auto;
        border-bottom: 1px solid #3c4043;
        animation: fadeInDown 0.5s ease-in-out;
    }

    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Main Content Area */
    .main-container {
        max-width: 800px;
        margin: 0 auto;
        padding-top: 2rem;
        padding-bottom: 10rem; 
    }

    /* Welcome Screen Styling */
    .welcome-container {
        text-align: center;
        padding: 4rem 1rem;
    }
    .welcome-container h1 {
        font-size: 3.5rem;
        font-weight: 600;
        background: -webkit-linear-gradient(45deg, #4285F4, #9B72CB, #FBBC05, #34A853);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .welcome-container p {
        font-size: 1.2rem;
        color: #9aa0a6;
        margin-bottom: 2rem;
    }

    /* Chat Exchange Styling */
    .chat-exchange { margin-bottom: 2rem; }
    .prompt-block, .response-block { display: flex; align-items: flex-start; padding: 1rem; }
    .chat-icon { font-size: 1.5rem; margin-right: 1rem; }
    .prompt-content p, .response-content p { margin: 0; font-size: 1.1rem; line-height: 1.6; }
    .prompt-content { font-weight: 500; }

    /* Fixed Input Bar at the Bottom */
    .input-bar-fixed {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: #131314;
        padding: 1rem 0;
        z-index: 100;
    }
    .input-bar-container {
        display: flex;
        align-items: center;
        gap: 10px;
        max-width: 800px;
        margin: 0 auto;
        background-color: #1e1f20;
        border-radius: 2rem;
        padding: 0.5rem 1rem;
        border: 1px solid #3c4043;
    }
    .input-bar-container .stTextInput { flex-grow: 1; }
    .input-bar-container .stTextInput > div > input {
        background-color: #1e1f20 !important;
        color: #e3e3e3 !important;
        border: none !important;
        font-size: 1.1rem !important;
        padding-left: 0.5rem;
    }
    .input-bar-container .stButton > button {
        background: transparent;
        border: none;
        color: #9aa0a6;
        font-size: 1.5rem;
        cursor: pointer;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .input-bar-container .stButton > button:hover { background-color: #282a2c; }
    /* Let the file uploader have some default styles to show file names */
    .input-bar-container .stFileUploader > div[data-testid="stFileDropzone"] {
        min-width: 40px !important;
    }
    </style>
""", unsafe_allow_html=True)


# --- Session State Initialization ---
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'llm' not in st.session_state:
    st.session_state['llm'] = GeminiLLM()
if 'vector_store' not in st.session_state:
    st.session_state['vector_store'] = None

# --- Helper Functions ---
def handle_query(user_query, uploaded_files):
    """Adds query to history and triggers a rerun to show the prompt immediately."""
    file_names = [f.name for f in uploaded_files]
    st.session_state.chat_history.append({"user": user_query, "ai": None, "files": file_names})
    # Pass the file objects directly for processing
    st.session_state.temp_files = uploaded_files
    st.rerun()

is_loading = bool(st.session_state.chat_history and st.session_state.chat_history[-1]["ai"] is None)

# --- Main App Logic ---
if is_loading:
    last_exchange = st.session_state.chat_history[-1]
    user_query = last_exchange["user"]
    ai_response = ""

    # Process files if they were passed in this exchange
    if "temp_files" in st.session_state and st.session_state.temp_files:
        with st.spinner("Analyzing documents..."):
            temp_dir = tempfile.mkdtemp()
            for uploaded_file in st.session_state.temp_files:
                file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            
            loader = DocumentLoader(temp_dir)
            docs = loader.load_documents()
            chunks = [doc['text'] for doc in docs if doc['text']]
            llm = st.session_state['llm']
            embeddings = [llm.get_embedding(chunk) for chunk in chunks]
            store = SimpleVectorStore(dim=768)
            for emb, chunk in zip(embeddings, chunks):
                store.add(emb, chunk)
            st.session_state['vector_store'] = store
        del st.session_state.temp_files # Clean up after processing

    # Generate answer
    if st.session_state['vector_store'] is not None:
        with st.spinner("Searching for answers..."):
            llm = st.session_state['llm']
            query_emb = llm.get_embedding(user_query)
            retrieved = st.session_state['vector_store'].search(query_emb, top_k=3)
            retrieved_texts = [text for text, _ in retrieved]
            context = '\n---\n'.join(retrieved_texts)
            answer = llm.answer_query(user_query, context)
            ai_response = answer
    else:
        ai_response = "I can only answer questions about documents you've uploaded. Please upload a file."

    st.session_state.chat_history[-1]["ai"] = ai_response
    st.rerun()

# --- UI Rendering ---
if st.session_state.chat_history:
    st.markdown('<div class="small-header">Insure Genie ✨</div>', unsafe_allow_html=True)

st.markdown('<div class="main-container">', unsafe_allow_html=True)

if not st.session_state.chat_history:
    st.markdown("""
        <div class="welcome-container">
            <h1>Insure Genie</h1>
            <p>Ask me anything about the documents you upload.</p>
        </div>
    """, unsafe_allow_html=True)
else:
    for exchange in st.session_state.chat_history:
        user_prompt_html = f'<div class="prompt-block"><div class="chat-icon">🧑‍💻</div><div class="prompt-content"><p>{exchange["user"]}</p></div></div>'
        files_html = ""
        if exchange.get('files'):
            file_bubbles = "".join([f'<div class="file-bubble">📎 {fname}</div>' for fname in exchange['files']])
            files_html = f'<div class="response-block"><div class="chat-icon"></div><div class="response-content">{file_bubbles}</div></div>'
        if exchange["ai"] is None:
            ai_response_html = '<div class="response-block"><div class="chat-icon">✨</div><div class="loader-container"><div class="loader-icon"></div><span>Generating...</span></div></div>'
        else:
            ai_response_html = f'<div class="response-block"><div class="chat-icon">✨</div><div class="response-content"><p>{exchange["ai"]}</p></div></div>'
        full_exchange_html = f'<div class="chat-exchange">{user_prompt_html}{files_html}{ai_response_html}</div>'
        st.markdown(full_exchange_html, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


# --- SIMPLIFIED FIXED INPUT BAR ---
st.markdown('<div class="input-bar-fixed">', unsafe_allow_html=True)
with st.container():
    st.markdown('<div class="input-bar-container">', unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Upload",
        type=["pdf", "docx", "eml"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        key="file_uploader_widget",
        disabled=is_loading
    )

    user_query = st.text_input("Query", placeholder="Ask about your documents...", label_visibility="collapsed", key="query_input", disabled=is_loading)
    send_pressed = st.button("➤", key="send_button", disabled=is_loading or not user_query.strip())
    
    st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

if send_pressed:
    handle_query(user_query, uploaded_files)