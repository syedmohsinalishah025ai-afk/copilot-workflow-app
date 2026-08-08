# AI Workflow Copilot

A small tool for small-business owners: describe your business, get an
AI-generated task plan, follow-up email, or weekly report template.

## Run the backend

```
cd backend
pip install -r requirements.txt --break-system-packages
export GEMINI_API_KEY=your_key_here   # optional — falls back to demo mode without it
python3 server.py
```

Backend runs on http://localhost:8001

## Run the frontend

Just open `frontend/index.html` in a browser (it calls the backend at
http://localhost:8001/api). For real deployment, host it on Netlify like
FinanceAI, and update `API_BASE` in the HTML to your deployed backend URL.

## What it does

- POST /api/generate — takes a business description + task type
  (task_plan / email / report), returns AI-generated text, saves it
- GET /api/history — returns recent generations
- SQLite storage, no external DB needed
