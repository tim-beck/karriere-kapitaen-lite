import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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

# --- System Prompt ---
base_prompt = """
Du bist ein inspirierender Karriere-Coach für die ISM International School of Management.
Deine Aufgabe ist es, basierend auf den gewählten Studiengängen und Zielen der Person eine motivierende Zukunftsversion zu entwickeln.
Stelle keine Diagnosen und gib keine vorschnellen Ratschläge. 
Fokussiere dich darauf, neue Perspektiven zu eröffnen und Denkanstöße zu geben.
"""

# Custom CSS für ISM Branding
st.markdown("""
    <style>
    .stApp header {
        background-color: #003366;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 ISM Berufsvisionen")

# Willkommens-Text
st.markdown("""
Willkommen bei den ISM Berufsvisionen! 💙 
Hier entwickelst du deine persönliche Zukunftsversion basierend auf deinen Wünschen und Zielen.
Wichtig: Bitte schreibe hier keine personenbezogenen Daten hin.
""")

# --- Hauptfragen ---
st.subheader("Deine Wünsche und Ziele")

studiengaenge = st.text_area(
    "Welche ISM-Studiengänge interessieren dich besonders?",
    help="⚠️ Bitte gib hier keine personenbezogenen Daten ein"
)

ziele = st.text_area(
    "Was möchtest du in deinem Beruf erreichen? (z.B. bestimmte Position, Gehalt, Verantwortung)",
    help="⚠️ Bitte gib hier keine personenbezogenen Daten ein"
)

werte = st.multiselect(
    "Was ist dir in deinem Beruf wichtig?",
    options=[
        "Work-Life-Balance",
        "Teamarbeit",
        "Kreativität",
        "Verantwortung",
        "Internationalität",
        "Karriereentwicklung",
        "Flexibilität",
        "Nachhaltigkeit",
        "Innovation",
        "Sicherheit"
    ],
    help="⚠️ Wähle die für dich wichtigsten Aspekte aus"
)

# --- Berufsvisionen generieren ---
if st.button("🎯 Berufsvisionen entwickeln"):
    if not (studiengaenge and ziele and werte):
        st.warning("Bitte fülle alle Felder aus.")
    else:
        # Erstelle den Prompt für die Berufsvisionen
        vision_prompt = f"""
        Basierend auf folgenden Informationen, entwickle eine inspirierende Zukunftsversion für das Jahr 2035:
        
        Interessante Studiengänge: {studiengaenge}
        Berufliche Ziele: {ziele}
        Wichtige Werte: {', '.join(werte)}
        
        WICHTIG - Zeitliche Einordnung:
        - Aktuelles Jahr: 2025
        - Bachelor-Abschluss (3 Jahre): 2028
        - Master-Abschluss (2 Jahre): 2026
        - Zieljahr der Vision: 2035
        
        WICHTIG - Realistische Karriereentwicklung:
        - Nach 10 Jahren Berufserfahrung sind typische Positionen:
          * Teamleitung oder Projektleitung
          * Senior Spezialist/in
          * Abteilungsleitung in kleineren Teams
          * Bereichsleitung in mittelgroßen Unternehmen
        - KEINE CEO, C-Level oder Geschäftsführungspositionen
        - Realistische Gehaltsentwicklung
        - Typische Karriereschritte und Verantwortungsbereiche
        
        Erstelle:
        1. Eine Übersicht des Karrierewegs von 2025 bis 2035 (in Stichpunkten)
        2. Einen detaillierten Absatz zu einer möglichen Lebensrealität im Jahr 2035
        
        WICHTIG für die Lebensrealität:
        - Beschreibe einen typischen Arbeitstag sehr konkret
        - Nenne spezifische Unternehmen/Organisationen, bei denen die Person arbeitet
        - Erkläre, wie die Person ihre Werte im Arbeitsalltag lebt
        - Beschreibe die Work-Life-Balance und das Privatleben
        
        Formatiere die Antwort wie folgt:
        
        🎯 Dein Karriereweg 2025-2035
        ---------------------------
        [Stichpunkte zum Karriereweg, beginnend mit dem Studium 2025]
        
        🌟 Eine mögliche Lebensrealität im Jahr 2035
        ------------------------------------------
        [Konkrete Beschreibung mit spezifischen Unternehmen und typischem Tagesablauf]
        """
        
        with st.spinner("💭 Entwickle deine Berufsvisionen..."):
            try:
                response = requests.post(api_url, headers=headers, json={
                    "model": "gpt-4",
                    "messages": [
                        {"role": "system", "content": base_prompt},
                        {"role": "user", "content": vision_prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1000
                })
                
                response.raise_for_status()
                response_data = response.json()
                
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    vision = response_data["choices"][0]["message"]["content"]
                    st.session_state.messages = [
                        {"role": "system", "content": base_prompt},
                        {"role": "assistant", "content": vision}
                    ]
                    st.session_state.chat_started = True
                    st.session_state.first_round = True
                else:
                    st.error("Unerwartetes Antwortformat von der API. Bitte versuche es später erneut.")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"Fehler bei der API-Anfrage: {str(e)}")
            except (KeyError, ValueError) as e:
                st.error(f"Fehler beim Verarbeiten der API-Antwort: {str(e)}")

# --- Chat-Interface für Feedback und Alternative ---
if st.session_state.get("chat_started", False):
    st.divider()
    st.header("💬 Dein Feedback")

    # Chatverlauf anzeigen
    for msg in st.session_state.messages[1:]:
        st.chat_message("user" if msg["role"] == "user" else "assistant").write(msg["content"])

    # Nachrichteneingabe
    user_input = st.chat_input("Wie findest du diese Vision? Möchtest du es dir anders vorstellen?")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

        with st.spinner("💭 Entwickle eine alternative Vision..."):
            try:
                alternative_prompt = f"""
                Basierend auf dem Feedback des Nutzers, entwickle eine alternative Zukunftsversion.
                Berücksichtige die ursprünglichen Wünsche und Ziele, aber mit einem anderen Ansatz.
                
                Formatiere die Antwort wie folgt:
                
                🔄 Alternative Vision
                --------------------
                [Beschreibung der alternativen Vision]
                
                💫 Warum dieser Ansatz?
                ----------------------
                [Begründung für den alternativen Ansatz]
                """
                
                response = requests.post(api_url, headers=headers, json={
                    "model": "gpt-4",
                    "messages": st.session_state.messages + [{"role": "user", "content": alternative_prompt}],
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