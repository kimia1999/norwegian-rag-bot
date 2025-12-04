import json
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

INPUT_FILE = "data/benchmark_dataset.json"
OUTPUT_FILE = "data/benchmark_dataset_clean.json"

MIN_CONTEXT_LENGTH = 200

def setup_auditor():
    
    return ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0, api_key=OPENAI_API_KEY)

def audit_dataset():
    print(" Starting Strict Audit of Benchmark Data.")
    
    if not os.path.exists(INPUT_FILE):
        print(f" Error: {INPUT_FILE} not found.")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    llm = setup_auditor()
    valid_data = []
    
    stats = {
        "total": len(data),
        "deleted_empty": 0,
        "deleted_hallucination": 0,
        "kept": 0
    }

    print(f"   Reviewing {len(data)} generated Q&A pairs.\n")

    for i, item in enumerate(data):
        question = item.get("question")
        answer = item.get("ground_truth")
        context = item.get("context_used", "") 
        
       
        if len(context) < MIN_CONTEXT_LENGTH:
            print(f"    Q{i}: REJECTED (Context too short : likely just URL)")
            stats["deleted_empty"] += 1
            continue

    
        prompt = f"""
        You are a Data Quality Auditor.
        Verify if the ANSWER can be derived EXCLUSIVELY from the CONTEXT.

        Context: "{context}"
        
        Question: "{question}"
        Generated Answer: "{answer}"

        Rules:
        1. If the Context is just a header or menu and contains no real info, FAIL.
        2. If the Answer contains facts NOT present in the Context (External Knowledge), FAIL.
        3. If the Answer is fully supported by the Context, PASS.
        
        Reply ONLY with "PASS" or "FAIL".
        """

        try:
            response = llm.invoke(prompt)
            verdict = response.content.strip().upper()
            
            if "PASS" in verdict:
                
                valid_data.append(item)
                stats["kept"] += 1
            else:
                print(f"    Q{i}: REJECTED (Hallucination or External Info)")
                
            
                stats["deleted_hallucination"] += 1
                
        except Exception as e:
            print(f"Error checking Q{i}: {e}")

    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(valid_data, f, indent=2)

    print("\n" + "="*30)
    print(" AUDIT REPORT")
    print(f"   Total Original:       {stats['total']}")
    print(f"    Deleted (URL Only): {stats['deleted_empty']}")
    print(f"    Deleted (Made Up):  {stats['deleted_hallucination']}")
    print(f"    Final Clean Set:    {stats['kept']}")
    print(f"    Saved to: {OUTPUT_FILE}")
    print("="*30)

if __name__ == "__main__":
    audit_dataset()