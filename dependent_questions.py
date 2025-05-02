import streamlit as st
import requests

# --- OpenAI API Konfiguration ---
api_key = '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'
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

st.title("🎓 Karriere-Coach Chatbot")

# Willkommens-Text
st.markdown("""
Willkommen beim Karriere-Coach 🤝  
Hier bekommst du keine "goldene Lösung", sondern Denkanstöße und neue Perspektiven.  
Der Chat soll dir helfen, deine eigenen Ideen zu sortieren und mutige nächste Schritte zu entdecken.
""")

# Benutzerinformationen
vorname = st.text_input("Vorname")
email = st.text_input("E-Mail")

# Datenschutz und Kontakt
dsgvo_zustimmung = st.checkbox("Ich stimme der [Datenverarbeitung gemäß DSGVO](https://deine-datenschutzseite.de) zu.", help="Ohne Zustimmung kann der Chat nicht starten.")
kontakt_erlaubnis = st.checkbox("Ich bin einverstanden, dass ihr mich per E-Mail kontaktiert.")

# --- Hauptziel-Auswahl ---
ziel = st.radio(
    "Worum geht es dir gerade?",
    ["Ich suche meinen Beruf", "Ich überlege Studium oder Ausbildung", "Ich will ein Gap Year planen"],
    key="ziel"
)

# --- Zusatzfragen basierend auf Hauptziel ---
zusatz_info = ""
if ziel == "Ich suche meinen Beruf":
    interesse = st.text_input("Was interessiert dich aktuell besonders?")
    staerken = st.multiselect("Welche Stärken passen zu dir?", ["analytisch", "kreativ", "kommunikativ", "teamfähig", "organisiert", "hilfsbereit"])
    zusatz_info = f"Der/die Nutzer:in heißt {vorname}, sucht Orientierung für die Berufswahl, interessiert sich für {interesse}, Stärken: {', '.join(staerken)}."
elif ziel == "Ich überlege Studium oder Ausbildung":
    wichtig = st.selectbox("Was ist dir dabei wichtiger?", ["Praxis", "Theorie", "Beides"])
    fach = st.text_input("In welchem Bereich möchtest du dich evtl. weiterbilden?")
    zusatz_info = f"Der/die Nutzer:in heißt {vorname}, überlegt zwischen Studium und Ausbildung, bevorzugt {wichtig}, interessiert an {fach}."
elif ziel == "Ich will ein Gap Year planen":
    aktivitaeten = st.multiselect("Was möchtest du im Gap Year machen?", ["Reisen", "Arbeiten", "Soziales", "Lernen", "Praktikum"])
    ort = st.text_input("Gibt es bestimmte Orte oder Länder, die dich reizen?")
    zusatz_info = f"Der/die Nutzer:in heißt {vorname}, plant ein Gap Year, möchte dabei {', '.join(aktivitaeten)} machen und denkt an {ort}."

# --- Chat-Start bei vollständigen Informationen ---
if st.button("✅ Chat starten", disabled=not (vorname and email and dsgvo_zustimmung and kontakt_erlaubnis)):
    system_prompt = base_prompt + "\n\n" + zusatz_info
    st.session_state.messages = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": "Hi 👋 Schön, dass du da bist. Worüber möchtest du heute sprechen?"}
    ]
    st.session_state.chat_started = True

# --- Chat-Interface ---
if st.session_state.get("chat_started", False):
    st.divider()
    st.header("🗨️ Dein Coaching-Chat")

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
                    "model": "gpt-4o",
                    "messages": st.session_state.messages,
                    "temperature": 0.7,
                    "max_tokens": 1000
                })
                reply = response.json()["choices"][0]["message"]["content"]
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.chat_message("assistant").write(reply)
