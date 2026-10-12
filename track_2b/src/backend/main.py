import json
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.backend.models import (
    BautagebuchRequest,
    BautagebuchResponse,
    SuvaAuditRequest,
    SuvaAuditResponse,
    InfrastructureDecisionRequest,
    InfrastructureDecisionResponse,
    TenderComparisonRequest,
    TenderComparisonResponse,
    PermitOppositionRequest,
    PermitOppositionResponse,
)
from src.backend.provider import apertus_engine
from src.backend.legal_rag import swiss_decision_engine
from src.backend.pdf_exporter import generate_bautagebuch_pdf, generate_decision_report_pdf

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chronomine.main")

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
GEO_DIR = BASE_DIR / "data" / "geo"
DEMO_DIR = BASE_DIR / "data" / "demo"
KNOWLEDGE_DIR = BASE_DIR / "data" / "knowledge"

app = FastAPI(
    title="SwissBau Copilot — Apertus AI (ChronoMine)",
    description="Sovereign Swiss Construction Project Developer & Owner (Bauherr) Copilot powered by Apertus v1.5-70B",
    version="2.0.0"
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
@app.get("/api/demo/field-notes")
async def get_demo_field_notes():
    notes_file = DEMO_DIR / "field_notes.json"
    if not notes_file.exists():
        return []
    with open(notes_file, "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/api/geo/swiss-tunnels")
async def get_swiss_railway_tunnels():
    f = GEO_DIR / "swiss_railway_tunnels.geojson"
    if not f.exists():
        raise HTTPException(status_code=404, detail="swiss_railway_tunnels.geojson not found")
    with open(f, "r", encoding="utf-8") as fp:
        return json.load(fp)


@app.get("/api/geo/gotthard-line")
async def get_gotthard_base_tunnel_geometry():
    f = GEO_DIR / "gotthard_base_tunnel_sbb.geojson"
    if not f.exists():
        raise HTTPException(status_code=404, detail="gotthard_base_tunnel_sbb.geojson not found")
    with open(f, "r", encoding="utf-8") as fp:
        return json.load(fp)


@app.get("/api/knowledge/fedlex-bauav")
async def get_fedlex_bauav():
    f = KNOWLEDGE_DIR / "fedlex_bauav_2022.json"
    if not f.exists():
        raise HTTPException(status_code=404, detail="fedlex_bauav_2022.json not found")
    with open(f, "r", encoding="utf-8") as fp:
        return json.load(fp)


@app.get("/api/knowledge/suva-vital-rules")
async def get_suva_vital_rules():
    f = KNOWLEDGE_DIR / "suva_vital_rules_underground.json"
    if not f.exists():
        raise HTTPException(status_code=404, detail="suva_vital_rules_underground.json not found")
    with open(f, "r", encoding="utf-8") as fp:
        return json.load(fp)


@app.get("/api/knowledge/sia-118")
async def get_sia_118():
    f = KNOWLEDGE_DIR / "sia_118_articles.json"
    if not f.exists():
        raise HTTPException(status_code=404, detail="sia_118_articles.json not found")
    with open(f, "r", encoding="utf-8") as fp:
        return json.load(fp)


@app.get("/api/demo/rules")
@app.get("/api/demo/suva-rules")
async def get_demo_suva_rules():
    rules_file = KNOWLEDGE_DIR / "suva_rules.json"
    if not rules_file.exists():
        return {"rules": []}
    with open(rules_file, "r", encoding="utf-8") as f:
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


@app.post("/api/copilot/bautagebuch/export-pdf")
async def export_bautagebuch_pdf(data: BautagebuchResponse):
    try:
        pdf_bytes = generate_bautagebuch_pdf(data)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=Bautagebuch_SIA118_{data.date}.pdf"
            }
        )
    except Exception as e:
        logger.error(f"Error generating Bautagebuch PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================================================
# Swiss Construction Project Developer & Owner (Bauherr) Copilot Endpoints
# ==============================================================================

@app.post("/api/project/infrastructure-arbitration", response_model=InfrastructureDecisionResponse)
async def arbitrate_infrastructure(req: InfrastructureDecisionRequest):
    """
    Multicriteria comparative arbitration between bridge, tunnel, and surface route variants.
    Evaluates costs (CapEx/OpEx), litigation/opposition risk (LAT/OPB/ISOS), delays, and environmental impact.
    """
    try:
        return await swiss_decision_engine.arbitrate_infrastructure(req)
    except Exception as e:
        logger.error(f"Error arbitrating infrastructure: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/project/tender-comparison", response_model=TenderComparisonResponse)
async def compare_tender_bids(req: TenderComparisonRequest):
    """
    Analyzes contractor tender bids according to SIA 118 & AIMP public procurement.
    Detects abnormally low prices, hidden exclusion clauses, and ranks bidders.
    """
    try:
        return await swiss_decision_engine.compare_tender_bids(req)
    except Exception as e:
        logger.error(f"Error comparing tender bids: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/project/permit-opposition", response_model=PermitOppositionResponse)
async def evaluate_permit_opposition(req: PermitOppositionRequest):
    """
    Analyzes neighbor/association building permit oppositions under Swiss Planning & Environmental Laws (LAT / OPB).
    Provides qualified rebuttal strategy and formal letters.
    """
    try:
        return await swiss_decision_engine.evaluate_permit_opposition(req)
    except Exception as e:
        logger.error(f"Error evaluating permit opposition: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/project/export-decision-pdf")
async def export_decision_pdf(data: InfrastructureDecisionResponse):
    """Generates official Swiss Infrastructure Strategic Decision & Siting Optimization Report."""
    try:
        import unicodedata
        import re
        pdf_bytes = generate_decision_report_pdf(data)
        clean_name = unicodedata.normalize('NFKD', data.project_name).encode('ASCII', 'ignore').decode('ASCII')
        safe_name = re.sub(r"[^a-zA-Z0-9_\-]", "_", clean_name).strip("_") or "Projet"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=Decision_Arbitrage_{safe_name}.pdf"
            }
        )
    except Exception as e:
        logger.error(f"Error generating decision PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/system/status")
async def get_system_status():
    mode = apertus_engine.provider_mode
    is_cloud = mode in ("swisscom", "cscs")
    return {
        "provider": mode,
        "model": apertus_engine.model,
        "deployment_profile": "Sovereign Swiss Cloud" if is_cloud else "Air-Gapped Subterranean Node",
        "jurisdiction": "Switzerland (Swisscom Cloud / CSCS Lugano)" if is_cloud else "On-Premise / Subsurface Workstation",
        "data_residency_swiss": True,
        "nlpd_compliant": True,
        "connected": True
    }


# Mount demo images if directory exists
DEMO_IMAGES_DIR = DEMO_DIR / "images"
if DEMO_IMAGES_DIR.exists():
    app.mount("/demo/images", StaticFiles(directory=str(DEMO_IMAGES_DIR)), name="demo-images")

# Mount static frontend files if directory exists
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
