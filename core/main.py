from fastapi import FastAPI
from pydantic import BaseModel

from core.database import engine
from core import models
from core.models import Base

from finance.langgraph_agent import graph
from finance.ai_explainer import explain_financial_state


# --------------------
# Create FastAPI app
# --------------------

app = FastAPI()


# --------------------
# Create DB tables
# --------------------

Base.metadata.create_all(bind=engine)


# --------------------
# Basic test route
# --------------------

@app.get("/")
def root():
    return {"message": "Backend running successfully"}


# --------------------
# Chat schema
# --------------------

class ChatRequest(BaseModel):
    message: str
    user_id: int


# --------------------
# Chat endpoint
# --------------------

@app.post("/chat")
def chat_finance(request: ChatRequest):

    # Run agentic workflow
    agent_state = graph.invoke({"user_id": request.user_id})

    # Generate AI explanation
    explanation = explain_financial_state(agent_state)

    return {
        "user_message": request.message,
        "ai_response": explanation,
        "raw_data": agent_state
    }
