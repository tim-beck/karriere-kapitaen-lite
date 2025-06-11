import streamlit as st
import requests
import os
from dotenv import load_dotenv
import base64

# Set page config
st.set_page_config(
    page_title="Mini-Coaching",
    page_icon="🎓",
    layout="centered"
)

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

# Define all texts in both languages
LANGUAGES = {
    "DE": {
        "title": "🎓 Karriere-Kapitän Mini-Coaching",
        "welcome": "👋 Hey! Hier findest du Ideen für deine Zukunft, passend zu dir. Vergiss nicht, nur du entscheidest, was zu dir passt.",
        "support_needed": "Wobei brauchst du gerade Unterstützung?",
        "support_options": ["Beruf finden", "Studium oder Ausbildung wählen", "Gap Year planen"],
        "career_goals": "Was genau wünschst du dir vom Karriere-Kapitän?",
        "free_time": "Wie verbringst du am liebsten deine Freizeit? Warum?",
        "strengths": "Was kannst du gut – oder wofür wurdest du schonmal gelobt?",
        "enjoyable_work": "Was könntest du dir vorstellen, den ganzen Tag zu tun, ohne dass es dich langweilt?",
        "work_values": "Was ist dir bei der Arbeit am wichtigsten?",
        "work_values_options": [
            "Sicherheit & Stabilität",
            "Selbstverwirklichung & Kreativität",
            "Einfluss & Verantwortung",
            "Soziales Engagement & Zusammenarbeit",
            "Leistung & Weiterentwicklung",
            "Abwechslung & Abenteuer",
            "Ich weiß noch nicht"
        ],
        "activity_types": "Welche Art von Tätigkeiten reizt dich am meisten?",
        "activity_types_options": [
            "Praktisch–handwerklich (z. B. reparieren, bauen, mit Werkzeugen arbeiten)",
            "Wissenschaftlich–analytisch (z. B. forschen, Probleme logisch lösen)",
            "Künstlerisch–kreativ (z. B. gestalten, schreiben, musizieren)",
            "Sozial–unterstützend (z. B. helfen, lehren, betreuen)",
            "Unternehmerisch–überzeugend (z. B. verkaufen, leiten, motivieren)",
            "Organisatorisch–strukturiert (z. B. planen, verwalten, analysieren)",
            "Ich weiß noch nicht"
        ],
        "content_areas": "Mit welchen Inhalten beschäftigst du dich gerne?",
        "content_areas_options": [
            "Technik, Maschinen & IT",
            "Menschen, Gesellschaft & Bildung",
            "Sprache, Medien & Kultur",
            "Wirtschaft, Recht & Organisation",
            "Naturwissenschaften & Umwelt",
            "Medizin, Gesundheit & Pflege",
            "Ich weiß noch nicht"
        ],
        "work_environment": "In welcher Umgebung arbeitest du am liebsten?",
        "work_environment_options": [
            "In Bewegung, im Freien oder an wechselnden Orten",
            "In einem Büro mit klaren Prozessen",
            "In einem Labor oder technischen Umfeld",
            "In einem kreativen, offenen Umfeld",
            "In engem Austausch mit anderen Menschen",
            "In Führungs- oder Entscheidungspositionen",
            "Ich weiß noch nicht"
        ],
        "gap_year_goal": "Was ist dein Hauptziel für dein Gap Year?",
        "gap_year_goal_options": [
            "Neue Erfahrungen sammeln",
            "Soziale oder ökologische Wirkung erzielen",
            "Die Welt entdecken und reisen",
            "Eine neue Sprache oder Kultur lernen",
            "Zeit zur beruflichen Orientierung nutzen",
            "Geld verdienen und unabhängig sein",
            "Noch offen – ich möchte verschiedene Dinge ausprobieren",
            "Ich weiß noch nicht"
        ],
        "gap_year_duration": "Wie lange möchtest du dein Gap Year gestalten?",
        "gap_year_duration_options": [
            "Bis zu 3 Monate (z. B. Sommerpraktikum, Kurzzeitprojekt)",
            "3–6 Monate (z. B. Halbjahresprojekt, Sprachreise)",
            "6–12 Monate (z. B. FSJ, Freiwilligendienst, Work & Travel)",
            "Noch unklar – ich will erstmal herausfinden, was möglich ist",
            "Ich weiß noch nicht"
        ],
        "gap_year_activities": "Welche Aktivitäten könntest du dir vorstellen?",
        "gap_year_activities_options": [
            "Au Pair",
            "Bundeswehr",
            "Direkt beginnen mit Ausbildung/Studium",
            "Freiwilliges Soziales/ Ökologisches/ Kulturelles Jahr",
            "Ich weiß noch nicht",
            "Jobben und Geld sparen",
            "Online Kurse",
            "Praktikum zur Berufsorientierung",
            "Sprachkurs",
            "Studienorientierung (z.B. Studium Generale)",
            "Work & Travel oder saisonale Jobs im Ausland",
            "Etwas anderes",
            "Ich weiß noch nicht"
        ],
        "gap_year_experiences": "Was würdest du gern erleben oder lernen, bevor du ins Berufsleben oder Studium startest?",
        "gap_year_concerns": "Was hält dich aktuell noch davon ab, ein Gap Year zu planen oder umzusetzen?",
        "start_chat": "✅ Chat starten",
        "thinking": "💭 Denke nach...",
        "chat_title": "💬 Dein Karriere-Kapitän-Chat",
        "chat_input": "Was möchtest du besprechen?",
        "footer_text": "Studien- und Berufsberatung mit KI, jetzt Vollversion testen bei",
        "privacy_text": "Datenschutzhinweise",
        "max_requests": "Du hast das Maximum von 7 Anfragen erreicht. Bitte starte eine neue Sitzung, wenn du weitere Fragen hast.",
        "remaining_requests": "Verbleibende Anfragen",
        "subjects": "Welche Schulfächer interessieren dich am meisten? In welchen Fächern bist du besonders gut?",
        "open_questions_prompt": "Willst du noch bessere Inspirationen erhalten, indem du offene Fragen beantwortest?",
        "open_questions": "Offene Fragen",
        "yes": "Ja",
        "no": "Nein",
        "study_type": "Wie würdest du deinen Lerntyp beschreiben?",
        "study_type_options": [
            "Ich lerne lieber praktisch durch Ausprobieren",
            "Ich lese und verstehe gern komplexe Inhalte",
            "Ich brauche eine klare Struktur und Anleitung",
            "Ich weiß noch nicht"
        ],
        "learning_environment": "Welche Lernumgebung trifft am ehesten auf deine Bedürfnisse zu?",
        "learning_environment_options": [
            "Metropol-Universität - Wenig Lehrkräfte pro Lernende, viel Freiheit, breites Campusleben",
            "Praxis-FH - Mittlere Zahl an Lehrkräften pro Lernende, praxisnah, moderat strukturiert",
            "Private Kleinhochschule - Viele Lehrkräfte pro Lernende, enge Betreuung, wenig Campus",
            "Dual / Ausbildungsintegriert - Sehr viele Lehrkräfte pro Lernende, verschult, kaum Campusleben",
            "Ich weiß noch nicht"
        ],
        "version_comparison_title": "Die Vollversion unterscheidet sich in 3 Merkmalen:",
        "version_comparison_features": [
            "Unlimitierte Anfragen - So viele Fragen wie du möchtest",
            "Noch mehr Fragen an dich - Für noch personalisiertere Inspirationen",
            "Zuverlässigere Antworten - Basierend auf unserer Datenbank statt nur dem Sprachmodell"
        ]
    },
    "EN": {
        "title": "🎓 Karriere-Kapitän Mini-Coaching",
        "welcome": "👋 Hey! Here you'll find ideas for your future, tailored to you. Don't forget, only you decide what fits you best.",
        "support_needed": "What kind of support do you need right now?",
        "support_options": ["Find a career", "Choose study or training", "Plan gap year"],
        "career_goals": "What exactly do you want from Karriere-Kapitän?",
        "free_time": "How do you like to spend your free time? Why?",
        "strengths": "What are you good at – or what have you been praised for?",
        "enjoyable_work": "What could you imagine doing all day without getting bored?",
        "work_values": "What is most important to you at work?",
        "work_values_options": [
            "Security & Stability",
            "Self-realization & Creativity",
            "Influence & Responsibility",
            "Social Engagement & Collaboration",
            "Achievement & Development",
            "Variety & Adventure",
            "I don't know yet"
        ],
        "activity_types": "Which type of activities interests you the most?",
        "activity_types_options": [
            "Practical–manual (e.g., repairing, building, working with tools)",
            "Scientific–analytical (e.g., researching, solving problems logically)",
            "Artistic–creative (e.g., designing, writing, making music)",
            "Social–supportive (e.g., helping, teaching, caring)",
            "Entrepreneurial–persuasive (e.g., selling, leading, motivating)",
            "Organizational–structured (e.g., planning, managing, analyzing)",
            "I don't know yet"
        ],
        "content_areas": "Which content areas interest you?",
        "content_areas_options": [
            "Technology, Machines & IT",
            "People, Society & Education",
            "Language, Media & Culture",
            "Business, Law & Organization",
            "Natural Sciences & Environment",
            "Medicine, Health & Care",
            "I don't know yet"
        ],
        "work_environment": "In which environment do you prefer to work?",
        "work_environment_options": [
            "In motion, outdoors or at changing locations",
            "In an office with clear processes",
            "In a laboratory or technical environment",
            "In a creative, open environment",
            "In close exchange with other people",
            "In leadership or decision-making positions",
            "I don't know yet"
        ],
        "study_type": "How would you describe your learning style?",
        "study_type_options": [
            "I prefer learning through practical experience",
            "I enjoy reading and understanding complex content",
            "I need clear structure and guidance",
            "I don't know yet"
        ],
        "learning_environment": "Which learning environment best matches your needs?",
        "learning_environment_options": [
            "Metropolitan University - Few teachers per learner, lots of freedom, broad campus life",
            "Applied Sciences University - Medium number of teachers per learner, practical, moderately structured",
            "Private Small College - Many teachers per learner, close supervision, little campus life",
            "Dual / Integrated Training - Very many teachers per learner, school-like structure, minimal campus life",
            "I don't know yet"
        ],
        "gap_year_goal": "What is your main goal for your gap year?",
        "gap_year_goal_options": [
            "Gain new experiences",
            "Make a social or ecological impact",
            "Discover the world and travel",
            "Learn a new language or culture",
            "Use time for career orientation",
            "Earn money and become independent",
            "Still open – I want to try different things",
            "I don't know yet"
        ],
        "gap_year_duration": "How long would you like to plan your gap year?",
        "gap_year_duration_options": [
            "Up to 3 months (e.g., summer internship, short-term project)",
            "3-6 months (e.g., half-year project, language trip)",
            "6-12 months (e.g., voluntary service, work & travel)",
            "Still unclear – I want to find out what's possible first",
            "I don't know yet"
        ],
        "gap_year_activities": "Which activities could you imagine?",
        "gap_year_activities_options": [
            "Au Pair",
            "Military Service",
            "Start training/studies directly",
            "Voluntary Social/Ecological/Cultural Year",
            "I don't know yet",
            "Work and save money",
            "Online Courses",
            "Internship for career orientation",
            "Language Course",
            "Study orientation (e.g., General Studies)",
            "Work & Travel or seasonal jobs abroad",
            "Something else",
            "I don't know yet"
        ],
        "gap_year_experiences": "What would you like to experience or learn before starting your career or studies?",
        "gap_year_concerns": "What's currently holding you back from planning or implementing a gap year?",
        "start_chat": "✅ Start Chat",
        "thinking": "💭 Thinking...",
        "chat_title": "💬 Your Karriere-Kapitän Chat",
        "chat_input": "What would you like to discuss?",
        "footer_text": "Study and Career Counseling with AI, try the full version at",
        "privacy_text": "Privacy Policy",
        "max_requests": "You have reached the maximum of 7 requests. Please start a new session if you have more questions.",
        "remaining_requests": "Remaining requests",
        "subjects": "Which school subjects interest you the most? In which subjects are you particularly good?",
        "open_questions_prompt": "Would you like to get even better inspirations by answering open questions?",
        "open_questions": "Open Questions",
        "yes": "Yes",
        "no": "No",
        "version_comparison_title": "The full version differs in 3 features:",
        "version_comparison_features": [
            "Unlimited requests - Ask as many questions as you want",
            "More questions for you - For even more personalized inspirations",
            "More reliable answers - Based on our database instead of just the language model"
        ]
    }
}

