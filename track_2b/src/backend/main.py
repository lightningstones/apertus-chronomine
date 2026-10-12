import json
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.backend.models import (
    BautagebuchRequest,
    BautagebuchResponse,
    SuvaAuditRequest,
    SuvaAuditResponse
)
from src.backend.provider import apertus_engine

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chronomine.main")

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
GEO_DIR = BASE_DIR / "data" / "geo"
DEMO_DIR = BASE_DIR / "data" / "demo"

app = FastAPI(
    title="ChronoMine AI — SwissTunnelCopilot",
    description="Sovereign Subterranean Situation Awareness & Compliance Copilot powered by Apertus v1.5",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ChronoMine AI",
        "provider_mode": apertus_engine.provider_mode,
        "model": apertus_engine.model,
        "sovereign_swiss_cloud": apertus_engine.provider_mode == "cscs",
        "air_gapped_compatible": True
    }


@app.get("/api/geo/tunnels")
async def get_tunnels_geojson():
    tunnel_file = GEO_DIR / "tunnels.geojson"
    if not tunnel_file.exists():
        raise HTTPException(status_code=404, detail="tunnels.geojson not found")
    with open(tunnel_file, "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/api/geo/miners")
async def get_miners_geojson():
    miner_file = GEO_DIR / "miners.geojson"
    if not miner_file.exists():
        raise HTTPException(status_code=404, detail="miners.geojson not found")
    with open(miner_file, "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/api/demo/notes")
async def get_demo_field_notes():
    notes_file = DEMO_DIR / "field_notes.json"
    if not notes_file.exists():
        return []
    with open(notes_file, "r", encoding="utf-8") as f:
        return json.load(f)


@app.post("/api/copilot/bautagebuch", response_model=BautagebuchResponse)
async def generate_bautagebuch(req: BautagebuchRequest):
    try:
        return await apertus_engine.generate_bautagebuch(req)
    except Exception as e:
        logger.error(f"Error generating Bautagebuch: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/copilot/suva-audit", response_model=SuvaAuditResponse)
async def audit_suva_safety(req: SuvaAuditRequest):
    try:
        return await apertus_engine.audit_suva_safety(req)
    except Exception as e:
        logger.error(f"Error running SUVA audit: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Mount static frontend files if directory exists
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
