import os
import json
import random
from typing import List
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATA_PATH = "data/scraped_text"
OUTPUT_FILE = "data/benchmark_dataset.json"


NUM_CHUNKS_TO_SAMPLE = 20 


class QAPair(BaseModel):
    question: str = Field(description="A user-style question (e.g., 'Can I work if...')")
    answer: str = Field(description="The correct answer based ONLY on the text")

class DatasetOutput(BaseModel):
    qa_pairs: List[QAPair] = Field(description="List of 3 question-answer pairs")

def generate_questions():
    print(" Starting User-Centric Dataset Generation.")

    #  Load & Chunk
    if not os.path.exists(DATA_PATH):
        print(f"Error: {DATA_PATH} not found.")
        return

    loader = DirectoryLoader(DATA_PATH, glob="*.txt", loader_cls=TextLoader)
    documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    all_chunks = text_splitter.split_documents(documents)
    
    
    sample_size = min(NUM_CHUNKS_TO_SAMPLE, len(all_chunks))
    selected_chunks = random.sample(all_chunks, sample_size)
    print(f"   Selected {len(selected_chunks)} chunks to generate scenario questions from.")

    # Setup the Scenario Generator LLM
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7, api_key=OPENAI_API_KEY)
    parser = JsonOutputParser(pydantic_object=DatasetOutput)

   
    prompt = ChatPromptTemplate.from_template(
        """
        You are an expert at simulating users for an Immigration Chatbot.
        Your goal is to generate realistic questions that an immigrant, student, or worker would ask.

        Read the provided text context and generate exactly 3 Question-Answer pairs.

        STRICT RULES FOR QUESTIONS:
        1. DO NOT ask "What is..." or "Define..." questions.
        2. DO ask "Can I...", "If I am...", "Do I need...", or "What happens if..." questions.
        3. Create hypothetical scenarios (e.g., "I am a student, can I work?").
        4. If the text mentions a rule, ask a question about *breaking* that rule or *following* it.

        STRICT RULES FOR ANSWERS:
        1. The answer must be factually correct based ONLY on the context.
        2. Keep the answer helpful and specific.

        Context:
        {context}

        {format_instructions}
        """
    )

    chain = prompt | llm | parser

    #  Loop and Generate
    final_dataset = []
    
    print("This takes a minute")
    for i, chunk in enumerate(selected_chunks):
        try:
            print(f"   Processing chunk {i+1}/{len(selected_chunks)}...")
            
            result = chain.invoke({
                "context": chunk.page_content,
                "format_instructions": parser.get_format_instructions()
            })
            
            for pair in result["qa_pairs"]:
                final_dataset.append({
                    "question": pair["question"],
                    "ground_truth": pair["answer"],
                    "context_used": chunk.page_content, 
                    "source_chunk_id": i
                })
                
        except Exception as e:
            print(f"  Skipped chunk {i}: {e}")

    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final_dataset, f, indent=2)

    print(f"Success . Saved {len(final_dataset)} realistic questions to '{OUTPUT_FILE}'")

if __name__ == "__main__":
    generate_questions()