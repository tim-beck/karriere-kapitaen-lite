import streamlit as st
import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Language Settings ---
LANGUAGES = {
    "DE": {
        "title": "🎓 ISM Studiengang-Matching",
        "welcome": "Willkommen bei der ISM International School of Management! 💙\nHier findest du deine passenden Studiengänge basierend auf deinen Interessen und Stärken.\nWichtig: Bitte schreibe hier keine personenbezogenen Daten hin.",
        "interests_goals": "Deine Interessen und Ziele",
        "study_goals": "Was möchtest du später einmal erreichen?",
        "interests": "Was machst du am liebsten in deiner Freizeit?",
        "strengths": "Was sind deine größten Stärken?",
        "preferences": "Deine Präferenzen",
        "degrees": "Welche Abschlüsse interessieren dich?",
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
        "welcome": "Welcome to ISM International School of Management! 💙\nHere you'll find suitable study programs based on your interests and strengths.\nImportant: Please do not enter any personal data here.",
        "interests_goals": "Your Interests and Goals",
        "study_goals": "What would you like to achieve in the future?",
        "interests": "What do you enjoy doing in your free time?",
        "strengths": "What are your greatest strengths?",
        "preferences": "Your Preferences",
        "degrees": "Which degrees interest you?",
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

api_url = "https://api.openai.com/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# --- Lade ISM Studiengänge ---
def load_study_programs():
    try:
        with open('ism_studiengaenge.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        st.error(f"Fehler beim Laden der Studiengänge: {str(e)}")
        return []

# Lade Studiengänge beim Start
study_programs = load_study_programs()

# --- System Prompt mit Studiengängen ---
base_prompt = f"""
Du bist ein inspirierender Studienberater für die ISM International School of Management.
Deine Aufgabe ist es, basierend auf den Interessen und Stärken der Studieninteressierten passende Studiengänge zu empfehlen.
Stelle keine Diagnosen und gib keine vorschnellen Ratschläge. 
Fokussiere dich darauf, neue Perspektiven zu eröffnen und Denkanstöße zu geben.

WICHTIG: Du darfst NUR Studiengänge aus dieser Liste empfehlen:
{json.dumps([program['titel'] for program in study_programs], indent=2, ensure_ascii=False)}

Für jeden empfohlenen Studiengang, gib auch diese Details an:
- Abschluss
- Standorte
- Dauer
- Studiengebühr
"""

# Custom CSS für ISM Branding
st.markdown("""
    <style>
    .stApp header {
        background-color: #003366;
    }
    </style>
    """, unsafe_allow_html=True)

# Language Toggle
col1, col2 = st.columns([1, 5])
with col1:
    if st.button("🇩🇪" if st.session_state.language == "EN" else "🇬🇧"):
        st.session_state.language = "EN" if st.session_state.language == "DE" else "DE"
        st.rerun()

current_lang = LANGUAGES[st.session_state.language]

st.title(current_lang["title"])

# Willkommens-Text
st.markdown(current_lang["welcome"])

# --- Hauptfragen ---
st.subheader(current_lang["interests_goals"])

studienziele = st.text_area(
    current_lang["study_goals"],
    help="⚠️ Bitte gib hier keine personenbezogenen Daten ein"
)

interessen = st.text_area(
    current_lang["interests"],
    help="⚠️ Bitte gib hier keine personenbezogenen Daten ein"
)

staerken = st.text_area(
    current_lang["strengths"],
    help="⚠️ Bitte gib hier keine personenbezogenen Daten ein"
)

# --- Filter-Optionen ---
st.subheader(current_lang["preferences"])

abschluss = st.multiselect(
    current_lang["degrees"],
    options=["Bachelor", "Master"],
    help="Du kannst mehrere Abschlüsse auswählen"
)

standorte = st.multiselect(
    current_lang["locations"],
    options=["Dortmund", "Frankfurt/Main", "München", "Hamburg", "Köln", "Stuttgart"],
    help="Du kannst mehrere Standorte auswählen"
)

# --- Studiengang-Matching ---
if st.button(current_lang["find_programs"]):
    if not (studienziele and interessen and staerken):
        st.warning(current_lang["fill_all_fields"])
    else:
        # Erstelle den Prompt für das Studiengang-Matching
        matching_prompt = f"""
        Basierend auf folgenden Informationen, gib 5 passende ISM-Studiengänge:
        
        Studienziele: {studienziele}
        Top 3 Interessen: {interessen}
        Top 3 Stärken: {staerken}
        Gewünschte Abschlüsse: {', '.join(abschluss) if abschluss else 'Alle'}
        Gewünschte Standorte: {', '.join(standorte) if standorte else 'Alle'}
        
        Für jeden Studiengang:
        1. Nenne den Studiengangstitel (NUR aus der vorgegebenen Liste!)
        2. Erkläre kurz, warum dieser Studiengang passen könnte
        3. Gib die Details (Abschluss, Standorte, Dauer, Studiengebühr)
        
        WICHTIG: Berücksichtige die gewünschten Abschlüsse und Standorte bei deinen Empfehlungen!
        
        Formatiere die Antwort wie folgt:
        
        🎓 [STUDIENGANGSTITEL]
        ----------------------
        Warum passt dieser Studiengang zu dir?
        [Erklärung]
        
        📚 Details:
        - Abschluss: [Abschluss]
        - Standorte: [Standorte]
        - Dauer: [Dauer]
        - Studiengebühr: [Studiengebühr]
        
        [Wiederhole für jeden Studiengang]
        """
        
        with st.spinner(current_lang["finding_programs"]):
            try:
                response = requests.post(api_url, headers=headers, json={
                    "model": "gpt-4",
                    "messages": [
                        {"role": "system", "content": base_prompt},
                        {"role": "user", "content": matching_prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1000
                })
                
                response.raise_for_status()
                response_data = response.json()
                
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    suggestions = response_data["choices"][0]["message"]["content"]
                    st.session_state.messages = [
                        {"role": "system", "content": base_prompt},
                        {"role": "assistant", "content": suggestions}
                    ]
                    st.session_state.chat_started = True
                    st.session_state.first_round = True
                else:
                    st.error("Unerwartetes Antwortformat von der API. Bitte versuche es später erneut.")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"Fehler bei der API-Anfrage: {str(e)}")
            except (KeyError, ValueError) as e:
                st.error(f"Fehler beim Verarbeiten der API-Antwort: {str(e)}")

# --- Chat-Interface für Feedback und Iteration ---
if st.session_state.get("chat_started", False):
    st.divider()
    st.header(current_lang["feedback"])

    # Chatverlauf anzeigen
    for msg in st.session_state.messages[1:]:
        st.chat_message("user" if msg["role"] == "user" else "assistant").write(msg["content"])

    # Nachrichteneingabe
    user_input = st.chat_input(current_lang["feedback_input"])
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

        with st.spinner(current_lang["analyzing_feedback"]):
            try:
                # Angepasster Prompt basierend auf der Runde
                if st.session_state.get("first_round", False):
                    iteration_prompt = f"""
                    Basierend auf dem Feedback des Nutzers, passe die Studiengang-Vorschläge an.
                    Erkläre die Logik hinter den Änderungen.
                    WICHTIG: Verwende NUR Studiengänge aus der vorgegebenen Liste!
                    """
                    st.session_state.first_round = False
                else:
                    iteration_prompt = f"""
                    Basierend auf den finalen Studiengang-Vorschlägen, beschreibe passende Berufsperspektiven.
                    Fokussiere dich auf die Top 3 Studiengänge und zeige für jeden 2-3 konkrete Berufsbilder.
                    """
                
                response = requests.post(api_url, headers=headers, json={
                    "model": "gpt-4",
                    "messages": st.session_state.messages + [{"role": "user", "content": iteration_prompt}],
                    "temperature": 0.7,
                    "max_tokens": 1000
                })
                
                response.raise_for_status()
                response_data = response.json()
                
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    reply = response_data["choices"][0]["message"]["content"]
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                    st.chat_message("assistant").write(reply)
                else:
                    st.error("Unerwartetes Antwortformat von der API. Bitte versuche es später erneut.")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"Fehler bei der API-Anfrage: {str(e)}")
            except (KeyError, ValueError) as e:
                st.error(f"Fehler beim Verarbeiten der API-Antwort: {str(e)}") 