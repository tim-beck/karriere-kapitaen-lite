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

# --- System Prompt (wird mit User-Infos ergänzt) ---
base_prompt = """
Du bist ein einfühlsamer und klarer KI-Coach für Studien- und Berufsorientierung.
Nutze Methoden aus dem systemischen Coaching (z. B. zirkuläre Fragen, Ressourcenorientierung, Perspektivwechsel) 
und Best Practices aus der Berufsberatung, um dem/der Nutzer:in zu helfen, eigene Einsichten zu gewinnen.

Stelle keine Diagnosen und gib keine vorschnellen Ratschläge. Stelle stattdessen offene, reflektierende Fragen, 
hilf beim Sortieren von Gedanken und biete bei Bedarf passende Informationen an.
"""

st.title("🎓 Karriere-Kapitän Mini-Coaching")

# Willkommens-Text
st.markdown("""
Willkommen! 💙 Hier bekommst du neue Perspektiven für deine Karriereplanung. 
Wichtig: hier gibt's keine "goldene Lösung", sondern nur Denkanstöße - nur du bist der Kapitän deiner Karriere.
""")

# --- Generelle Fragen ---
st.subheader("Allgemeine Informationen")
vorname = st.text_input("Wie heißt du?")
email = st.text_input("Wie lautet deine E-Mail-Adresse?")

# Datenschutz und Kontakt
dsgvo_zustimmung = st.checkbox(
    "Ich bin mindestens 16 Jahre alt oder habe die Einverständniserklärung meiner Eltern.",
    help="Ohne Zustimmung kann der Chat nicht starten."
)

datenschutz_agb = st.checkbox(
    "Ich habe die [Datenschutzerklärung](https://karriere-kapitaen.com/datenschutz/) und die [AGB](https://karriere-kapitaen.com/agb/) gelesen und stimme der Verarbeitung meiner Daten ausdrücklich zu.",
    help="Ohne Zustimmung kann der Chat nicht starten."
)

openai_zustimmung = st.checkbox(
    "Ich stimme der Verarbeitung der Antworten, die ich hier gebe, durch OpenAI zu.",
    help="Ohne Zustimmung kann der Chat nicht starten."
)

# Hauptziel-Auswahl
ziel = st.radio(
    "Wobei brauchst du gerade Unterstützung?",
    ["Beruf finden", "Studium oder Ausbildung wählen", "Gap Year planen", "Etwas anderes"],
    key="ziel"
)

# Weitere generelle Fragen
wunsch = st.text_input("Was genau wünschst du dir vom Karriere-Kapitän?")
freizeit = st.text_input("Was machst du gerne in deiner Freizeit? Warum?")
staerken = st.text_input("Was kannst du gut – oder wofür wurdest du schonmal gelobt?")

# --- Pfadspezifische Fragen ---
zusatz_info = ""

if ziel == "Studium oder Ausbildung wählen":
    schulfaecher = st.text_input("Welche Schulfächer magst oder mochtest du besonders? Wo warst du besonders gut?")
    ueberlegungen = st.text_input("Was hast du bisher in Richtung Studium oder Ausbildung überlegt? Warum?")
    zusatz_info = f"Der/die Nutzer:in heißt {vorname}, überlegt zwischen Studium und Ausbildung. Besonders interessiert an {schulfaecher}, bisherige Überlegungen: {ueberlegungen}."

elif ziel == "Beruf finden":
    berufsfelder = st.text_input("Welche Berufsfelder findest du spannend? Warum?")
    zusatz_info = f"Der/die Nutzer:in heißt {vorname}, sucht Orientierung für die Berufswahl. Interessante Berufsfelder: {berufsfelder}."

elif ziel == "Gap Year planen":
    gap_year_optionen = st.multiselect(
        "Was könntest du dir für dein Gap Year vorstellen?",
        ["Freiwilliges Soziales/ Ökologisches/ Kulturelles Jahr", "Bundeswehr", "Praktika", "Sprachkurs", 
         "Online Kurse", "Studium Generale/ Orientierungsstudium", "Au Pair", "Work & Travel",
         "Etwas anderes", "Direkt beginnen mit Ausbildung/Studium"]
    )
    zusatz_info = f"Der/die Nutzer:in heißt {vorname}, plant ein Gap Year. Interessante Optionen: {', '.join(gap_year_optionen)}."

elif ziel == "Etwas anderes":
    # Hier können später spezifische Fragen für andere Anliegen hinzugefügt werden
    zusatz_info = f"Der/die Nutzer:in heißt {vorname}, hat ein spezielles Anliegen: {wunsch}."

