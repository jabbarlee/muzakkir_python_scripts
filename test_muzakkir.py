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

def ask_muzakir(question):
    print(f"\n❓ Question: {question}")
    print("SEARCHING...")

    # 1. Turn the question into a vector
    # We must use the exact same model as we did for the books
    query_vector = openai_client.embeddings.create(
        input=[question], 
        model="text-embedding-3-small"
    ).data[0].embedding

    # 2. Search Supabase for the closest matching paragraph
    # We use the 'match_documents' function we created in SQL
    response = supabase.rpc("match_documents", {
        "query_embedding": query_vector,
        "match_threshold": 0.5, # How strict? (0.5 is loose, 0.8 is strict)
        "match_count": 3        # Return top 3 results
    }).execute()

    # 3. Print Results
    if not response.data:
        print("❌ No matching text found. Try a different question.")
        return

    print(f"✅ Found {len(response.data)} relevant matches!\n")
    
    for i, match in enumerate(response.data):
        print(f"--- Match {i+1} (Similarity: {match['similarity']:.2f}) ---")
        print(f"📖 Chapter: {match['metadata']['chapter']}")
        print(f"📄 Text: {match['content'][:200]}...") # Show first 200 chars
        print("-" * 50)

# Run the test
if __name__ == "__main__":
    # You can change this question to anything
    ask_muzakir("Why is Bismillah important?")