# --- Session State Initialisierung ---
# Speichere den Sprachzustand
if 'language' not in st.session_state:
    st.session_state.language = "DE"

# Initialize request counter
if 'request_count' not in st.session_state:
    st.session_state.request_count = 0

# Get current language texts
current_lang = LANGUAGES[st.session_state.language]

# --- UI Components ---
# Create header with language toggle and privacy notice
col1, col2, col3 = st.columns([0.6, 0.2, 0.2])
with col1:
    if st.button("🇩🇪 DE" if st.session_state.language == "EN" else "🇬🇧 ENG"):
        st.session_state.language = "EN" if st.session_state.language == "DE" else "DE"
        st.rerun()

with col3:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(script_dir, "logos", "kk_short.png")
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 1rem; justify-content: flex-end;">
            <a href="https://app.karriere-kapitaen.com" target="_blank">
                <img src="data:image/png;base64,{base64.b64encode(open(logo_path, 'rb').read()).decode()}" alt="Karriere-Kapitän Logo" style="height: 30px; width: auto;">
            </a>
            <a href="https://karriere-kapitaen.com/datenschutzhinweise-mini-coaching/" target="_blank" style="color: #666; text-decoration: none; font-size: 0.8em;">{current_lang["privacy_text"]}</a>
        </div>
    """, unsafe_allow_html=True)

# --- System Prompt (wird mit User-Infos ergänzt) ---
base_prompt = {
    "DE": """