# --- Chat-Start bei vollständigen Informationen ---
if st.button("✅ Chat starten", disabled=not (vorname and email and dsgvo_zustimmung and datenschutz_agb and openai_zustimmung)):
    # Erstelle den initialen System-Prompt mit allen gesammelten Informationen
    system_prompt = base_prompt + "\n\n" + zusatz_info
    
    # Erstelle den Prompt für die erste Nachricht
    first_message_prompt = f"""
    Bedanke dich beim Nutzer freundlich für die Angaben.
    Fasse kurz zusammen, wobei der oder die Nutzer*in sich Unterstützung wünscht – orientiere dich dazu an den Antworten zu:
    - Hauptziel: {ziel}
    - Wunsch: {wunsch}
    
    Gib dann ein bis zwei konkrete, neue Ideen oder Denkanstöße, die helfen könnten – passend zur ausgewählten Richtung.
    
    Beziehe dabei auch passende Infos aus den anderen Antworten ein:
    - Freizeitaktivitäten: {freizeit}
    - Stärken: {staerken}
    
    Frag am Ende proaktiv nach:
    "Was davon findest du interessant?" oder "Worüber möchtest du als Nächstes sprechen?"
    """
    
    # Initialisiere die Chat-Historie mit System-Prompt
    st.session_state.messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    # Generiere die erste Nachricht mit dem Sprachmodell
    with st.spinner("💭 Bereite deine persönliche Beratung vor..."):
        response = requests.post(api_url, headers=headers, json={
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": first_message_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        })
        first_message = response.json()["choices"][0]["message"]["content"]
        st.session_state.messages.append({"role": "assistant", "content": first_message})
        st.session_state.chat_started = True

# --- Chat-Interface ---
if st.session_state.get("chat_started", False):
    st.divider()
    st.header("💬 Dein Karriere-Kapitän-Chat")

    # Maximale Anzahl an Nachrichten: 10 (5 User, 5 Bot)
    max_messages = 10
    current_count = len(st.session_state.messages) - 1  # System-Prompt nicht mitzählen

    # Chatverlauf anzeigen
    for msg in st.session_state.messages[1:]:  # System-Prompt überspringen
        st.chat_message("user" if msg["role"] == "user" else "assistant").write(msg["content"])

    # Nachrichteneingabe oder Limit-Erreichung
    if current_count >= max_messages:
        st.warning("🚫 Du hast das Limit von 10 Nachrichten erreicht.")

        # --- Call-to-Action am Ende ---
        st.markdown("---")
        st.subheader("🎯 Nächster Schritt?")
        st.write("""
        Wenn du tiefer einsteigen willst, kannst du hier ein kostenloses Orientierungsgespräch buchen.  
        Dabei bekommst du exklusiven Zugang zu unseren trainierten Sprachmodellen für **Berufswahl**, **Studienwahl** und **Ausbildungswahl** sowie tiefgreifende Interviews, die dir bei deiner Orientierung helfen sollen.
        """)
        st.link_button("🔗 Gespräch buchen", "https://dein-buchungslink.de")

        # --- Feedback-Bereich ---
        st.markdown("---")
        st.subheader("📝 Dein Feedback")

        feedback_col1, feedback_col2 = st.columns([1, 3])

        with feedback_col1:
            bewertung = st.radio("Wie fandest du den Chat?", ["👍", "👎"], horizontal=True)

        with feedback_col2:
            kommentar = st.text_area("Möchtest du uns noch etwas mitgeben?", placeholder="Dein Feedback hilft uns, besser zu werden.")

        if st.button("📩 Feedback senden"):
            st.success("Vielen Dank für dein Feedback 🙏")
            st.session_state["feedback"] = {
                "bewertung": bewertung,
                "kommentar": kommentar,
                "vorname": vorname,
                "email": email
            }
    else:
        user_input = st.chat_input("Was möchtest du besprechen?")
        if user_input:
            # Sofortige Anzeige der Nutzernachricht
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.chat_message("user").write(user_input)

            with st.spinner("💭 Denke nach..."):
                response = requests.post(api_url, headers=headers, json={
                    "model": "gpt-4",
                    "messages": st.session_state.messages,
                    "temperature": 0.7,
                    "max_tokens": 1000
                })
                reply = response.json()["choices"][0]["message"]["content"]
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.chat_message("assistant").write(reply)
