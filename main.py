from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from agent_core import ask_agent


app = FastAPI(
    title="Syllabus & Exam Assistant API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str
    session_id: str = "default-session"


class QueryResponse(BaseModel):
    answer: str


@app.get("/")
async def root():
    return FileResponse("index.html")


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