# University Course & Exam Assistant

A grounded AI assistant for university course and exam preparation. The system combines Retrieval-Augmented Generation (RAG), deterministic GPA and study-schedule tools, conversation memory, and a FastAPI backend with a simple web frontend.

## Project Overview

The assistant helps students:

- Ask course-specific questions using provided course material.
- Retrieve grounded information from a syllabus/course document.
- Calculate the impact of an anticipated grade on cumulative GPA.
- Generate a day-by-day study schedule.
- Continue multi-turn conversations using short-term memory.
- Avoid inventing course policies when the requested information is not available in the provided material.

## Main Technologies

- Python 3.12
- Groq API
- LangChain
- LangGraph
- FastAPI
- Pydantic
- FAISS
- HuggingFace Embeddings (`sentence-transformers/all-MiniLM-L6-v2`)
- PyPDFLoader
- HTML / CSS / JavaScript

## System Architecture

```text
                    Student
                       |
                       v
                 Web Frontend
                 index.html
                       |
                       v
                 FastAPI API
                  main.py
                       |
                       v
                 Agent Core
                agent_core.py
                       |
          +------------+------------+
          |            |            |
          v            v            v
        RAG Tool     GPA Tool    Study Tool
          |            |            |
          v            v            v
     rag_engine.py   tools.py    tools.py
          |
          v
       FAISS
          |
          v
   Syllabus / Course
       Material
                       
                       |
                       v
                  Groq LLM
                       |
                       v
                  Final Answer

                + Conversation Memory
```

## Grounded RAG

The RAG pipeline processes the course PDF as follows:

```text
PDF
 -> PyPDFLoader
 -> RecursiveCharacterTextSplitter
 -> HuggingFace Embeddings
 -> FAISS Vector Store
 -> Retriever
 -> Agent RAG Tool
 -> Groq
 -> Grounded Answer
```

The retriever returns the most relevant document chunks for the user's question. The Agent uses those results when answering course-specific questions.

The assistant is instructed not to invent course-specific facts. When information cannot be found in the provided material, it should explain that the information was not found and direct the student to the Teaching Assistant or instructor.

## Project Structure

```text
university_ai_course_assistant/
|
|-- agent_core.py        # Agent, Groq, prompt, guardrails, tools, memory
|-- rag_engine.py        # PDF loading, chunking, embeddings, FAISS, retrieval
|-- tools.py             # GPA and study-schedule tools
|-- main.py              # FastAPI application
|-- index.html           # Frontend user interface
|-- syllabus.pdf         # Course material used by the RAG pipeline
|-- test_all.py          # Full backend/integration test suite
|-- .env                 # Local API secret (not committed)
|-- .gitignore
|-- requirements.txt
|-- README.md
`-- .venv/
```

## Team Responsibilities

### Member 1 - RAG & Vector Store

File: `rag_engine.py`

Responsible for:

- Loading the syllabus PDF.
- Splitting documents into chunks.
- Creating HuggingFace embeddings.
- Creating the FAISS vector store.
- Retrieving relevant course material.

Main interface:

```python
retrieve_relevant_documents(query: str)
```

### Member 2 - Custom Tools

File: `tools.py`

Responsible for:

- GPA impact simulation.
- Study schedule generation.
- Input validation and deterministic calculations.

Main tools:

```python
gpa_impact_simulator(...)
generate_study_schedule(...)
```

### Member 3 - Agent Core & Prompt Engineering

File: `agent_core.py`

Responsible for:

- Groq LLM configuration.
- System prompt and guardrails.
- RAG tool integration.
- Tool integration.
- Conversation memory.
- Agent creation.
- Public `ask_agent()` interface.

Main interface:

```python
ask_agent(message: str, session_id: str)
```

### Member 4 - FastAPI Backend

File: `main.py`

Responsible for:

- FastAPI server.
- Request and response models.
- `/chat` endpoint.
- Connecting the frontend to the Agent.
- API error handling.

### Member 5 - Frontend

File: `index.html`

Responsible for:

- Chat interface.
- User input.
- Displaying assistant responses.
- Connecting the browser to the FastAPI backend.
- User-friendly interaction.

## Requirements

Use Python 3.12 for the project environment.

Create and activate the virtual environment:

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

If `requirements.txt` is not yet complete, the core packages used by the project include:

```powershell
python -m pip install langchain langchain-groq langgraph python-dotenv langchain-community langchain-huggingface faiss-cpu fastapi uvicorn pydantic
```

## Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Never commit `.env` or the API key to GitHub.

Recommended `.gitignore` entries:

```text
.env
.venv/
__pycache__/
*.pyc
```

## Course Material

Place the syllabus/course document in the project root with the filename:

```text
syllabus.pdf
```

The file must contain actual PDF content. An empty PDF will cause the PDF loader to fail.

## Running the Backend

Start FastAPI from the project root:

```powershell
.venv\Scripts\python.exe -m uvicorn main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

