import os
import time
from typing import List, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv


from langchain_openai import OpenAIEmbeddings         
from langchain_community.chat_models import ChatOllama 
from langchain_community.vectorstores import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()
app = FastAPI(title="Norwegian Immigration RAG API (Hybrid)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "chroma_db"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


print(" Loading Vector Database.")
if not OPENAI_API_KEY:
    print(" Error: OPENAI_API_KEY missing.")

embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)

if not os.path.exists(DB_PATH):
    raise RuntimeError(" chromadb not found. Run 3_ingest.py first.")

vector_db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
print("Database loaded successfully.")

print(" Connecting to Local Ollama.")
llm = ChatOllama(model="llama3", temperature=0.0)


prompt = ChatPromptTemplate.from_template("""
Answer the following question based ONLY on the provided context.
If you don't know the answer from the context, say "I don't know".

<context>
{context}
</context>

Question: {input}
""")

document_chain = create_stuff_documents_chain(llm, prompt)
retriever = vector_db.as_retriever(search_kwargs={"k": 6})
qa_chain = create_retrieval_chain(retriever, document_chain)


class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: Optional[str] = "llama3" 
    messages: List[Message]

class Choice(BaseModel):
    index: int
    message: Message
    finish_reason: str

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    choices: List[Choice]


@app.get("/v1/models")
def list_models():
    return {
        "object": "list",
        "data": [{
            "id": "norwegian-rag-hybrid",
            "object": "model",
            "owned_by": "local-llama3"
        }]
    }

@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
def chat_completions(request: ChatCompletionRequest):
    user_message = request.messages[-1].content
    print(f" Hybrid Bot received: {user_message}")

    try:
        
        result = qa_chain.invoke({"input": user_message})
        answer_text = result['answer']
    except Exception as e:
        print(f" Error: {e}")
        answer_text = "I encountered an error connecting to Llama ?"

    return ChatCompletionResponse(
        id=f"chatcmpl-{int(time.time())}",
        created=int(time.time()),
        choices=[
            Choice(
                index=0,
                message=Message(role="assistant", content=answer_text),
                finish_reason="stop"
            )
        ]
    )