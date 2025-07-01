"""
Vercel looks for an ASGI app (or a Mangum handler) in the file you point to
from `vercel.json`.  We import the FastAPI instance created in main.py and
wrap it with Mangum so it runs on Vercel’s serverless runtime.
"""

from mangum import Mangum          # ← you forgot this import
from .main import app              # relative import inside the same package

handler = Mangum(app)              # what Vercel will actually call
