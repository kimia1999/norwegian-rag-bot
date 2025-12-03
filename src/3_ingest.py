import os
import shutil
from dotenv import load_dotenv # Used to load the key securely

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma


load_dotenv() 


KEY = os.getenv("OPENAI_API_KEY")
if not KEY:
    print(" OPENAI_API_KEY not found in .env file.")
    exit()


DATA_PATH = "data/scraped_text"
DB_PATH = "chroma_db"

def ingest_data():
    

    if not os.path.exists(DATA_PATH):
        print(f" error: {DATA_PATH} not found.")
        return

    print(" Loading text files...")
    loader = DirectoryLoader(DATA_PATH, glob="*.txt", loader_cls=TextLoader)
    documents = loader.load()
    print(f"  Loaded {len(documents)} documents.")

    if len(documents) == 0:
        print("No documents found.")
        return

    print(" Splitting text")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(documents)
    print(f"  Created {len(chunks)} chunks.")

    print(f" Generating Embeddings and saving to '{DB_PATH}'.")
    

    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)

    
    embeddings = OpenAIEmbeddings(
    api_key=KEY,
    chunk_size=100)
    
    
    db = Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings, 
        persist_directory=DB_PATH
    )
    
    print(" Success. Database created")

if __name__ == "__main__":
    ingest_data()