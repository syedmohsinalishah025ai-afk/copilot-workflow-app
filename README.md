# Copilot

An AI workflow assistant for small business owners. Describe your business once, then generate a task plan, a follow-up email, or a weekly report — instantly, in plain language, tailored to what you told it.

**Live demo:** https://splendid-pasca-2d0216.netlify.app

## What it does

Small business owners rarely have time to write structured plans, customer emails, or weekly reports from scratch. Copilot takes a short description of the business and generates one of three outputs on demand:

- **Task Plan** — a practical, ordered weekly action plan
- **Follow-up Email** — a ready-to-send customer thank-you/follow-up
- **Weekly Report** — a fill-in-the-blanks store summary template

Every generation is saved and shown in a history list, so past outputs stay accessible.

## Tech stack

- **Frontend:** HTML, Tailwind CSS, vanilla JavaScript
- **Backend:** FastAPI (Python)
- **AI:** Google Gemini (`gemini-2.0-flash`)
- **Storage:** SQLite
- **Deployment:** Vercel (backend), Netlify (frontend)

## How it works

1. User describes their business and picks an output type
2. Frontend sends a `POST` request to the FastAPI backend
3. Backend builds a prompt and calls the Gemini API
4. Result is saved to SQLite and returned to the frontend
5. Frontend renders the result (parsed from Markdown) and refreshes the history list

## Running locally

```bash
# Backend
pip install -r requirements.txt
# add your GEMINI_API_KEY to a .env file
python server.py

# Frontend
# just open index.html in a browser
```

## Notes

Built as a fast, focused project to demonstrate end-to-end product thinking: from prompt design and API wiring to deployment — using AI tools throughout the build process.