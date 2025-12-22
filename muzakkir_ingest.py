import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()

# ================= CONFIGURATION =================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# The file we created in the previous step
INPUT_FILE = "sozler_data_md.json"
# =================================================

# Initialize connection to OpenAI and Supabase
openai_client = OpenAI(api_key=OPENAI_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_embedding(text):
    """
    Sends text to OpenAI and gets back a list of numbers (vector).
    We use 'text-embedding-3-small' because it's cheap and fast.
    """
    # Remove newlines to make it easier for AI to process
    text = text.replace("\n", " ")
    return openai_client.embeddings.create(input=[text], model="text-embedding-3-small").data[0].embedding

def ingest_data():
    print(f"🚀 Awakening Muzakir... Reading {INPUT_FILE}...")
    
    # Check if file exists
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Error: Could not find {INPUT_FILE}. Did you run the chunker script?")
        return

    # Load the JSON data
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    
    print(f"📚 Found {len(chunks)} paragraphs to teach Muzakir.")

    # Loop through every paragraph
    for i, chunk in enumerate(chunks):
        try:
            print(f"Processing chunk {i+1}/{len(chunks)}...", end="\r")
            
            # 1. Turn text into numbers (Vector)
            vector = get_embedding(chunk["text"])
            
            # 2. Prepare the data package
            data = {
                "content": chunk["text"],
                "metadata": {
                    "book": chunk["book"],
                    "chapter": chunk["chapter"],
                    "format": chunk.get("format", "text")
                },
                "embedding": vector
            }
            
            # 3. Send to Supabase
            supabase.table("documents").insert(data).execute()
                
        except Exception as e:
            print(f"\n❌ Error on chunk {i}: {e}")

    print("\n🎉 Ingestion Complete! Muzakir has memorized 'The Words' (Sözler).")

if __name__ == "__main__":
    # You need to install these first: pip install openai supabase
    ingest_data()