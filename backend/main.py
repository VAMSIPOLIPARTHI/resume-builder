# api/index.py
import os, json, uuid, mimetypes
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from mangum import Mangum   # <‑‑ lets FastAPI run as a Vercel/Lambda function

app = FastAPI(title="Resume Editor Mock AI")

# ─────── CORS ────────────────────────────────────────────────────────────
# During local dev we allow localhost:5173.  
# In production set an env var ALLOWED_ORIGINS with a comma‑separated list:
#   ALLOWED_ORIGINS=http://localhost:5173,https://your-frontend.vercel.app
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in allowed_origins if o],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────── Lightweight disk “DB” ───────────────────────────────────────────
STORE_PATH = Path(__file__).with_suffix(".json")          # api/index.json
if not STORE_PATH.exists():
    STORE_PATH.write_text("{}")

def load_json() -> dict:
    return json.loads(STORE_PATH.read_text())

def save_json(data: dict) -> None:
    STORE_PATH.write_text(json.dumps(data, indent=2))

# ─────── Schemas ────────────────────────────────────────────────────────
class AIRequest(BaseModel):
    section: str
    content: str

class Resume(BaseModel):
    id: Optional[str] = Field(default=None)
    model_config = {"extra": "allow"}      # accept any extra keys

# ─────── Routes ─────────────────────────────────────────────────────────
@app.post("/ai-enhance")
async def ai_enhance(req: AIRequest):
    return {
        "section": req.section,
        "improved": f"{req.content.strip()} (✨ Polished by AI ✨)"
    }

@app.post("/save-resume")
async def save_resume(resume: Resume):
    data = load_json()
    rid = resume.id or str(uuid.uuid4())
    data[rid] = resume.model_dump(exclude={"id"})
    save_json(data)
    return {"id": rid, "status": "saved"}

@app.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    if mimetypes.guess_type(file.filename)[0] not in {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }:
        raise HTTPException(400, "Only .pdf or .docx allowed")

    dummy_parsed = {
        "name": "Jane Doe",
        "summary": "Enthusiastic developer with 2 years’ experience.",
        "experience": [{"company": "Acme", "role": "Intern", "years": "2023–2024"}],
        "education": [{"degree": "B.Tech CSE", "year": 2023}],
        "skills": ["React", "FastAPI", "SQL"],
    }
    return {"parsed": dummy_parsed}

# ─────── Vercel/Lambda adapter ──────────────────────────────────────────
handler = Mangum(app)