Du bist ein einfühlsamer und klarer KI-Coach für Studien- und Berufsorientierung.
Nutze Methoden aus dem systemischen Coaching (z. B. zirkuläre Fragen, Ressourcenorientierung, Perspektivwechsel) 
und Best Practices aus der Berufsberatung, um dem/der Nutzer:in zu helfen, eigene Einsichten zu gewinnen.

Wichtige Hinweise:
- Duze den Nutzer/die Nutzerin (verwende "du" statt "Sie")
- Stelle keine Diagnosen und gib keine vorschnellen Ratschläge
- Stelle stattdessen offene, reflektierende Fragen
- Hilf beim Sortieren von Gedanken
- Biete bei Bedarf passende Informationen an
""",
    "EN": """
You are an empathetic and clear AI coach for study and career orientation.
Use methods from systemic coaching (e.g., circular questions, resource orientation, perspective shifts)
and best practices from career counseling to help the user gain their own insights.

Important notes:
- Use informal "you" instead of formal address
- Don't make diagnoses or give premature advice
- Instead, ask open, reflective questions
- Help with organizing thoughts
- Offer relevant information when needed
"""
}

st.title(current_lang["title"])

# Willkommens-Text
st.markdown(f"""
<div style="color: #000000; margin-bottom: 1em; font-size: 1.1em;">
    <p style="margin-bottom: 0.5em;">{current_lang["welcome"]}</p>
    <p>ℹ️ Wichtig: Bitte keine persönlichen Daten eingeben (z.B. Name oder Kontaktdaten).</p>
