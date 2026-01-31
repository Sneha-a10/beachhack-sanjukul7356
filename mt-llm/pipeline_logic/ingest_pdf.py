import os
import json
import uuid
import pypdf
from typing import List, Dict
from sentence_transformers import SentenceTransformer

# Paths
PDF_PATH = os.path.join("knowledge_base", "Predictive Maintenance Knowledge Base.pdf")
OUTPUT_PATH = os.path.join("knowledge_base", "knowledgebase.json")
MODEL_NAME = "all-MiniLM-L6-v2"

def load_pdf_text(filepath: str) -> str:
    """Extracts full text from a PDF file."""
    if not os.path.exists(filepath):
        print(f"Error: PDF not found at {filepath}")
        return ""
    
    try:
        reader = pypdf.PdfReader(filepath)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Splits text into chunks with overlap."""
    if not text:
        return []
    
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += (chunk_size - overlap)
    
    return chunks

def ingest_data():
    print(f"Loading PDF from {PDF_PATH}...")
    full_text = load_pdf_text(PDF_PATH)
    if not full_text:
        return

    print("Chunking text...")
    chunks = chunk_text(full_text)
    print(f"Created {len(chunks)} chunks.")

    print(f"Loading embedding model {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)
    
    print("Generating embeddings...")
    embeddings = model.encode(chunks)
    
    knowledge_base = []
    for i, (text_chunk, embedding) in enumerate(zip(chunks, embeddings)):
        doc_id = str(uuid.uuid4())
        record = {
            "id": doc_id,
            "text": text_chunk.strip(),
            "embedding": embedding.tolist(),
            "metadata": {
                "source": os.path.basename(PDF_PATH),
                "chunk_index": i
            }
        }
        knowledge_base.append(record)
    
    # Load existing KB to preserve User keys
    existing_kb = []
    if os.path.exists(OUTPUT_PATH):
        try:
            with open(OUTPUT_PATH, 'r') as f:
                existing_kb = json.load(f)
        except Exception as e:
            print(f"Warning: Could not read existing KB: {e}")
            existing_kb = []

    # Filter out old PDF chunks (to update them) but keep User chunks
    preserved_chunks = [
        chunk for chunk in existing_kb
        if chunk.get("metadata", {}).get("section") == "User_Verified"
    ]
    print(f"Preserving {len(preserved_chunks)} user-verified chunks.")
    
    # Combine
    final_kb = preserved_chunks + knowledge_base
    
    print(f"Saving {len(final_kb)} records to {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(final_kb, f, indent=4)
    
    print("Ingestion complete.")

if __name__ == "__main__":
    ingest_data()
