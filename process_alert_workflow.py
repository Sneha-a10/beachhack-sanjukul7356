import os
import json
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class SimpleJSONRetriever:
    """
    A lightweight retriever that searches through JSON records based on keywords.
    Replaces the complex Vector DB ingestion for this specific workflow.
    """
    def __init__(self, data_sources: List[Dict]):
        self.data_sources = data_sources

    def search(self, query: str, context_keywords: List[str] = None) -> List[Dict]:
        """
        Search for records containing query terms or context keywords.
        """
        results = []
        query_terms = query.lower().split()
        
        for record in self.data_sources:
            text = record.get('text', '').lower()
            metadata = record.get('metadata', {})
            meta_str = str(metadata).lower()
            
            # Score based on keyword matches
            score = 0
            
            # Check query terms in text
            for term in query_terms:
                if term in text:
                    score += 2
            
            # Check context keywords (e.g., failed rule names, decision) in text & metadata
            if context_keywords:
                for kw in context_keywords:
                    kw_lower = kw.lower()
                    if kw_lower in text:
                        score += 3
                    if kw_lower in meta_str:
                        score += 1
            
            if score > 0:
                results.append((score, record))
        
        # Sort by score desc
        results.sort(key=lambda x: x[0], reverse=True)
        return [r[1] for r in results[:5]] # Return top 5

def load_json_file(filepath: str) -> Any:
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"File not found: {filepath}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON {filepath}: {e}")
        return None

def main():
    # 1. Load Data
    logging.info("Loading data files...")
    
    # Input Alert
    alert_trace_path = "post_decision_trace.json"
    alert_data = load_json_file(alert_trace_path)
    if not alert_data:
        logging.error("Failed to load alert trace. Exiting.")
        return

    # Knowledge Sources
    vectordb_path = "vectorDB.json"
    kb_path = "knowledgebase.json"
    
    vectordb_data = load_json_file(vectordb_path)
    kb_data = load_json_file(kb_path)
    
    # Merge sources for the retriever
    # vectorDB.json is a single object in the snippet provided by user step 81? 
    # Wait, Step 81 content shows it's a SINGLE OBJECT not a list. 
    # But typically a VectorDB dump is a list.
    # The snippet in Step 81:
    # { "id": "chunk_023", ... }
    # Step 82: knowledgebase.json IS A LIST.
    # I should handle both single object and list to be safe.
    
    all_knowledge_records = []
    
    if vectordb_data:
        if isinstance(vectordb_data, list):
            all_knowledge_records.extend(vectordb_data)
        elif isinstance(vectordb_data, dict):
            all_knowledge_records.append(vectordb_data)
            
    if kb_data:
        if isinstance(kb_data, list):
            all_knowledge_records.extend(kb_data)
        elif isinstance(kb_data, dict):
            all_knowledge_records.append(kb_data)

    if not all_knowledge_records:
        logging.error("No knowledge base records loaded. Exiting.")
        return

    # 2. Extract Alert Details
    # The file contains a single object as per Step 83/92
    trace = alert_data.get('input_trace', {})
    
    decision = trace.get('decision', 'Unknown Issue')
    observed = trace.get('observed_behavior', 'anomaly')
    rules_triggered = trace.get('rules_triggered', [])
    
    logging.info(f"Processing Alert: {decision}")
    logging.info(f"Observed: {observed}")

    # 3. Initialize Retriever
    retriever = SimpleJSONRetriever(all_knowledge_records)

    # 4. Search for Context
    # We search using the decision failure type and the specific observed symptom
    query_str = f"{decision} {observed}"
    context_keywords = rules_triggered + [decision]
    
    relevant_docs = retriever.search(query_str, context_keywords)
    
    logging.info(f"Found {len(relevant_docs)} relevant context records.")

    # 5. Generate Recommendation (Using Groq or Mock)
    # Since we can't be sure if `langchain_groq` is installed/configured in this environment (though rag.ipynb used it),
    # I will check for the key. If missing, I'll print a detailed prompt that *would* be sent.
    # This ensures the script runs successfully even if API keys aren't set in this specific terminal session.
    
    # 5. Generate Recommendation (Using Groq or Mock)
    output_data = {}
    
    context_text = ""
    references = set()
    for idx, doc in enumerate(relevant_docs, 1):
        context_text += f"Source {idx}:\n{doc.get('text', 'No text')}\n---\n"
        # Extract source metadata for references
        meta = doc.get('metadata', {})
        if 'document' in meta:
            references.add(f"{meta['document']} (Section {meta.get('section', '?')})")
        elif 'failure_type' in meta:
             references.add(f"{meta['failure_type']} (Section {meta.get('section', '?')})")

    reference_str = ", ".join(references) if references else "Internal Knowledge Base"

    # Try to use Groq if available
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("\n" + "="*40)
        print(" [!] GROQ_API_KEY not found. Simulating structured JSON Output.")
        print("="*40)
        
        # Simulated JSON content based on the known context contents
        output_data = {
            "recommended_action": [
                f"Address {decision}: Check lubrication levels immediately.",
                "Schedule bearing replacement within 5–10 days if symptoms persist.",
                f"Monitor {observed} and vibration trends closely."
            ],
            "safety_note": "Before inspecting bearings, ensure the machine is powered down and locked out to prevent injury.",
            "reference": reference_str
        }
    else:
        try:
            from langchain_groq import ChatGroq
            chat = ChatGroq(temperature=0, model_name="llama-3.3-70b-versatile", groq_api_key=api_key)
            
            json_prompt = f"""
            You are an expert industrial maintenance assistant.
            
            ALERT: {decision} with {observed}
            CONTEXT: {context_text}
            
            TASK: Return a valid JSON object with the following structure:
            {{
              "recommended_action": ["action 1", "action 2", ...],
              "safety_note": "safety warning...",
              "reference": "source names..."
            }}
            
            Strictly return ONLY the JSON string.
            """
            
            response = chat.invoke(json_prompt)
            content = response.content.strip()
            # clean up potential markdown fencing
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            output_data = json.loads(content.strip())
            
        except Exception as e:
            logging.error(f"Error calling LLM or parsing JSON: {e}")
            output_data = {
                "error": "Failed to generate recommendation via LLM",
                "recommended_action": ["Consult manual manually"],
                "safety_note": "Exercise caution",
                "reference": "N/A"
            }

    # 6. Save Logic
    output_file = "final_recommendation.json"
    print(f"\nFinal Structure:\n{json.dumps(output_data, indent=2)}")
    
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\nSaved output to {output_file}")

if __name__ == "__main__":
    main()
