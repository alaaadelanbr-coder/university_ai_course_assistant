from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agent_core import ask_agent


app = FastAPI(
    title="Syllabus & Exam Assistant API"
)


class QueryRequest(BaseModel):
    question: str
    session_id: str = "default-session"


class QueryResponse(BaseModel):
    answer: str


@app.get("/")
async def root():
    return {
        "message": "Syllabus & Exam Assistant API is running."
    }


@app.post("/chat", response_model=QueryResponse)
async def chat_endpoint(request: QueryRequest):
    try:
        answer = ask_agent(
            message=request.question,
            session_id=request.session_id
        )

        return QueryResponse(
            answer=answer
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )