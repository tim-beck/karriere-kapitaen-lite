import streamlit as st
import os
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

# --- Language Settings ---
LANGUAGES = {
    "DE": {
        "title": "🎓 ISM Studiengang-Matching",
        "welcome": "Willkommen bei der ISM International School of Management! 💙\nHier findest du deine passenden Studiengänge basierend auf deinen Interessen und Stärken - für dich kuratiert von unserer ISM-KI, ermöglicht durch [Karriere-Kapitän](https://karriere-kapitaen.com).",
        "interests_goals": "Deine Interessen und Ziele",
        "privacy_notice": "ℹ️ **Wichtig:** Bitte keine personenbezogenen Daten eingeben (z.B. Name oder Kontaktdaten).",
        "study_goals": "Was möchtest du später einmal erreichen?",
        "interests": "Was machst du am liebsten in deiner Freizeit?",
        "strengths": "Was sind deine größten Stärken? Wofür wurdest du schonmal gelobt?",
        "aspirations": "Was möchtest du in deinem Leben erreichen? Was sind deine Träume und Ziele?",
        "preferences": "Deine Präferenzen",
        "filter_tip": "💡 Du kannst bei allen Filtern mehrere Optionen auswählen, indem du sie anklickst.",
        "language": "Unterrichtssprache",
        "study_form": "Studienform",
        "locations": "Standorte",
        "find_programs": "🎓 Studiengänge finden",
        "fill_all_fields": "Bitte fülle alle Felder aus.",
        "finding_programs": "💭 Finde passende Studiengänge...",
        "feedback": "💬 Dein Feedback",
        "feedback_input": "Was denkst du zu den Studiengang-Vorschlägen?",
        "filter_options": {
            "language": ["Primär Deutsch, teils Englisch", "Nur Englisch"],
            "study_form": ["Vollzeit", "Dual", "Berufsbegleitend"],
            "locations": ["Dortmund", "Frankfurt/Main", "München", "Hamburg", "Köln", "Stuttgart", "Berlin"]
        },
        "why_fits": "Warum passt dieser Studiengang zu dir?",
        "details": "📚 Details",
        "degree": "Abschluss",
        "fees": "Studiengebühren",
        "deadline": "Bewerbungsfrist",
        "semester_abroad": "Auslandssemester",
        "accreditation": "Akkreditierung",
        "more_info": "🔗 Mehr Infos",
        "remaining_rounds": "Verbleibende Feedback-Runden",
        "new_suggestions": "Neue Vorschläge basierend auf deinem Feedback",
        "why_fits_feedback": "Warum passt dieser Studiengang zu deinem Feedback?",
        "no_programs_found": "Keine passenden Studiengänge gefunden. Versuche es mit anderem Feedback.",
        "max_rounds": "Du hast das Maximum von 5 Feedback-Runden erreicht. Bitte starte eine neue Suche, wenn du weitere Vorschläge möchtest.",
        "enter_feedback": "Bitte gib dein Feedback ein, damit wir neue Vorschläge machen können.",
        "search_error": "Fehler bei der Suche",
        "tips": "💡 Tipp: Du möchtest mehr über die ISM erfahren? Besuche unsere [Infotage und -abende](https://ism.de/studieninteressierte/infoveranstaltungen/infotage-und-infoabende) oder nutze die Möglichkeit zum [Probehören](https://ism.de/studieninteressierte/infoveranstaltungen/probehoeren).",
        "duration": "Regelstudienzeit",
        "adjust_inputs": "💡 <span style='font-size: 1.2em; font-weight: bold;'>Möchtest du andere Studiengänge sehen?</span>\n\nDu kannst deine Eingaben oben anpassen und dann erneut auf 'Studiengänge finden' klicken, um neue Vorschläge zu erhalten.",
        "max_requests": "Vielen Dank für die Nutzung unseres Services! Du hast das Maximum von 5 Empfehlungen erreicht.",
        "recommendation": "Empfehlung",
        "of": "von"
    },
    "EN": {
        "title": "🎓 ISM Study Program Matching",
        "welcome": "Welcome to ISM International School of Management! 💙\nHere you'll find suitable study programs based on your interests and strengths - curated for you by our ISM AI, powered by [Karriere-Kapitän](https://karriere-kapitaen.com).",
        "interests_goals": "Your Interests and Goals",
        "privacy_notice": "ℹ️ **Important:** Please do not enter any personal data (e.g., name or contact details).",
        "study_goals": "What would you like to achieve in the future?",
        "interests": "What do you enjoy doing in your free time?",
        "strengths": "What are your greatest strengths? What have you been praised for?",
        "aspirations": "What do you want to achieve in your life? What are your dreams and goals?",
        "preferences": "Your Preferences",
        "language": "Language of Instruction",
        "study_form": "Study Form",
        "locations": "Locations",
        "find_programs": "🎓 Find Study Programs",
        "fill_all_fields": "Please fill in all fields.",
        "finding_programs": "💭 Finding suitable study programs...",
        "feedback": "💬 Your Feedback",
        "feedback_input": "What do you think about the study program suggestions?",
        "filter_options": {
            "language": ["Primarily German, partly English", "English only"],
            "study_form": ["Full-time", "Dual", "Part-time"],
            "locations": ["Dortmund", "Frankfurt/Main", "Munich", "Hamburg", "Cologne", "Stuttgart", "Berlin"]
        },
        "why_fits": "Why does this study program fit you?",
        "details": "📚 Details",
        "degree": "Degree",
        "fees": "Tuition Fees",
        "deadline": "Application Deadline",
        "semester_abroad": "Semester Abroad",
        "accreditation": "Accreditation",
        "more_info": "🔗 More Info",
        "remaining_rounds": "Remaining Feedback Rounds",
        "new_suggestions": "New suggestions based on your feedback",
        "why_fits_feedback": "Why does this study program fit your feedback?",
        "no_programs_found": "No matching study programs found. Try different feedback.",
        "max_rounds": "You have reached the maximum of 5 feedback rounds. Please start a new search if you want more suggestions.",
        "enter_feedback": "Please enter your feedback to get new suggestions.",
        "search_error": "Error during search",
        "tips": "💡 Tip: Want to learn more about ISM? Visit our [Information Days and Evenings](https://ism.de/studieninteressierte/infoveranstaltungen/infotage-und-infoabende) or try [Sitting in on Lectures](https://ism.de/studieninteressierte/infoveranstaltungen/probehoeren).",
        "filter_tip": "💡 You can select multiple options for all filters by clicking on them.",
        "duration": "Duration",
        "adjust_inputs": "💡 <span style='font-size: 1.2em; font-weight: bold;'>Want to see different study programs?</span>\n\nYou can adjust your inputs above and click 'Find Study Programs' again to get new suggestions.",
        "max_requests": "Thank you for using our service! You have reached the maximum of 5 recommendations.",
        "recommendation": "Recommendation",
        "of": "of"
    }
}

