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
# =================================================

openai_client = OpenAI(api_key=OPENAI_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def diagnose():
    print("🕵️‍♂️ Starting Diagnostics...")

    # TEST 1: Check if data exists
    try:
        count_response = supabase.table("documents").select("id", count="exact").execute()
        count = count_response.count
        print(f"📊 Total Paragraphs in Database: {count}")
        
        if count == 0:
            print("❌ CRITICAL: Database is empty! Ingestion failed silently.")
            return
    except Exception as e:
        print(f"⚠️ Could not check count: {e}")

    # TEST 2: Search with NO threshold (Accept anything)
    question = "Bismillah" # Simple keyword
    print(f"\n❓ Testing Search for: '{question}'")
    
    query_vector = openai_client.embeddings.create(
        input=[question], 
        model="text-embedding-3-small"
    ).data[0].embedding

    # Threshold 0.0 means "Show me everything, even if it's a bad match"
    response = supabase.rpc("match_documents", {
        "query_embedding": query_vector,
        "match_threshold": 0.0, 
        "match_count": 1
    }).execute()

    if response.data:
        match = response.data[0]
        print(f"✅ FOUND A MATCH!")
        print(f"   Similarity Score: {match['similarity']}")
        print(f"   Text Snippet: {match['content'][:100000]}...")
    else:
        print("❌ Search returned nothing. This might be an embedding dimension mismatch.")

if __name__ == "__main__":
    diagnose()