</div>
""", unsafe_allow_html=True)

# Add version number at the bottom
st.markdown("""
<div style="position: fixed; bottom: 0; right: 0; padding: 10px; font-size: 0.8em; color: #666;">
    v1.0.0
</div>
""", unsafe_allow_html=True)

# Hauptziel-Auswahl
ziel = st.radio(
    current_lang["support_needed"],
    current_lang["support_options"],
    key="ziel"
)

# --- Pfadspezifische Fragen ---
zusatz_info = ""

if ziel == current_lang["support_options"][0]:  # "Beruf finden" or "Find a career"
    work_values = st.multiselect(
        current_lang["work_values"],
        current_lang["work_values_options"],
        key="work_values",
        help="This question is based on scientific models of values and motivation. It helps us understand what's important to you in your career."
    )
    
    activity_types = st.multiselect(
        current_lang["activity_types"],
        current_lang["activity_types_options"],
        key="activity_types",
        help="This question is based on the RIASEC model, one of the best-known career choice models. It helps us understand which types of activities interest you."
    )
    
    work_environment = st.multiselect(
        current_lang["work_environment"],
        current_lang["work_environment_options"],
        key="work_environment",
        help="This question is based on research about person-environment fit. It helps us understand in which environment you feel most comfortable."
    )
    
    # Ask if user wants to answer open questions
    show_open_questions = st.radio(
        current_lang["open_questions_prompt"],
        [current_lang["no"], current_lang["yes"]],
        horizontal=True
    )
    
    # Show open questions only if user wants to
    if show_open_questions == current_lang["yes"]:
        st.markdown("---")
        st.markdown(f"##### {current_lang['open_questions']}")
        enjoyable_work = st.text_input(current_lang["enjoyable_work"])
        strengths = st.text_input(current_lang["strengths"])
    
    # Create zusatz_info only with the fields that were filled out
    info_parts = []
    if work_values:
        info_parts.append(f"Important values: {', '.join(work_values)}")
    if activity_types:
        info_parts.append(f"Preferred activity types: {', '.join(activity_types)}")
    if work_environment:
        info_parts.append(f"Preferred work environment: {', '.join(work_environment)}")
    if show_open_questions == current_lang["yes"]:
        if strengths:
            info_parts.append(f"Strengths: {strengths}")
        if enjoyable_work:
            info_parts.append(f"Interesting activities: {enjoyable_work}")
    
    zusatz_info = f"The user is looking for career orientation. {' '.join(info_parts)}."

elif ziel == current_lang["support_options"][1]:  # "Studium oder Ausbildung wählen" or "Choose study or training"
    # Mandatory MC questions
    learning_environment = st.multiselect(
        current_lang["learning_environment"],
        current_lang["learning_environment_options"],
        key="learning_environment",
        help="This question helps us understand in which environment you feel most comfortable and how you learn best."
    )
    
    study_type = st.multiselect(
        current_lang["study_type"],
        current_lang["study_type_options"],
        key="study_type",
        help="This question is based on learning style models and helps us understand how you learn best."
    )
    
    content_areas = st.multiselect(
        current_lang["content_areas"],
        current_lang["content_areas_options"],
        key="content_areas",
        help="This question is based on occupational field classifications (e.g., BIBB, AMS, ONET)."
    )
    
    # Ask if user wants to answer open questions
    show_open_questions = st.radio(
        current_lang["open_questions_prompt"],
        [current_lang["no"], current_lang["yes"]],
        horizontal=True
    )
    
    # Show open questions only if user wants to
    if show_open_questions == current_lang["yes"]:
        st.markdown("---")
        st.markdown(f"##### {current_lang['open_questions']}")
        subjects = st.text_input(current_lang["subjects"])
        free_time = st.text_input(current_lang["free_time"])
        strengths = st.text_input(current_lang["strengths"])
    
    # Create zusatz_info only with the fields that were filled out
    info_parts = []
    if learning_environment:
        info_parts.append(f"Preferred learning environment: {', '.join(learning_environment)}")
    if study_type:
        info_parts.append(f"Learning style: {', '.join(study_type)}")
    if content_areas:
        info_parts.append(f"Interesting content: {', '.join(content_areas)}")
    if show_open_questions == current_lang["yes"]:
        if subjects:
            info_parts.append(f"School subjects: {subjects}")
        if free_time:
            info_parts.append(f"Free time interests: {free_time}")
        if strengths:
            info_parts.append(f"Strengths: {strengths}")
    
    zusatz_info = f"The user is looking for orientation for study or training. {' '.join(info_parts)}."

elif ziel == current_lang["support_options"][2]:  # "Gap Year planen" or "Plan gap year"
    # Mandatory MC questions
    gap_year_goal = st.multiselect(
        current_lang["gap_year_goal"],
        current_lang["gap_year_goal_options"],
        key="gap_year_goal",
        help="This question helps us understand what you want to achieve with your gap year."
    )
    
    gap_year_duration = st.multiselect(
        current_lang["gap_year_duration"],
        current_lang["gap_year_duration_options"],
        key="gap_year_duration",
        help="This question helps us find suitable options for your time planning."
    )
    
    gap_year_activities = st.multiselect(
        current_lang["gap_year_activities"],
        current_lang["gap_year_activities_options"],
        key="gap_year_activities",
        help="This question helps us suggest specific activities that match your goals."
    )
    
    # Ask if user wants to answer open questions
    show_open_questions = st.radio(
        current_lang["open_questions_prompt"],
        [current_lang["no"], current_lang["yes"]],
        horizontal=True
    )
    
    # Show open questions only if user wants to
    if show_open_questions == current_lang["yes"]:
        st.markdown("---")
        st.markdown(f"##### {current_lang['open_questions']}")
        gap_year_experiences = st.text_input(current_lang["gap_year_experiences"])
        gap_year_concerns = st.text_input(current_lang["gap_year_concerns"])
    
    # Create zusatz_info only with the fields that were filled out
    info_parts = []
    if gap_year_goal:
        info_parts.append(f"Main goal: {', '.join(gap_year_goal)}")
    if gap_year_duration:
        info_parts.append(f"Time planning: {', '.join(gap_year_duration)}")
    if gap_year_activities:
        info_parts.append(f"Interesting activities: {', '.join(gap_year_activities)}")
    if show_open_questions == current_lang["yes"]:
        if gap_year_experiences:
            info_parts.append(f"Desired experiences: {gap_year_experiences}")
        if gap_year_concerns:
            info_parts.append(f"Concerns: {gap_year_concerns}")
    
    zusatz_info = f"The user is planning a gap year. {' '.join(info_parts)}."

# --- Chat-Start bei vollständigen Informationen ---
if st.button(current_lang["start_chat"]):
    if st.session_state.request_count >= 7:
        st.warning(current_lang["max_requests"])
    else:
        # Erstelle den initialen System-Prompt mit allen gesammelten Informationen
        system_prompt = base_prompt[st.session_state.language] + "\n\n" + zusatz_info
        
        # Erstelle den Prompt für die erste Nachricht
        first_message_prompt = {
            "DE": f"""
        Bedanke dich beim Nutzer freundlich für die Angaben.
        Fasse kurz zusammen, wobei der oder die Nutzer*in sich Unterstützung wünscht – orientiere dich dazu an den Antworten zu:
        - Hauptziel: {ziel}
        
        Gib dann ein bis zwei konkrete, neue Ideen oder Denkanstöße, die helfen könnten – passend zur ausgewählten Richtung.
        
        Beziehe dabei auch passende Infos aus den anderen Antworten ein:
        {zusatz_info}
        
        Frag am Ende proaktiv nach:
        "Was davon findest du interessant?" oder "Worüber möchtest du als Nächstes sprechen?"
            """,
            "EN": f"""
            Thank the user warmly for their input.
            Briefly summarize what kind of support the user is looking for – based on their answers to:
            - Main goal: {ziel}
            
            Then provide one or two concrete, new ideas or thought starters that could help – matching the selected direction.
            
            Include relevant information from their other answers:
            {zusatz_info}
            
            Proactively ask at the end:
            "What interests you about this?" or "What would you like to discuss next?"
            """
        }
        
        # Initialisiere die Chat-Historie mit System-Prompt
        st.session_state.messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Generiere die erste Nachricht mit dem Sprachmodell
        with st.spinner(current_lang["thinking"]):
            response = requests.post(api_url, headers=headers, json={
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": first_message_prompt[st.session_state.language]}
                ],
                "temperature": 0.7,
                "max_tokens": 1000
            })
            
            if response.status_code == 200:
                first_message = response.json()["choices"][0]["message"]["content"]
                st.session_state.messages.append({"role": "assistant", "content": first_message})
                st.session_state.chat_started = True
                st.session_state.request_count += 1
            else:
                st.error(f"Error: {response.status_code} - {response.text}")

# --- Chat-Interface ---
if st.session_state.get("chat_started", False):
    st.divider()

    # Show remaining requests in light gray
    st.markdown(f"""
    <div style="color: #888888; margin-bottom: 1em;">
        <strong>{current_lang['remaining_requests']}:</strong> {7 - st.session_state.request_count}
    </div>
    """, unsafe_allow_html=True)

    # Add version comparison text in a gray box with rounded corners
    st.markdown(f"""
    <div style="background-color: #f5f5f5; border-radius: 10px; padding: 1em; margin: 1em 0; border: 1px solid #e0e0e0;">
        <div style="font-size: 0.9em;">
            {current_lang["version_comparison_title"]}
            <ul style="margin-top: 0.5em; margin-bottom: 0.5em;">
                <li><strong>{current_lang["version_comparison_features"][0]}</strong></li>
                <li><strong>{current_lang["version_comparison_features"][1]}</strong></li>
                <li><strong>{current_lang["version_comparison_features"][2]}</strong></li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Maximale Anzahl an Nachrichten: 10 (5 User, 5 Bot)
    max_messages = 10
    current_count = len(st.session_state.messages) - 1  # System-Prompt nicht mitzählen

    # Chatverlauf anzeigen
    for msg in st.session_state.messages[1:]:  # System-Prompt überspringen
        if msg["role"] == "user":
            st.chat_message("user", avatar="lite/logos/kk_icon.png").write(msg["content"])
        else:
            st.chat_message("assistant").write(msg["content"])

    # Nachrichteneingabe oder Limit-Erreichung
    if current_count >= max_messages:
        st.warning("🚫 Du hast das Limit von 10 Nachrichten erreicht.")
    else:
        user_input = st.chat_input(current_lang["chat_input"])
        if user_input:
            if st.session_state.request_count >= 7:
                st.warning(current_lang["max_requests"])
            else:
                # Sofortige Anzeige der Nutzernachricht
                st.session_state.messages.append({"role": "user", "content": user_input})
                st.chat_message("user").write(user_input)

                with st.spinner(current_lang["thinking"]):
                    response = requests.post(api_url, headers=headers, json={
                        "model": "gpt-4",
                        "messages": st.session_state.messages,
                        "temperature": 0.7,
                        "max_tokens": 1000
                    })
                    reply = response.json()["choices"][0]["message"]["content"]
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                    st.chat_message("assistant").write(reply)
                    st.session_state.request_count += 1