# Add mapping dictionaries for filter options
FILTER_MAPPINGS = {
    "EN": {
        "language": {
            "Primarily German, partly English": "Primär Deutsch, teils Englisch",
            "English only": "Nur Englisch"
        },
        "study_form": {
            "Full-time": "Vollzeit",
            "Dual": "Dual",
            "Part-time": "Berufsbegleitend"
        },
        "locations": {
            "Dortmund": "Dortmund",
            "Frankfurt/Main": "Frankfurt/Main",
            "Munich": "München",
            "Hamburg": "Hamburg",
            "Cologne": "Köln",
            "Stuttgart": "Stuttgart",
            "Berlin": "Berlin"
        }
    }
}

# Initialize language in session state
if 'language' not in st.session_state:
    st.session_state.language = "DE"

# Initialize session state for results
if 'initial_results' not in st.session_state:
    st.session_state.initial_results = None
if 'feedback_results' not in st.session_state:
    st.session_state.feedback_results = None
if 'feedback_count' not in st.session_state:
    st.session_state.feedback_count = 0
if 'show_initial_results' not in st.session_state:
    st.session_state.show_initial_results = True
if 'show_feedback_results' not in st.session_state:
    st.session_state.show_feedback_results = False
if 'request_count' not in st.session_state:
    st.session_state.request_count = 0

# Initialize session state for initial inputs and results
if 'initial_studienziele' not in st.session_state:
    st.session_state.initial_studienziele = None
if 'initial_interessen' not in st.session_state:
    st.session_state.initial_interessen = None
if 'initial_staerken' not in st.session_state:
    st.session_state.initial_staerken = None
if 'initial_suggestions' not in st.session_state:
    st.session_state.initial_suggestions = []

# --- RAG Setup ---
@st.cache_resource
def setup_vectorstore():
    # Use an absolute path for the vectorstore directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    vectorstore_dir = os.path.join(script_dir, "vectorstore")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = Chroma(
        persist_directory=vectorstore_dir,
        embedding_function=embeddings
    )
    return vectorstore

vectorstore = setup_vectorstore()

# Initialize LLM for explanations
llm = ChatOpenAI(
    model_name="gpt-4.1-mini",
    temperature=0.7
)

