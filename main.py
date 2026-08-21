from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_community.chat_message_histories import ChatMessageHistory
from rag_engine import build_vector_store
from agent_core import setup_agent
import os

app = FastAPI(title="Syllabus & Exam Assistant API")

retriever = build_vector_store("syllabus.pdf")
agent_executor = setup_agent(retriever, api_key=os.getenv("GROQ_API_KEY", "YOUR_GROQ_KEY"))

memory = ChatMessageHistory()

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str

@app.post("/chat", response_model=QueryResponse)
async def chat_endpoint(request: QueryRequest):
    try:
        response = agent_executor.invoke({
            "input": request.question,
            "chat_history": memory.messages
        })
       
        memory.add_user_message(request.question)
        memory.add_ai_message(response["output"])
        
        return QueryResponse(answer=response["output"])
    except Exception as e:
        raise HTTPException(status_status_code=500, detail=str(e))
