import os
import json
import re

# CONFIGURATION
# IMPORTANT: Point this to your Obsidian folder
TARGET_FOLDER = "obsidian-markdown/01 Sözler" 
OUTPUT_FILE = "sozler_data_md.json"

MIN_CHUNK_SIZE = 300 
MAX_CHUNK_SIZE = 1500 

def clean_markdown(text):
    """
    Cleans Obsidian-specific syntax to make it easier for AI to read.
    """
    # 1. Remove [[WikiLinks]] but keep the text inside. 
    # Example: "Read [[The First Word]]" becomes "Read The First Word"
    text = re.sub(r'\[\[(.*?)\]\]', r'\1', text)
    
    # 2. Remove Bold/Italic markers (** or *)
    text = text.replace("**", "").replace("*", "")
    
    # 3. Remove Header markers (### Chapter)
    # We remove the symbols but keep the text as a paragraph
    text = text.replace("### ", "").replace("## ", "").replace("# ", "")
    
    return text

def process_sozler_md():
    all_chunks = []
    chunk_id = 0
    
    if not os.path.exists(TARGET_FOLDER):
        print(f"❌ ERROR: Could not find folder: {TARGET_FOLDER}")
        print("Please check if the folder name matches exactly.")
        return

    print(f"📂 Reading Markdown files from: {TARGET_FOLDER}...")

    for root, dirs, files in os.walk(TARGET_FOLDER):
        files.sort()
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                
                # Get Chapter Name from Filename
                chapter_name = file.replace(".md", "").replace("_", " ")

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        raw_text = f.read()
                        
                    # Clean the Markdown syntax before chunking
                    clean_text = clean_markdown(raw_text)
                        
                    # Split by double newlines (paragraphs)
                    paragraphs = clean_text.split("\n\n")
                    current_chunk = ""
                    
                    for para in paragraphs:
                        para = para.strip()
                        if not para: continue

                        if len(current_chunk) + len(para) < MAX_CHUNK_SIZE:
                            current_chunk += para + "\n\n"
                        else:
                            if len(current_chunk) > MIN_CHUNK_SIZE:
                                all_chunks.append({
                                    "book": "Sözler",
                                    "chapter": chapter_name,
                                    "format": "markdown",
                                    "text": current_chunk.strip()
                                })
                                chunk_id += 1
                            current_chunk = para + "\n\n"
                    
                    if len(current_chunk) > MIN_CHUNK_SIZE:
                        all_chunks.append({
                            "book": "Sözler",
                            "chapter": chapter_name,
                            "format": "markdown",
                            "text": current_chunk.strip()
                        })
                        chunk_id += 1
                        
                except Exception as e:
                    print(f"⚠️ Skipping {file}: {e}")

    # Save to JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Success! Created {len(all_chunks)} chunks in '{OUTPUT_FILE}'")

if __name__ == "__main__":
    process_sozler_md()