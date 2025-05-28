# ISM Studienfinder

A Streamlit app that helps students find suitable study programs at ISM using AI-powered recommendations.

## Quick Start

1. **Setup Environment**:
   ```bash
   cd ism
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   - Create `.env` file in `rag_app` folder
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_key_here
     ```

3. **Run the App**:
   ```bash
   cd rag_app
   streamlit run app.py
   ```

The app will be available at http://localhost:8501

## Features
- AI-powered study program recommendations
- Multi-language support (DE/EN)
- Location and study form filters 