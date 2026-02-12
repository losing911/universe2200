"""
Broadcast API for Universe 2200

Read-only FastAPI layer providing public simulation data.
Mode: Broadcast (No authentication, No wites)
Data Source: Cached JSON files in data/public/
"""

import json
import os
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

# Configuration
DATA_DIR = Path("data/public")
API_VERSION = "1.0.0"

app = FastAPI(
    title="Universe 2200 Broadcast API",
    description="Read-only public data feed for the Universe 2200 simulation.",
    version=API_VERSION,
    docs_url="/docs",
    redoc_url=None  # Disable ReDoc to keep it simple
)

# CORS Configuration - Allow all for broadcast nature
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET"],  # Strictly read-only
    allow_headers=["*"],
)

def _load_json_safe(filename: str) -> Dict[str, Any]:
    """
    Safely load JSON data from the public data directory.
    Returns empty dict or specific error/state if file missing.
    """
    file_path = DATA_DIR / filename
    
    if not file_path.exists():
        # graceful fallback for missing data (simulation might not have started)
        return {"status": "waiting_for_simulation", "timestamp": None, "data": []}
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        raise HTTPException(status_code=500, detail="Internal Data Error")

@app.get("/")
async def root():
    """API Root / Health Check."""
    return {
        "system": "Universe 2200 Broadcast Node",
        "status": "online",
        "version": API_VERSION
    }

@app.get("/api/news")
async def get_news():
    """
    Get latest news articles and headlines.
    Source: public_news.json
    """
    return _load_json_safe("public_news.json")

@app.get("/api/social")
async def get_social():
    """
    Get recent social media feed and trending topics.
    Source: public_social.json
    """
    return _load_json_safe("public_social.json")

@app.get("/api/metrics")
async def get_metrics():
    """
    Get aggregated world metrics (Unrest, Trust, etc.).
    Source: public_metrics.json
    """
    return _load_json_safe("public_metrics.json")

@app.get("/api/world_snapshot")
async def get_world_snapshot():
    """
    Get full public world snapshot (Metrics + News + Social).
    Source: public_snapshot.json
    """
    return _load_json_safe("public_snapshot.json")

if __name__ == "__main__":
    import uvicorn
    # Local development runner
    print(f"📡 Starting Broadcast API on port 8000...")
    print(f"📂 Serving data from: {DATA_DIR.absolute()}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
