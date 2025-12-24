import os
import re
from openai import OpenAI
from dotenv import load_dotenv
from supabase import create_client, Client

# ================= CONFIGURATION =================
# 1. Keys (Same as before)

# Load environment variables from .env file
load_dotenv()

# ================= CONFIGURATION =================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 2. Folder Path
# Make sure this matches your folder structure exactly
TARGET_FOLDER = "obsidian-markdown/01 Sözler"

# 3. Missing Files Keywords
# We will only process files that contain these words in their name
TARGET_KEYWORDS = ["33", "Lemaat", "Konferans", "Fihrist"]
# =================================================

openai_client = OpenAI(api_key=OPENAI_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def clean_markdown(text):
    """Same cleaning logic as before to keep data consistent."""
    text = re.sub(r'\[\[(.*?)\]\]', r'\1', text) # Remove links
    text = text.replace("**", "").replace("*", "") # Remove bold/italic
    text = text.replace("### ", "").replace("## ", "").replace("# ", "") # Remove headers
    return text

def get_embedding(text):
    text = text.replace("\n", " ")
    return openai_client.embeddings.create(input=[text], model="text-embedding-3-small").data[0].embedding

def process_missing_files():
    print(f"🕵️‍♂️ Scanning {TARGET_FOLDER} for missing chapters...")
    
    if not os.path.exists(TARGET_FOLDER):
        print(f"❌ Error: Folder not found at {TARGET_FOLDER}")
        return

    # Find the specific files
    files_to_process = []
    for filename in os.listdir(TARGET_FOLDER):
        if filename.endswith(".md"):
            # Check if filename contains any of our target keywords
            if any(keyword in filename for keyword in TARGET_KEYWORDS):
                files_to_process.append(filename)

    if not files_to_process:
        print("❌ No matching files found. Check your keywords or folder path.")
        return

    print(f"📝 Found {len(files_to_process)} missing files to process: {files_to_process}")

    total_chunks_added = 0

    for filename in files_to_process:
        file_path = os.path.join(TARGET_FOLDER, filename)
        chapter_name = filename.replace(".md", "").replace("_", " ")
        print(f"\n🚀 Processing: {chapter_name}...")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_text = f.read()
            
            clean_text = clean_markdown(raw_text)
            paragraphs = clean_text.split("\n\n")
            
            current_chunk = ""
            chunks = []
            
            # Chunking Logic
            for para in paragraphs:
                para = para.strip()
                if not para: continue
                
                if len(current_chunk) + len(para) < 1500:
                    current_chunk += para + "\n\n"
                else:
                    if len(current_chunk) > 300:
                        chunks.append(current_chunk.strip())
                    current_chunk = para + "\n\n"
            
            if len(current_chunk) > 300:
                chunks.append(current_chunk.strip())

            # Uploading Logic
            print(f"   found {len(chunks)} paragraphs. Uploading...")
            
            for i, text in enumerate(chunks):
                vector = get_embedding(text)
                
                data = {
                    "content": text,
                    "metadata": {
                        "book": "Sözler",
                        "chapter": chapter_name,
                        "format": "markdown"
                    },
                    "embedding": vector
                }
                
                supabase.table("documents").insert(data).execute()
                total_chunks_added += 1
                print(f"   ✅ Uploaded chunk {i+1}/{len(chunks)}", end="\r")

        except Exception as e:
            print(f"❌ Failed on file {filename}: {e}")

    print(f"\n\n🎉 SUCCESS! Added {total_chunks_added} new paragraphs from missing chapters.")

if __name__ == "__main__":
    # Remember to activate your venv first: source venv/bin/activate
    process_missing_files()