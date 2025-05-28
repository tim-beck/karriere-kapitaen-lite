"""
Dieses Skript bereitet die Daten für den ISM-Studienfinder vor.
Es lädt die Studiengangsdaten aus einer CSV-Datei, erstellt Embeddings und speichert sie in einer Chroma-Vektordatenbank.
"""

import pandas as pd
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import os
import torch

def prepare_vectorstore():
    """
    Hauptfunktion zum Erstellen der Vektordatenbank.
    
    Ablauf:
    1. Lädt Studiengangsdaten aus CSV
    2. Erstellt Text-Repräsentationen und Metadaten
    3. Generiert Embeddings mit einem HuggingFace-Modell
    4. Speichert alles in einer persistenten Chroma-Datenbank
    """
    # Bestimme das Verzeichnis des Skripts für relative Pfade
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Script directory: {script_dir}")
    
    # Pfad zur CSV-Datei mit den Studiengängen
    csv_path = os.path.join(script_dir, 'data', 'studiengaenge.csv')
    print(f"Looking for CSV file at: {csv_path}")
    
    # Überprüfe, ob die CSV-Datei existiert
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found at: {csv_path}")
    
    # Lade die CSV-Datei in ein pandas DataFrame
    df = pd.read_csv(csv_path)
    print(f"Successfully loaded CSV file with {len(df)} rows")
    
    # Listen für Text und Metadaten vorbereiten
    texts = []  # Enthält die Text-Repräsentationen für die Embeddings
    metadatas = []  # Enthält die Metadaten für jeden Studiengang
    
    # Finde alle Standort-Spalten (beginnen mit 'loc_')
    location_columns = [col for col in df.columns if col.startswith('loc_')]
    
    # Verarbeite jeden Studiengang
    for _, row in df.iterrows():
        # Erstelle Text-Repräsentation für Embeddings
        text = f"""
        Studiengang: {row['Titel des Studiengangs']}
        Kurzbeschreibung: {row['Kurzbeschreibung']}
        """
        texts.append(text)
        
        # Extrahiere aktive Standorte aus den binären Spalten
        active_locations = []
        for loc_col in location_columns:
            if row[loc_col]:
                # Mappe Spaltennamen auf Städtenamen
                city_map = {
                    'loc_dor': 'Dortmund',
                    'loc_ffm': 'Frankfurt/Main',
                    'loc_muc': 'München',
                    'loc_hh': 'Hamburg',
                    'loc_cgn': 'Köln',
                    'loc_stu': 'Stuttgart',
                    'loc_bln': 'Berlin'
                }
                active_locations.append(city_map[loc_col])
        
        # Füge Standorte als kommagetrennte Liste hinzu
        locations_str = ", ".join(active_locations)
        
        # Sammle alle relevanten Metadaten für den Studiengang
        metadata = {
            'titel': row['Titel des Studiengangs'],
            'abschluss': row['Abschluss'],
            'studienform': row['Studienform'],
            'standorte': locations_str,  # String für die Anzeige
            'unterrichtssprache': row['Unterrichtssprache (kurz)'],
            'url': row['URL'],
            'studiengebuehren': row['Studiengebühren'],
            'regelstudienzeit': row['Regel­studien­zeit'],
            'bewerbungsfrist': row['Bewerbungsfrist'],
            'auslandssemester': row['Auslandssemester'],
            'akkreditierung': row['Akkreditierung'],
            # Füge Standort-Boolean-Spalten hinzu
            'loc_dor': row['loc_dor'],
            'loc_ffm': row['loc_ffm'],
            'loc_muc': row['loc_muc'],
            'loc_hh': row['loc_hh'],
            'loc_cgn': row['loc_cgn'],
            'loc_stu': row['loc_stu'],
            'loc_bln': row['loc_bln']
        }
        metadatas.append(metadata)
    
    # Wähle das Gerät für das Embedding-Modell: GPU wenn verfügbar, sonst CPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Initialisiere das HuggingFace Embedding-Modell
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': device}
    )
    
    # Erstelle das Verzeichnis für die Vektordatenbank
    vectorstore_dir = os.path.join(script_dir, "vectorstore")
    os.makedirs(vectorstore_dir, exist_ok=True)
    
    # Erstelle die Chroma-Vektordatenbank und speichere sie
    vectorstore = Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas,
        persist_directory=vectorstore_dir
    )
    
    # Speichere die Vektordatenbank dauerhaft
    vectorstore.persist()
    print("Vectorstore prepared and persisted successfully!")

# Führe die Funktion aus, wenn das Skript direkt ausgeführt wird
if __name__ == "__main__":
    prepare_vectorstore() 