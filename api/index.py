"""Vercel serverless entry — re-exports the Flask `app` from /app.py at repo root."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from app import app  # noqa: E402,F401
