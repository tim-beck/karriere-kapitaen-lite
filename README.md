# Mini-Coaching App

A Streamlit-based coaching application that helps users explore career paths, study options, and gap year planning.

## Setup

1. Create a virtual environment:
```bash
python -m venv .venv
```

2. Activate the virtual environment:
- On macOS/Linux:
```bash
source .venv/bin/activate
```
- On Windows:
```bash
.venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Running the App

1. Make sure your virtual environment is activated

2. Run the Streamlit app:
```bash
streamlit run lite/app.py
```

The app will open in your default web browser at `http://localhost:8501`

## Features

- Bilingual support (German/English)
- Career path exploration
- Study and training options
- Gap year planning
- Interactive coaching chat 