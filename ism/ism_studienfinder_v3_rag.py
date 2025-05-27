import streamlit as st
import requests
import os
import pandas as pd
import json
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# Load environment variables from .env file
load_dotenv()

# --- Language Settings ---
LANGUAGES = {
    "DE": {
        "title": "🎓 ISM Studiengang-Matching",
        "welcome": "Willkommen bei der ISM International School of Management! 💙\nHier findest du deine passenden Studiengänge basierend auf deinen Interessen und Stärken - für dich kuratiert von unserer ISM-KI, ermöglicht durch [Karriere-Kapitän](https://karriere-kapitaen.com).\n\nWichtig: Bitte gib hier keine personenbezogenen Daten ein (z.B. Name, Wohnort, Geburtsdatum, Telefonnummer, E-Mail-Adresse oder andere persönliche Informationen).",
        "interests_goals": "Deine Interessen und Ziele",
        "study_goals": "Was möchtest du später einmal erreichen?",
        "interests": "Was machst du am liebsten in deiner Freizeit?",
        "strengths": "Was sind deine größten Stärken? Wofür wurdest du schonmal gelobt?",
        "aspirations": "Was möchtest du in deinem Leben erreichen? Was sind deine Träume und Ziele?",
        "preferences": "Deine Präferenzen",
        "language": "Unterrichtssprache",
        "study_form": "Studienform",
        "locations": "An welchen Standorten möchtest du studieren?",
        "find_programs": "🎓 Studiengänge finden",
        "fill_all_fields": "Bitte fülle alle Felder aus.",
        "finding_programs": "💭 Finde passende Studiengänge...",
        "feedback": "💬 Dein Feedback",
        "feedback_input": "Was denkst du zu den Studiengang-Vorschlägen?",
        "analyzing_feedback": "💭 Analysiere dein Feedback..."
    },
    "EN": {
        "title": "🎓 ISM Study Program Matching",
        "welcome": "Welcome to ISM International School of Management! 💙\nHere you'll find suitable study programs based on your interests and strengths - curated for you by our ISM AI, powered by [Karriere-Kapitän](https://karriere-kapitaen.com).\n\nImportant: Please do not enter any personal data here (e.g., name, address, date of birth, phone number, email address, or other personal information).",
        "interests_goals": "Your Interests and Goals",
        "study_goals": "What would you like to achieve in the future?",
        "interests": "What do you enjoy doing in your free time?",
        "strengths": "What are your greatest strengths? What have you been praised for?",
        "aspirations": "What do you want to achieve in your life? What are your dreams and goals?",
        "preferences": "Your Preferences",
        "language": "Language of Instruction",
        "study_form": "Study Form",
        "locations": "At which locations would you like to study?",
        "find_programs": "🎓 Find Study Programs",
        "fill_all_fields": "Please fill in all fields.",
        "finding_programs": "💭 Finding suitable study programs...",
        "feedback": "💬 Your Feedback",
        "feedback_input": "What do you think about the study program suggestions?",
        "analyzing_feedback": "💭 Analyzing your feedback..."
    }
}

# Initialize language in session state if not present
if 'language' not in st.session_state:
    st.session_state.language = "DE"

# --- OpenAI API Konfiguration ---
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    st.error("Please set the OPENAI_API_KEY environment variable in your .env file")
    st.stop()

# --- RAG Setup ---
@st.cache_resource
def setup_rag():
    # Load study programs
    df = pd.read_csv('studiengaenge.csv')
    
    # Create text chunks (one per study program)
    texts = []
    metadatas = []
    
    for _, row in df.iterrows():
        # Create text content for each study program
        text = f"""
        Studiengang: {row['Titel des Studiengangs']}
        Beschreibung: {row['Beschreibung']}
        """
        texts.append(text)
        
        # Store metadata
        metadata = {
            'titel': row['Titel des Studiengangs'],
            'studienform': row['Studienform'],
            'unterrichtssprache': row['Unterrichtssprache'],
            'standorte': row['Standorte'],
            'abschluss': row['Abschluss'],
            'dauer': row['Dauer'],
            'studiengebuehren': row['Studiengebühren'],
            'url': row['URL']
        }
        metadatas.append(metadata)
    
    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Create vector store
    vectorstore = Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas
    )
    
    return vectorstore

