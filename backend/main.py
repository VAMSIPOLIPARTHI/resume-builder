from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel,Field
from typing import Optional,Any
import json, uuid, os, mimetypes

app = FastAPI(title="Resume Editor Mock AI")

# --- CORS (allow front‑end dev port) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vite
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data store (disk or in‑mem) ---
STORE_PATH = "sample_store.json"
if not os.path.exists(STORE_PATH):
    with open(STORE_PATH, "w") as f:
        json.dump({}, f)

def save_json(data: dict):
    with open(STORE_PATH, "w") as f:
        json.dump(data, f, indent=2)

def load_json() -> dict:
    with open(STORE_PATH) as f:
        return json.load(f)

# --- Schemas ---
class AIRequest(BaseModel):
    section: str
    content: str
class Resume(BaseModel):
    id: Optional[str] = Field(default=None)
    # accept **any** other keys the user sends
    model_config = {"extra": "allow"}

# ---------- Endpoints ----------

@app.post("/ai-enhance")  # ✅ fixed hyphen
async def ai_enhance(req: AIRequest):
    """Return a lightly ‘improved’ version of the content."""
    improved = f"{req.content.strip()} (✨ Polished by AI ✨)"
    return {"section": req.section, "improved": improved}
@app.post("/save-resume")
async def save_resume(resume: Resume):
    data = load_json()
    rid = resume.id or str(uuid.uuid4())
    # store everything except the id itself
    data[rid] = resume.model_dump(exclude={"id"})
    save_json(data)
    return {"id": rid, "status": "saved"}


@app.post("/upload")  # ✅ correct
async def upload_resume(file: UploadFile = File(...)):
    """Accept .pdf or .docx and return dummy parsed content."""
    if mimetypes.guess_type(file.filename)[0] not in {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    }:
        raise HTTPException(400, "Only .pdf or .docx allowed")

    # Fake parse
    dummy = {
        "name": "Jane Doe",
        "summary": "Enthusiastic developer with 2 years’ experience.",
        "experience": [{"company": "Acme", "role": "Intern", "years": "2023–2024"}],
        "education": [{"degree": "B.Tech CSE", "year": 2023}],
        "skills": ["React", "FastAPI", "SQL"]
    }
    return {"parsed": dummy}
