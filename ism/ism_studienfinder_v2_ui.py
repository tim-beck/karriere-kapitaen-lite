import streamlit as st
import requests
import os
import pandas as pd
import json
import time
from dotenv import load_dotenv

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

api_url = "https://api.openai.com/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# --- Lade ISM Studiengänge ---
def load_study_programs():
    try:
        df = pd.read_csv('studiengaenge.csv')
        return df.to_dict('records')
    except Exception as e:
        st.error(f"Fehler beim Laden der Studiengänge: {str(e)}")
        return []

# Lade Studiengänge beim Start
study_programs = load_study_programs()

# --- System Prompt mit Studiengängen ---
base_prompt = {
    "DE": f"""
Du bist ein inspirierender Studienberater für die ISM International School of Management.
Deine Aufgabe ist es, basierend auf den Interessen und Stärken der Studieninteressierten passende Studiengänge zu empfehlen.
Stelle keine Diagnosen und gib keine vorschnellen Ratschläge. 
Fokussiere dich darauf, neue Perspektiven zu eröffnen und Denkanstöße zu geben.

WICHTIG: 
1. Du darfst NUR Studiengänge aus dieser Liste empfehlen:
{json.dumps([program['Titel des Studiengangs'] for program in study_programs], indent=2, ensure_ascii=False)}

2. Verwende IMMER die exakten Daten aus der CSV-Datei für:
   - Abschluss
   - Studienform
   - Standorte
   - Dauer
   - Studiengebühren (exakt wie in der CSV-Datei, inkl. "pro Semester")
   - Unterrichtssprache
   - URL

3. Gib genau 3 Studiengänge aus.

4. Am Ende deiner Empfehlungen, füge diese Information ein:
   "💡 Tipp: Du möchtest mehr über die ISM erfahren? Besuche unsere [Infotage und -abende](https://ism.de/studieninteressierte/infoveranstaltungen/infotage-und-infoabende) oder nutze die Möglichkeit zum [Probehören](https://ism.de/studieninteressierte/infoveranstaltungen/probehoeren)."

Antworte immer auf Deutsch.
""",
    "EN": f"""
You are an inspiring study advisor for ISM International School of Management.
Your task is to recommend suitable study programs based on the interests and strengths of prospective students.
Do not make diagnoses or give premature advice.
Focus on opening new perspectives and providing food for thought.

IMPORTANT:
1. You may ONLY recommend study programs from this list:
{json.dumps([program['Titel des Studiengangs'] for program in study_programs], indent=2, ensure_ascii=False)}

2. ALWAYS use the exact data from the CSV file for:
   - Degree
   - Study Form
   - Locations
   - Duration
   - Tuition fee (exactly as in the CSV file, including "per semester")
   - Language of instruction
   - URL

3. Provide exactly 3 study programs.

4. At the end of your recommendations, add this information:
   "💡 Tip: Want to learn more about ISM? Visit our [information days and evenings](https://ism.de/studieninteressierte/infoveranstaltungen/infotage-und-infoabende) or try a [trial lecture](https://ism.de/studieninteressierte/infoveranstaltungen/probehoeren)."

Always respond in English.
"""
}