# Initialize RAG components
vectorstore = setup_rag()

# --- Custom CSS für ISM Branding ---
st.markdown("""
    <style>
    .stApp header {
        background-color: #003366;
    }
    /* Custom color for multiselect options */
    .stMultiSelect [data-baseweb=select] span {
        background-color: #FFA500 !important;
        color: white !important;
    }
    /* Powered by text styling */
    .powered-by {
        text-align: center;
        font-size: 0.8em;
        color: #666;
        margin-top: 2rem;
        padding: 1rem 0;
        border-top: 1px solid #eee;
    }
    /* Response time styling */
    .response-time {
        font-size: 0.7em;
        color: #999;
        text-align: right;
        margin-top: -0.5rem;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Logo and Language Toggle
col1, col2 = st.columns([0.8, 0.2])
with col1:
    if st.button("🇩🇪 DE" if st.session_state.language == "EN" else "🇬🇧 ENG"):
        st.session_state.language = "EN" if st.session_state.language == "DE" else "DE"
        st.rerun()
with col2:
    st.image("logos/ism.png", width=150)

current_lang = LANGUAGES[st.session_state.language]

st.title(current_lang["title"])

# Willkommens-Text
st.markdown(current_lang["welcome"])

# --- Hauptfragen ---
st.subheader(current_lang["interests_goals"])

interessen = st.text_area(
    current_lang["interests"],
    help="⚠️ Bitte gib hier keine personenbezogenen Daten ein"
)

staerken = st.text_area(
    current_lang["strengths"],
    help="⚠️ Bitte gib hier keine personenbezogenen Daten ein"
)

studienziele = st.text_area(
    current_lang["aspirations"],
    help="⚠️ Bitte gib hier keine personenbezogenen Daten ein"
)

# --- Filter-Optionen ---
st.subheader(current_lang["preferences"])
st.markdown("💡 Du kannst bei allen Filtern mehrere Optionen auswählen, indem du sie anklickst.")

unterrichtssprache = st.multiselect(
    current_lang["language"],
    options=["Deutsch", "Englisch"],
    help="Du kannst mehrere Sprachen auswählen"
)

studienform = st.multiselect(
    current_lang["study_form"],
    options=["Vollzeit", "Dual", "Berufsbegleitend"],
    help="Du kannst mehrere Studienformen auswählen"
)

standorte = st.multiselect(
    current_lang["locations"],
    options=["Dortmund", "Frankfurt/Main", "München", "Hamburg", "Köln", "Stuttgart", "Berlin"],
    help="Du kannst mehrere Standorte auswählen"
)

# --- Studiengang-Matching ---
if st.button(current_lang["find_programs"]):
    if not (studienziele and interessen and staerken):
        st.warning(current_lang["fill_all_fields"])
    else:
        with st.spinner(current_lang["finding_programs"]):
            try:
                start_time = time.time()
                
                # Create filter conditions
                filter_conditions = {}
                if unterrichtssprache:
                    filter_conditions["unterrichtssprache"] = {"$in": unterrichtssprache}
                if studienform:
                    filter_conditions["studienform"] = {"$in": studienform}
                if standorte:
                    filter_conditions["standorte"] = {"$in": standorte}
                
                # Create query
                query = f"""
                Basierend auf folgenden Informationen:
            Studienziele: {studienziele}
                Interessen: {interessen}
                Stärken: {staerken}
                
                Finde passende Studiengänge.
                """
                
                # Perform similarity search with filters
                docs = vectorstore.similarity_search(
                    query,
                    k=3,
                    filter=filter_conditions if filter_conditions else None
                )
                
                # Format response
                suggestions = []
                for doc in docs:
                    metadata = doc.metadata
                    suggestion = f"""
                    🎓 {metadata['titel']}
            ----------------------
            Warum passt dieser Studiengang zu dir?
                    {doc.page_content}
            
            📚 Details:
                    - Abschluss: {metadata['abschluss']}
                    - Studienform: {metadata['studienform']}
                    - Standorte: {metadata['standorte']}
                    - Dauer: {metadata['dauer']}
                    - Studiengebühren: {metadata['studiengebuehren']}
                    - Unterrichtssprache: {metadata['unterrichtssprache']}
                    
                    🔗 Mehr Infos: {metadata['url']}
                    """
                    suggestions.append(suggestion)
                
                response_time = time.time() - start_time
                suggestions_text = "\n\n".join(suggestions)
                
                # Add tip and feedback request
                suggestions_text += """
                
                💡 Tipp: Du möchtest mehr über die ISM erfahren? Besuche unsere [Infotage und -abende](https://ism.de/studieninteressierte/infoveranstaltungen/infotage-und-infoabende) oder nutze die Möglichkeit zum [Probehören](https://ism.de/studieninteressierte/infoveranstaltungen/probehoeren).
                
                💭 Was hältst du von diesen Vorschlägen? Welche Aspekte interessieren dich besonders?
                """
                
                    st.session_state.messages = [
                    {"role": "system", "content": "Du bist ein hilfreicher Studienberater."},
                    {"role": "assistant", "content": suggestions_text, "response_time": response_time}
                    ]
                    st.session_state.chat_started = True
                    st.session_state.first_round = True
                
            except Exception as e:
                st.error(f"Fehler bei der Suche: {str(e)}")

# --- Chat-Interface für Feedback und Iteration ---
if st.session_state.get("chat_started", False):
    st.divider()
    st.header(current_lang["feedback"])

    # Chatverlauf anzeigen
    for msg in st.session_state.messages[1:]:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant", avatar="logos/ism.png").write(msg["content"])
            if "response_time" in msg:
                st.markdown(f'<div class="response-time">Antwortzeit: {msg["response_time"]:.1f} Sekunden</div>', unsafe_allow_html=True)

    # Nachrichteneingabe
    user_input = st.chat_input(current_lang["feedback_input"])
    
    # Powered by text right after chat input
    st.markdown('<div class="powered-by">Powered by <a href="https://karriere-kapitaen.com" target="_blank">Karriere-Kapitän</a></div>', unsafe_allow_html=True)
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

        with st.spinner(current_lang["analyzing_feedback"]):
            try:
                start_time = time.time()
                
                # Create new query based on feedback
                feedback_query = f"""
                Basierend auf dem Feedback des Nutzers: {user_input}
                
                Finde passende Studiengänge.
                """
                
                # Perform similarity search with filters
                docs = vectorstore.similarity_search(
                    feedback_query,
                    k=3,
                    filter=filter_conditions if filter_conditions else None
                )
                
                # Format response
                suggestions = []
                for doc in docs:
                    metadata = doc.metadata
                    suggestion = f"""
                    🎓 {metadata['titel']}
                    ----------------------
                    Warum passt dieser Studiengang zu dir?
                    {doc.page_content}
                    
                    📚 Details:
                    - Abschluss: {metadata['abschluss']}
                    - Studienform: {metadata['studienform']}
                    - Standorte: {metadata['standorte']}
                    - Dauer: {metadata['dauer']}
                    - Studiengebühren: {metadata['studiengebuehren']}
                    - Unterrichtssprache: {metadata['unterrichtssprache']}
                    
                    🔗 Mehr Infos: {metadata['url']}
                    """
                    suggestions.append(suggestion)
                
                response_time = time.time() - start_time
                suggestions_text = "\n\n".join(suggestions)
                
                # Add tip and feedback request
                suggestions_text += """
                
                💡 Tipp: Du möchtest mehr über die ISM erfahren? Besuche unsere [Infotage und -abende](https://ism.de/studieninteressierte/infoveranstaltungen/infotage-und-infoabende) oder nutze die Möglichkeit zum [Probehören](https://ism.de/studieninteressierte/infoveranstaltungen/probehoeren).
                
                💭 Was hältst du von diesen Vorschlägen? Welche Aspekte interessieren dich besonders?
                """
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": suggestions_text,
                    "response_time": response_time
                })
                st.chat_message("assistant", avatar="logos/ism.png").write(suggestions_text)
                st.markdown(f'<div class="response-time">Antwortzeit: {response_time:.1f} Sekunden</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Fehler bei der Suche: {str(e)}") 