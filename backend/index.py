"""
Vercel’s Python runtime looks for 'app' inside the file referenced by vercel.json.
We just re‑export the FastAPI instance from main.py.
"""
from backend.main import app
