import pandas as pd
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import os
import torch

# This function prepares a vector store from the study programs CSV file
# It loads the data, creates text and metadata for each entry, generates embeddings, and saves everything in a persistent vector store

def prepare_vectorstore():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Script directory: {script_dir}")
    
    # Build the absolute path to the CSV file containing the study programs
    csv_path = os.path.join(script_dir, 'data', 'studiengaenge.csv')
    print(f"Looking for CSV file at: {csv_path}")
    
    # Check if the CSV file exists, otherwise raise an error
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found at: {csv_path}")
    
    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_path)
    print(f"Successfully loaded CSV file with {len(df)} rows")
    
    # Prepare lists to hold the text chunks and their associated metadata
    texts = []
    metadatas = []
    
    # Get all location columns
    location_columns = [col for col in df.columns if col.startswith('loc_')]
    
    # Iterate over each row (study program) in the DataFrame
    for _, row in df.iterrows():
        # Create a text chunk for the study program (used for embedding)
        text = f"""
        Studiengang: {row['Titel des Studiengangs']}
        Kurzbeschreibung: {row['Kurzbeschreibung']}
        """
        texts.append(text)
        
        # Get active locations from binary columns
        active_locations = []
        for loc_col in location_columns:
            if row[loc_col]:
                # Convert column name to city name (e.g., loc_dor -> Dortmund)
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
        
        # Join locations into a comma-separated string
        locations_str = ", ".join(active_locations)
        
        # Collect relevant metadata for each study program
        metadata = {
            'titel': row['Titel des Studiengangs'],
            'abschluss': row['Abschluss'],
            'studienform': row['Studienform'],
            'standorte': locations_str,  # Keep the string for display
            'unterrichtssprache': row['Unterrichtssprache (kurz)'],
            'url': row['URL'],
            'studiengebuehren': row['Studiengebühren'],
            'regelstudienzeit': row['Regel­studien­zeit'],
            'bewerbungsfrist': row['Bewerbungsfrist'],
            'auslandssemester': row['Auslandssemester'],
            'akkreditierung': row['Akkreditierung'],
            # Add location boolean columns
            'loc_dor': row['loc_dor'],
            'loc_ffm': row['loc_ffm'],
            'loc_muc': row['loc_muc'],
            'loc_hh': row['loc_hh'],
            'loc_cgn': row['loc_cgn'],
            'loc_stu': row['loc_stu'],
            'loc_bln': row['loc_bln']
        }
        metadatas.append(metadata)
    
    # Choose the device for embedding model: GPU (cuda) if available, otherwise CPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    # Initialize the HuggingFace sentence transformer embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': device}
    )
    
    # Set up the directory where the vector store will be saved
    vectorstore_dir = os.path.join(script_dir, "vectorstore")
    os.makedirs(vectorstore_dir, exist_ok=True)
    
    # Create the Chroma vector store from the texts and metadata, and persist it to disk
    vectorstore = Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas,
        persist_directory=vectorstore_dir
    )
    
    # Persist the vectorstore to disk
    vectorstore.persist()
    print("Vectorstore prepared and persisted successfully!")

# Run the function if this script is executed directly
if __name__ == "__main__":
    prepare_vectorstore() 