# --- Custom CSS ---
st.markdown("""
    <style>
    .stApp header {
        background-color: #003366;
    }
    .stMultiSelect [data-baseweb=select] span {
        background-color: #FFA500 !important;
        color: white !important;
    }
    .powered-by {
        text-align: center;
        font-size: 0.8em;
        color: #666;
        margin-top: 2rem;
        padding: 1rem 0;
        border-top: 1px solid #eee;
    }
    .program-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #dee2e6;
    }
    .program-title {
        color: #003366;
        font-size: 1.5em;
        margin-bottom: 15px;
    }
    .program-details {
        margin-top: 15px;
    }
    .program-details p {
        margin: 5px 0;
    }
    /* Button Styling */
    .stButton > button {
        background-color: transparent !important;
        border: 2px solid #666666 !important;
        color: #666666 !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        border-color: #FFA500 !important;
        color: #FFA500 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- UI Components ---
col1, col2 = st.columns([0.8, 0.2])
with col1:
    if st.button("🇩🇪 DE" if st.session_state.language == "EN" else "🇬🇧 ENG"):
        st.session_state.language = "EN" if st.session_state.language == "DE" else "DE"
        st.rerun()
with col2:
    # Get the absolute path to the logo
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(script_dir, "logos", "ism.png")
    st.image(logo_path, use_container_width=True)

current_lang = LANGUAGES[st.session_state.language]
st.title(current_lang["title"])
st.markdown(current_lang["welcome"])

# --- Main Questions ---
st.subheader(current_lang["interests_goals"])
st.markdown(current_lang["privacy_notice"])

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

# --- Filter Options ---
st.subheader(current_lang["preferences"])
st.markdown(current_lang["filter_tip"])

unterrichtssprache = st.multiselect(
    current_lang["language"],
    options=current_lang["filter_options"]["language"]
)

studienform = st.multiselect(
    current_lang["study_form"],
    options=current_lang["filter_options"]["study_form"]
)

standorte = st.multiselect(
    current_lang["locations"],
    options=current_lang["filter_options"]["locations"]
)

# Convert selected options back to German for metadata filtering
if st.session_state.language == "EN":
    unterrichtssprache = [FILTER_MAPPINGS["EN"]["language"][lang] for lang in unterrichtssprache]
    studienform = [FILTER_MAPPINGS["EN"]["study_form"][form] for form in studienform]
    standorte = [FILTER_MAPPINGS["EN"]["locations"][loc] for loc in standorte]

# --- Study Program Matching ---
if st.button(current_lang["find_programs"]):
    if st.session_state.request_count >= 5:
        st.warning(current_lang["max_requests"])
    else:
        with st.spinner(current_lang["finding_programs"]):
            try:
                # Increment request counter
                st.session_state.request_count += 1
                
                # Build the query from user input, using empty strings if fields are blank
                filled_fields = []
                if studienziele:
                    filled_fields.append(f"Studienziele: {studienziele}")
                if interessen:
                    filled_fields.append(f"Interessen: {interessen}")
                if staerken:
                    filled_fields.append(f"Stärken: {staerken}")

                # If no fields are filled, use a more general query
                if not filled_fields:
                    query = "Finde drei verschiedene, interessante Studiengänge. Berücksichtige dabei verschiedene Fachrichtungen und Abschlüsse."
                else:
                    # Join fields with newlines without using f-string
                    fields_text = "\n".join(filled_fields)
                    query = f"Basierend auf folgenden Informationen:\n{fields_text}\n\nFinde drei verschiedene, passende Studiengänge. Achte darauf, dass die Studiengänge unterschiedliche Schwerpunkte und Abschlüsse haben."

                # Create filter conditions for metadata
                filter_conditions = []
                
                # Handle language filtering - if none selected, don't filter
                if unterrichtssprache:
                    if len(unterrichtssprache) == 1:
                        filter_conditions.append({"unterrichtssprache": {"$eq": unterrichtssprache[0]}})
                    else:
                        filter_conditions.append({"unterrichtssprache": {"$in": unterrichtssprache}})
                
                # Handle study form filtering - if none selected, don't filter
                if studienform:
                    if len(studienform) == 1:
                        filter_conditions.append({"studienform": {"$eq": studienform[0]}})
                    else:
                        filter_conditions.append({"studienform": {"$in": studienform}})
                
                # Handle location filtering using boolean columns - if none selected, don't filter
                if standorte:
                    location_conditions = []
                    location_map = {
                        "Dortmund": "loc_dor",
                        "Frankfurt/Main": "loc_ffm",
                        "München": "loc_muc",
                        "Hamburg": "loc_hh",
                        "Köln": "loc_cgn",
                        "Stuttgart": "loc_stu",
                        "Berlin": "loc_bln"
                    }
                    for location in standorte:
                        if location in location_map:
                            location_conditions.append({location_map[location]: {"$eq": True}})
                    if location_conditions:
                        if len(location_conditions) == 1:
                            filter_conditions.append(location_conditions[0])
                        else:
                            filter_conditions.append({"$or": location_conditions})

                # Create the final where clause based on number of conditions
                if len(filter_conditions) == 0:
                    where = None
                elif len(filter_conditions) == 1:
                    where = filter_conditions[0]
                else:
                    where = {"$and": filter_conditions}

                # Retrieve more results than needed to ensure diversity
                all_results = vectorstore.similarity_search(
                    query=query,
                    k=10,  # Get more results than needed
                    filter=where
                )

                # Ensure diverse results by selecting programs with different degrees and titles
                selected_results = []
                seen_degrees = set()
                seen_titles = set()
                
                for result in all_results:
                    degree = result.metadata['abschluss']
                    title = result.metadata['titel']
                    if degree not in seen_degrees and title not in seen_titles:
                        selected_results.append(result)
                        seen_degrees.add(degree)
                        seen_titles.add(title)
                        if len(selected_results) == 3:
                            break

                # If we don't have enough diverse results, add remaining ones that are different
                while len(selected_results) < 3 and all_results:
                    result = all_results.pop(0)
                    if result.metadata['titel'] not in seen_titles:
                        selected_results.append(result)
                        seen_titles.add(result.metadata['titel'])

                results = selected_results[:3]  # Ensure we only return 3 results

                # Store initial inputs and results in session state
                st.session_state.initial_studienziele = studienziele
                st.session_state.initial_interessen = interessen
                st.session_state.initial_staerken = staerken
                st.session_state.initial_suggestions = []

                # Store initial results in session state
                st.session_state.initial_results = results
                st.session_state.show_initial_results = True
                st.session_state.show_feedback_results = False

                # Display initial results
                if st.session_state.show_initial_results:
                    for i, doc in enumerate(results, 1):
                        meta = doc.metadata
                        
                        # Generate explanation using LLM
                        explanation_prompt = f"""
                        Basierend auf den folgenden Informationen des Nutzers:
                        Studienziele: {studienziele}
                        Interessen: {interessen}
                        Stärken: {staerken}
                        
                        Und diesem Studiengang:
                        Beschreibung: {doc.page_content}
                        
                        Erkläre in zwei kurzen, persönlichen Sätzen, warum dieser Studiengang gut zu den angegebenen Zielen, Interessen und Stärken des Nutzers passen könnte. 
                        Verwende dabei die Formulierung "Du" und beziehe dich direkt auf die Eingaben des Nutzers.
                        {'Provide the explanation in English.' if st.session_state.language == "EN" else ''}
                        """
                        
                        explanation = llm.invoke(explanation_prompt).content
                        
                        # Display the program card
                        st.markdown(f"""
                        <div class="program-card">
                            <div class="program-title">🎓 {meta['titel']}</div>
                            <div class="program-details">
                                <p><strong>{current_lang['why_fits']}</strong><br>{explanation}</p>
                                <p><strong>{current_lang['details']}</strong></p>
                                <ul style="list-style-type: none; padding-left: 0;">
                                    <li>• {current_lang['degree']}: {meta['abschluss']}</li>
                                    <li>• {current_lang['study_form']}: {meta['studienform']}</li>
                                    <li>• {current_lang['locations']}: {meta['standorte']}</li>
                                    <li>• {current_lang['duration']}: {meta['regelstudienzeit']}</li>
                                    <li>• {current_lang['fees']}: {meta['studiengebuehren']}</li>
                                    <li>• {current_lang['language']}: {meta['unterrichtssprache']}</li>
                                    <li>• {current_lang['deadline']}: {meta['bewerbungsfrist']}</li>
                                    <li>• {current_lang['semester_abroad']}: {meta['auslandssemester']}</li>
                                    <li>• {current_lang['accreditation']}: {meta['akkreditierung']}</li>
                                </ul>
                                <p><strong>{current_lang['more_info']}</strong> <a href="{meta['url']}" target="_blank">{meta['url']}</a></p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                # Add instructions for adjusting inputs
                st.markdown(f"""
                <div style="margin-top: 20px;">
                    {current_lang['adjust_inputs']}
                </div>
                """, unsafe_allow_html=True)

                # Add request counter display
                st.markdown(f"""
                <div style="text-align: right; color: #666; font-size: 0.8em; margin-top: 10px;">
                    {current_lang['recommendation']} {st.session_state.request_count} {current_lang['of']} 5
                </div>
                """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"{current_lang['search_error']}: {str(e)}")

# --- Powered by text ---
st.markdown('<div class="powered-by">Powered by <a href="https://karriere-kapitaen.com" target="_blank">Karriere-Kapitän</a></div>', unsafe_allow_html=True) 