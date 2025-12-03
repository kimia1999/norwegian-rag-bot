import os
import time
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware 
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()
app = FastAPI(title="Norwegian Immigration RAG API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

DB_PATH = "chroma_db"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("Error: OPENAI_API_KEY missing.")

print("Loading Vector Database...")
embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)

if not os.path.exists(DB_PATH):
    raise RuntimeError("chromadb folder not found! Run 3_ingest.py first.")

vector_db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
print("Database loaded successfully.")

llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.3, api_key=OPENAI_API_KEY)

prompt = ChatPromptTemplate.from_template("""
Answer the following question based only on the provided context:

<context>
{context}
</context>

Question: {input}
""")

document_chain = create_stuff_documents_chain(llm, prompt)
retriever = vector_db.as_retriever(search_kwargs={"k": 3})
qa_chain = create_retrieval_chain(retriever, document_chain)


class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: Optional[str] = "gpt-3.5-turbo"
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
            "id": "norwegian-rag-bot",
            "object": "model",
            "created": 1677610602,
            "owned_by": "student-project"
        }]
    }

@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
def chat_completions(request: ChatCompletionRequest):
    user_message = request.messages[-1].content
    print(f"Received Question: {user_message}")

    try:
        result = qa_chain.invoke({"input": user_message})
        answer_text = result['answer']
    except Exception as e:
        print(f"Error during RAG: {e}")
        answer_text = "I encountered an error accessing my database."

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