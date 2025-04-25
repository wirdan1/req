from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import psycopg2
from pathlib import Path

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

DB_URL = "postgresql://neondb_owner:npg_2wHo4RrvkFtO@ep-sparkling-frost-a5avyt8l-pooler.us-east-2.aws.neon.tech/gc-db?sslmode=require"

conn = psycopg2.connect(DB_URL)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS antitext_requests (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")
conn.commit()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    cursor.execute("SELECT content, created_at FROM antitext_requests ORDER BY created_at DESC")
    rows = cursor.fetchall()
    return templates.TemplateResponse("index.html", {"request": request, "requests": rows})

@app.post("/submit")
async def submit_antitext(content: str = Form(...)):
    cursor.execute("INSERT INTO antitext_requests (content) VALUES (%s)", (content,))
    conn.commit()
    return RedirectResponse(url="/", status_code=303)