## Running the Frontend

The current application can be served by FastAPI itself.

Open:

```text
http://127.0.0.1:8000/
```

This avoids needing a separate frontend server for the demo.

## API

### GET `/`

Health check.

Response:

```json
{
  "message": "Syllabus & Exam Assistant API is running."
}
```

### POST `/chat`

Request:

```json
{
  "question": "What is the final exam worth?",
  "session_id": "student-001"
}
```

Response:

```json
{
  "answer": "..."
}
```

The `session_id` identifies the conversation thread used by the Agent memory.

## Testing

The project includes `test_all.py` for end-to-end backend testing.

Run:

```powershell
.venv\Scripts\python.exe test_all.py
```

The integration tests cover:

1. FastAPI health check.
2. RAG + Agent + FastAPI.
3. Grounding / missing-information guardrail.
4. GPA tool.
5. Study schedule tool.
6. Conversation memory.
7. Empty-question handling.

A successful run should end with:

```text
Passed: 7/7
Failed: 0/7

ALL TESTS PASSED
```

## Example Questions

### Course / RAG

```text
What is the final exam worth?
```

```text
What are the attendance rules?
```

```text
What is the prerequisite for Operating Systems?
```

### GPA

```text
My current GPA is 3.2, I completed 90 credits,
and I expect an A in a 3-credit course.
What will my new GPA be?
```

### Study Schedule

```text
Create a study schedule for these topics:
Introduction, SQL, Normalization, Transactions.
My exam is on 2026-09-10 and I can study 3 hours per day.
```

### Memory

```text
The database midterm is worth 25%.
```

Then:

```text
How much is it worth?
```

The Agent should understand the reference from the previous message.

## Guardrails

The Agent is designed to:

- Prefer retrieved course material for course-specific facts.
- Avoid inventing policies, dates, grades, attendance rules, prerequisites, or deadlines.
- Use deterministic tools for GPA and scheduling calculations.
- Ask for or recognize required information when a tool needs it.
- Tell the student to consult the TA or instructor when required course information is unavailable.

## Git Workflow Used by the Team

The current team workflow uses the shared `main` branch.

Before pushing:

```powershell
git status
git diff
```

Add changes:

```powershell
git add agent_core.py main.py test_all.py
```

Commit:

```powershell
git commit -m "Integrate agent, RAG, tools, API, and tests"
```

Get the latest team changes:

```powershell
git pull --rebase origin main
```

Push:

```powershell
git push origin main
```

Never commit `.env` or API keys.

## Current Project Flow

```text
User
  |
  v
Frontend
  |
  | POST /chat
  v
FastAPI
  |
  v
Agent Core
  |
  +----> Course Material Search Tool ----> FAISS / Retriever
  |
  +----> GPA Impact Simulator
  |
  +----> Study Schedule Generator
  |
  +----> Conversation Memory
  |
  v
Groq LLM
  |
  v
Final grounded response
```

## Purpose of the Project

The goal is to provide a practical course companion that combines grounded retrieval with deterministic academic tools. The RAG component keeps course answers tied to supplied material, while the GPA and scheduling tools handle calculations and planning that should not be delegated to free-form LLM generation.