# Custom CSS für ISM Branding
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
        # Erstelle den Prompt für das Studiengang-Matching
        matching_prompt = {
            "DE": f"""
            Basierend auf folgenden Informationen, gib 3 passende ISM-Studiengänge:
            
            Studienziele: {studienziele}
            Top 3 Interessen: {interessen}
            Top 3 Stärken: {staerken}
            Gewünschte Unterrichtssprache: {', '.join(unterrichtssprache) if unterrichtssprache else 'Alle'}
            Gewünschte Studienform: {', '.join(studienform) if studienform else 'Alle'}
            Gewünschte Standorte: {', '.join(standorte) if standorte else 'Alle'}
            
            Für jeden Studiengang:
            1. Nenne den Studiengangstitel (NUR aus der vorgegebenen Liste!)
            2. Erkläre kurz, warum dieser Studiengang passen könnte
            3. Gib die Details (Abschluss, Studienform, Standorte, Dauer, Studiengebühren, Unterrichtssprache)
            4. Füge den Link zum Studiengang hinzu
            
            WICHTIG: 
            - Berücksichtige die gewünschte Unterrichtssprache, Studienform und Standorte bei deinen Empfehlungen!
            - Verwende IMMER die exakten Daten aus der CSV-Datei
            - Gib genau 3 Studiengänge aus
            - Bei den Standorten: Liste ALLE verfügbaren Standorte des Studiengangs auf, nicht nur die vom Nutzer ausgewählten!
            
            Formatiere die Antwort wie folgt:
            
            🎓 [STUDIENGANGSTITEL]
            ----------------------
            Warum passt dieser Studiengang zu dir?
            [Erklärung]
            
            📚 Details:
            - Abschluss: [Abschluss]
            - Studienform: [Studienform]
            - Standorte: [ALLE verfügbaren Standorte des Studiengangs]
            - Dauer: [Dauer]
            - Studiengebühren: [Studiengebühren pro Semester]
            - Unterrichtssprache: [Unterrichtssprache]
            
            🔗 Mehr Infos: [URL]
            
            [Wiederhole für 3 Studiengänge]
            
            💡 Tipp: Du möchtest mehr über die ISM erfahren? Besuche unsere [Infotage und -abende](https://ism.de/studieninteressierte/infoveranstaltungen/infotage-und-infoabende) oder nutze die Möglichkeit zum [Probehören](https://ism.de/studieninteressierte/infoveranstaltungen/probehoeren).
            
            💭 Was hältst du von diesen Vorschlägen? Welche Aspekte interessieren dich besonders?
            """,
            "EN": f"""
            Based on the following information, provide 3 suitable ISM study programs:
            
            Goals: {studienziele}
            Top 3 Interests: {interessen}
            Top 3 Strengths: {staerken}
            Desired Language of Instruction: {', '.join(unterrichtssprache) if unterrichtssprache else 'All'}
            Desired Study Form: {', '.join(studienform) if studienform else 'All'}
            Desired Locations: {', '.join(standorte) if standorte else 'All'}
            
            For each study program:
            1. Name the study program title (ONLY from the provided list!)
            2. Briefly explain why this program might be a good fit
            3. Provide the details (degree, study form, locations, duration, tuition fee, language of instruction)
            4. Add the link to the study program
            
            IMPORTANT:
            - Consider the desired language of instruction, study form, and locations in your recommendations!
            - ALWAYS use the exact data from the CSV file
            - Provide exactly 3 study programs
            - For locations: List ALL available locations of the study program, not just the ones selected by the user!
            
            Format the response as follows:
            
            🎓 [STUDY PROGRAM TITLE]
            ----------------------
            Why might this program be right for you?
            [Explanation]
            
            📚 Details:
            - Degree: [Degree]
            - Study Form: [Study Form]
            - Locations: [ALL available locations of the study program]
            - Duration: [Duration]
            - Tuition Fee: [Tuition Fee per Semester]
            - Language of Instruction: [Language]
            
            🔗 More Info: [URL]
            
            [Repeat for 3 study programs]
            
            💡 Tip: Want to learn more about ISM? Visit our [information days and evenings](https://ism.de/studieninteressierte/infoveranstaltungen/infotage-und-infoabende) or try a [trial lecture](https://ism.de/studieninteressierte/infoveranstaltungen/probehoeren).
            
            💭 What do you think about these suggestions? Which aspects interest you the most?
            """
        }
        
        with st.spinner(current_lang["finding_programs"]):
            try:
                start_time = time.time()
                response = requests.post(api_url, headers=headers, json={
                    "model": "gpt-4o",
                    "messages": [
                        {"role": "system", "content": base_prompt[st.session_state.language]},
                        {"role": "user", "content": matching_prompt[st.session_state.language]}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1000
                })
                
                response.raise_for_status()
                response_data = response.json()
                
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    suggestions = response_data["choices"][0]["message"]["content"]
                    response_time = time.time() - start_time
                    st.session_state.messages = [
                        {"role": "system", "content": base_prompt[st.session_state.language]},
                        {"role": "assistant", "content": suggestions, "response_time": response_time}
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
                
                # Angepasster Prompt basierend auf der Runde
                if st.session_state.get("first_round", False):
                    iteration_prompt = {
                        "DE": f"""
                        Basierend auf dem Feedback des Nutzers, passe die Studiengang-Vorschläge an.
                        Erkläre die Logik hinter den Änderungen.
                        WICHTIG: Verwende NUR Studiengänge aus der vorgegebenen Liste!
                        """,
                        "EN": f"""
                        Based on the user's feedback, adjust the study program suggestions.
                        Explain the reasoning behind the changes.
                        IMPORTANT: Use ONLY study programs from the provided list!
                        """
                    }
                    st.session_state.first_round = False
                else:
                    iteration_prompt = {
                        "DE": f"""
                        Basierend auf den finalen Studiengang-Vorschlägen, beschreibe passende Berufsperspektiven.
                        Fokussiere dich auf die Top 3 Studiengänge und zeige für jeden 2-3 konkrete Berufsbilder.
                        """,
                        "EN": f"""
                        Based on the final study program suggestions, describe suitable career prospects.
                        Focus on the top 3 study programs and show 2-3 concrete career paths for each.
                        """
                    }
                
                response = requests.post(api_url, headers=headers, json={
                    "model": "gpt-4o",
                    "messages": st.session_state.messages + [{"role": "user", "content": iteration_prompt[st.session_state.language]}],
                    "temperature": 0.7,
                    "max_tokens": 1000
                })
                
                response.raise_for_status()
                response_data = response.json()
                
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    reply = response_data["choices"][0]["message"]["content"]
                    response_time = time.time() - start_time
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": reply,
                        "response_time": response_time
                    })
                    st.chat_message("assistant", avatar="logos/ism.png").write(reply)
                    st.markdown(f'<div class="response-time">Antwortzeit: {response_time:.1f} Sekunden</div>', unsafe_allow_html=True)
                else:
                    st.error("Unerwartetes Antwortformat von der API. Bitte versuche es später erneut.")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"Fehler bei der API-Anfrage: {str(e)}")
            except (KeyError, ValueError) as e:
                st.error(f"Fehler beim Verarbeiten der API-Antwort: {str(e)}") 