# --- Custom CSS ---
st.markdown("""
    <style>
    /* Streamlit Icon Replacement */
    .stApp header img {
        content: url('lite/logos/kk_icon.png');
    }
    
    /* Multiple Choice Styling */
    .stMultiSelect [data-baseweb=select] span {
        background-color: #FF774C !important;
        color: white !important;
    }
    
    /* Input Field Focus Styling */
    .stTextArea textarea:focus,
    .stTextInput input:focus,
    .stMultiSelect [data-baseweb=select] div:focus {
        border-color: #FF774C !important;
        box-shadow: 0 0 0 1px #FF774C !important;
    }
    
    /* Button Styling */
    .stButton button {
        background-color: transparent !important;
        color: #FF774C !important;
        border: 1px solid #FF774C !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton button:hover {
        background-color: #FF774C !important;
        color: white !important;
    }
    
    /* Language Toggle Button (special case) */
    .stButton button:has(span:contains("DE")),
    .stButton button:has(span:contains("ENG")) {
        background-color: #FF774C !important;
        color: white !important;
        border: none !important;
    }
    
    /* Radio Button Styling */
    .stRadio [role="radiogroup"] label {
        color: #FF774C !important;
    }
    
    /* Loading Spinner Styling */
    .stSpinner > div {
        border-color: #FF774C !important;
    }
    
    /* Content Spacing */
    .main .block-container {
        padding-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True) 