import os
import json
import numpy as np
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer

# Paths
INPUT_PATH = os.path.join("knowledge_base", "maintenance_chunks.json")
OUTPUT_PATH = os.path.join("knowledge_base", "knowledgebase.json")
MODEL_NAME = "all-MiniLM-L6-v2"

def load_json_file(filepath: str) -> Any:
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return []

def ingest_data():
    print(f"Loading knowledge from {INPUT_PATH}...")
    chunks = load_json_file(INPUT_PATH)
    if not chunks:
        return

    print(f"Loaded {len(chunks)} chunks.")

    print(f"Loading embedding model {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)
    
    print("Generating embeddings...")
    texts = [chunk.get("text", "") for chunk in chunks]
    embeddings = model.encode(texts)
    
    new_knowledge_base = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        record = {
            "id": chunk.get("chunk_id"),
            "text": chunk.get("text", "").strip(),
            "embedding": embedding.tolist(),
            "metadata": {
                "source": "maintenance_chunks.json",
                "chunk_type": chunk.get("chunk_type"),
                "asset_type": chunk.get("asset_type"),
                "rule_id": chunk.get("rule_id"),
                "urgency": chunk.get("urgency")
            }
        }
        new_knowledge_base.append(record)
    
    # Load existing KB to preserve User keys
    existing_kb = []
    if os.path.exists(OUTPUT_PATH):
        try:
            with open(OUTPUT_PATH, 'r') as f:
                existing_kb = json.load(f)
        except Exception as e:
            print(f"Warning: Could not read existing KB: {e}")
            existing_kb = []

    # Filter out old chunks (to update them) but keep User chunks
    # We assume chunks from this file are "authoritative" for their IDs, 
    # but we strictly want to keep "User_Verified" chunks.
    preserved_chunks = [
        chunk for chunk in existing_kb
        if chunk.get("metadata", {}).get("section") == "User_Verified"
    ]
    print(f"Preserving {len(preserved_chunks)} user-verified chunks.")
    
    # Combine
    final_kb = preserved_chunks + new_knowledge_base
    
    print(f"Saving {len(final_kb)} records to {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(final_kb, f, indent=4)
    
    print("Ingestion complete.")

if __name__ == "__main__":
    ingest_data()
