import os
import shutil
import json
from dotenv import load_dotenv

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv() 

KEY = os.getenv("OPENAI_API_KEY")
if not KEY:
    print("Error: OPENAI_API_KEY not found in .env file.")
    exit()

DATA_PATH = "data/scraped_text"
DB_PATH = "chroma_db"

DEBUG_FILE = "data/all_chunks_debug.json" 

def ingest_data():
    

    # Load Data
    if not os.path.exists(DATA_PATH):
        print(f" Error: {DATA_PATH} not found.")
        return

    print(" Loading text files...")
    loader = DirectoryLoader(DATA_PATH, glob="*.txt", loader_cls=TextLoader)
    documents = loader.load()
    print(f"   Loaded {len(documents)} documents.")

    if len(documents) == 0:
        print(" No documents found.")
        return

    #  Split Text
    print(" Splitting text")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(documents)
    print(f"   Created {len(chunks)} chunks.")

  
    print(f" Saving chunks to '{DEBUG_FILE}' for inspection...")
    
 
    chunks_data = []
    for i, chunk in enumerate(chunks):
        chunks_data.append({
            "chunk_id": i,
            "source": chunk.metadata.get("source", "unknown"),
            "content": chunk.page_content
        })
    
    with open(DEBUG_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks_data, f, indent=2, ensure_ascii=False)
   
    print(f"Embeddings saving to '{DB_PATH}'...")
    
    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)

    embeddings = OpenAIEmbeddings(
        api_key=KEY,
        chunk_size=100 
    )
    
    db = Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings, 
        persist_directory=DB_PATH
    )
    
    print("  Database created.")
    print(f" chunks in: {DEBUG_FILE}")

if __name__ == "__main__":
    ingest_data()