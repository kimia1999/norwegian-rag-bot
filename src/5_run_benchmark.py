import json
import time
import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOllama
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATASET_FILE = "data/benchmark_dataset_clean.json"
DB_PATH = "chroma_db"
MODEL_NAME = "llama3"

def setup_rag_system():
    """Re-creates your RAG logic with STRICT rules (Same as main_api.py)"""
    embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
    vector_db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
    
    
    llm = ChatOllama(model=MODEL_NAME, temperature=0.0) 
    
   
    prompt = ChatPromptTemplate.from_template("""
    You are a strict assistant for Norwegian Immigration (UDI). 
    You must answer the question based ONLY on the context provided below.

    Strict Rules:
    1. Do NOT use any outside knowledge, internet data, or training data.
    2. If the answer is NOT found in the context, you MUST say: "I do not know the answer based on the provided UDI documents."
    3. Do not try to be helpful by guessing.

    <context>
    {context}
    </context>

    Question: {input}
    """)
    
    doc_chain = create_stuff_documents_chain(llm, prompt)
    retriever = vector_db.as_retriever(search_kwargs={"k": 3})
    return create_retrieval_chain(retriever, doc_chain)

def llm_judge(question, ground_truth, student_answer):
    """
    STRICT JUDGE: Compares Student Answer vs Ground Truth.
    """
    
    judge_llm = ChatOllama(model="llama3", temperature=0.0)
    
    prompt = f"""
    You are a strict exam grader. 
    Compare the STUDENT ANSWER to the GROUND TRUTH.
    
    Question: {question}
    Ground Truth: {ground_truth}
    Student Answer: {student_answer}
    
    Tasks:
    1. If the Student says "I do not know" (or similar), it is a FAIL (unless Ground Truth is also "I don't know").
    2. Does the Student Answer convey the same factual meaning as the Ground Truth?
    
    Reply ONLY with the single word "PASS" or "FAIL". Do not write sentences.
    """
    
    response = judge_llm.invoke(prompt)
    grade = response.content.strip().upper()
    
    if grade == "PASS" or "PASS" in grade.split():
        return "PASS"
    
    return "FAIL"

def run_benchmark():
    
    
    #  Load Data
    if not os.path.exists(DATASET_FILE):
        print(f" Error: {DATASET_FILE} not found. Run '4_audit_dataset.py' first.")
        return

    with open(DATASET_FILE, "r", encoding="utf-8") as f:
        qa_pairs = json.load(f)
    
    print(f"   Loaded {len(qa_pairs)} validated questions.")
    
    # Setup Bot
    rag_chain = setup_rag_system()
    
    score = 0
    total = len(qa_pairs)
    
    for i, item in enumerate(qa_pairs):
        question = item["question"]
        truth = item["ground_truth"]
        
        print(f"\n Q{i+1}: {question}")
        
        # Ask RAG Bot
        try:
            
            result = rag_chain.invoke({"input": question})
            student_answer = result["answer"]
        except Exception as e:
            student_answer = "Error generating answer"

        
        print(f"      Expected: {truth}")
        print(f"      Got:      {student_answer}")

    
        grade = llm_judge(question, truth, student_answer)
        
        if grade == "PASS":
            print(f"    RESULT: PASS")
            score += 1
        else:
            print(f"    RESULT: FAIL")

    # 5. Final Score
    if total > 0:
        accuracy = (score / total) * 100
        print("\n" + "="*30)
        print(f"FINAL ACCURACY: {accuracy:.1f}%")
        print(f"   Correct: {score}/{total}")
        print("="*30)
    else:
        print("No questions found in dataset.")

if __name__ == "__main__":
    run_benchmark()