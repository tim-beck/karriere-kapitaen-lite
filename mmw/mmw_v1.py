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
Du bist ein inspirierender KI-Coach für Berufsorientierung.
Deine Aufgabe ist es, basierend auf den Interessen und Stärken des Nutzers passende Berufsinspirationen zu geben.
Stelle keine Diagnosen und gib keine vorschnellen Ratschläge. 
Fokussiere dich darauf, neue Perspektiven zu eröffnen und Denkanstöße zu geben.
"""

# Custom CSS für bordeaux rotes Branding
st.markdown("""
    <style>
    .stApp header {
        background-color: #800020;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 Mein Mutiger Weg Berufsinspirationen")

# Willkommens-Text
st.markdown("""
Willkommen! 💙 Hier bekommst du neue Perspektiven für deine Berufswahl.
Wichtig: Bitte schreibe hier keine personenbezogenen Daten hin.
""")

# --- Hauptfragen ---
st.subheader("Deine Berufswünsche und Stärken")

traumjob = st.text_area(
    "Was sind deine wichtigsten Kriterien für deinen Traumjob?",
    help="⚠️ Bitte gib hier keine personenbezogenen Daten ein (z. B. deinen Namen, deine Adresse oder deine Schule)"
)

interessen = st.text_area(
    "Was sind deine Top 3 Interessen?",
    help="⚠️ Bitte gib hier keine personenbezogenen Daten ein (z. B. deinen Namen, deine Adresse oder deine Schule)"
)

staerken = st.text_area(
    "Was sind deine Top 3 Stärken?",
    help="⚠️ Bitte gib hier keine personenbezogenen Daten ein (z. B. deinen Namen, deine Adresse oder deine Schule)"
)

# --- Berufsinspirationen generieren ---
if st.button("🎯 Berufsinspirationen erhalten"):
    if not (traumjob and interessen and staerken):
        st.warning("Bitte fülle alle Felder aus.")
    else:
        # Erstelle den Prompt für die Berufsinspirationen
        inspiration_prompt = f"""
        Basierend auf folgenden Informationen, gib 5 konkrete Berufsinspirationen:
        
        Traumjob-Kriterien: {traumjob}
        Top 3 Interessen: {interessen}
        Top 3 Stärken: {staerken}
        
        Für jeden Beruf:
        1. Nenne den Berufstitel
        2. Erkläre kurz, warum dieser Beruf passen könnte
        3. Gib 2-3 Kernaufgaben des Berufs
        
        Formatiere die Antwort übersichtlich mit Emojis und Absätzen.
        """
        
        with st.spinner("💭 Generiere deine Berufsinspirationen..."):
            try:
                response = requests.post(api_url, headers=headers, json={
                    "model": "gpt-4",
                    "messages": [
                        {"role": "system", "content": base_prompt},
                        {"role": "user", "content": inspiration_prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1000
                })
                
                # Überprüfe den Response-Status
                response.raise_for_status()
                
                # Versuche die Antwort zu parsen
                response_data = response.json()
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    inspirations = response_data["choices"][0]["message"]["content"]
                    # Initialisiere Chat
                    st.session_state.messages = [
                        {"role": "system", "content": base_prompt},
                        {"role": "assistant", "content": inspirations}
                    ]
                    st.session_state.chat_started = True
                else:
                    st.error("Unerwartetes Antwortformat von der API. Bitte versuche es später erneut.")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"Fehler bei der API-Anfrage: {str(e)}")
            except (KeyError, ValueError) as e:
                st.error(f"Fehler beim Verarbeiten der API-Antwort: {str(e)}")

# --- Chat-Interface ---
if st.session_state.get("chat_started", False):
    st.divider()
    st.header("💬 Dein Feedback")

    # Chatverlauf anzeigen
    for msg in st.session_state.messages[1:]:  # System-Prompt überspringen
        st.chat_message("user" if msg["role"] == "user" else "assistant").write(msg["content"])

    # Nachrichteneingabe
    user_input = st.chat_input("Was denkst du zu deinen Berufsinspirationen?")
    if user_input:
        # Sofortige Anzeige der Nutzernachricht
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

        with st.spinner("💭 Denke nach..."):
            try:
                response = requests.post(api_url, headers=headers, json={
                    "model": "gpt-4",
                    "messages": st.session_state.messages,
                    "temperature": 0.7,
                    "max_tokens": 1000
                })
                
                # Überprüfe den Response-Status
                response.raise_for_status()
                
                # Versuche die Antwort zu parsen
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