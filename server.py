"""
AI Workflow Copilot — backend
A tiny FastAPI app that lets a small business owner describe their business
and get an AI-generated task plan, follow-up email, or quick report.
"""

import os
import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

DB_PATH = os.getenv("DB_PATH", "workflow_copilot.db")

app = FastAPI(title="AI Workflow Copilot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- DB setup ----------

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS generations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_desc TEXT NOT NULL,
                task_type TEXT NOT NULL,
                result TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


init_db()


# ---------- Schemas ----------

class GenerateRequest(BaseModel):
    business_desc: str
    task_type: str  # "task_plan" | "email" | "report"


class GenerateResponse(BaseModel):
    id: int
    result: str
    created_at: str


# ---------- Prompting ----------

PROMPTS = {
    "task_plan": (
        "You are a helpful business assistant. A small business owner "
        "described their business as: \"{desc}\". Write a clear, practical "
        "task plan for their day or week — 5 to 8 concrete action items, "
        "no fluff, formatted as a simple numbered list."
    ),
    "email": (
        "You are a helpful business assistant. A small business owner "
        "described their business as: \"{desc}\". Draft a short, friendly "
        "follow-up email they could send to a customer or supplier. "
        "Keep it under 120 words, ready to send with minimal edits."
    ),
    "report": (
        "You are a helpful business assistant. A small business owner "
        "described their business as: \"{desc}\". Write a short weekly "
        "summary report template they can fill in weekly — sections for "
        "sales, expenses, wins, and next week's focus. Keep it concise."
    ),
}


def call_gemini(business_desc: str, task_type: str) -> str:
    if task_type not in PROMPTS:
        raise HTTPException(status_code=400, detail="Invalid task_type")

    if not GEMINI_API_KEY:
        # Fallback so the app is demoable even without an API key configured
        return (
            f"[Demo mode — no GEMINI_API_KEY set]\n\n"
            f"Sample output for '{task_type}' based on: {business_desc}"
        )

    prompt = PROMPTS[task_type].format(desc=business_desc)
    model = genai.GenerativeModel("gemini-flash-latest")
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI generation failed: {e}")


# ---------- Routes ----------

@app.get("/api/")
def root():
    return {"status": "ok", "service": "AI Workflow Copilot"}


@app.post("/api/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    if not req.business_desc.strip():
        raise HTTPException(status_code=400, detail="business_desc is required")

    result_text = call_gemini(req.business_desc, req.task_type)
    created_at = datetime.utcnow().isoformat()

    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO generations (business_desc, task_type, result, created_at) "
            "VALUES (?, ?, ?, ?)",
            (req.business_desc, req.task_type, result_text, created_at),
        )
        new_id = cursor.lastrowid

    return GenerateResponse(id=new_id, result=result_text, created_at=created_at)


@app.get("/api/history")
def history(limit: int = 20):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, business_desc, task_type, result, created_at "
            "FROM generations ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return {"items": [dict(row) for row in rows]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
