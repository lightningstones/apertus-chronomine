import os
import sys
from pathlib import Path

# Ensure track_2b is on sys.path for test discovery from root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient
from src.backend.main import app

client = TestClient(app)


def test_health_check():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["air_gapped_compatible"] is True


def test_get_tunnels_geojson():
    res = client.get("/api/geo/tunnels")
    assert res.status_code == 200
    data = res.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) > 0


def test_get_miners_geojson():
    res = client.get("/api/geo/miners")
    assert res.status_code == 200
    data = res.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) > 0


def test_bautagebuch_multilingual_portuguese():
    payload = {
        "raw_text": "A escavadora partiu uma tubagem de drenagem no PK 3.200, paragem 2h30, 3 homens a desobstruir lama.",
        "author_name": "Manuel Silva",
        "author_role": "Mineiro",
        "location_pk": "PK 3.200",
        "target_language": "de"
    }
    res = client.post("/api/copilot/bautagebuch", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["delay_hours"] == 2.5
    assert data["regierapport"]["is_required"] is True
    assert "SIA 118" in data["regierapport"]["sia_reference"]
    assert "BAUTAGEBUCH" in data["official_log_entry"] or "SIA 118" in data["official_log_entry"]


def test_suva_safety_audit_trench_hazard():
    payload = {
        "description": "Fouille d'excavation de 2m60 de profondeur creusée sans blindage ni caisson avec talus raide."
    }
    res = client.post("/api/copilot/suva-audit", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "critical_danger"
    assert data["stop_work_order"] is True
    assert any("BauAV Art. 54" in r["norm"] for r in data["infracted_rules"])


def test_frontend_index_html():
    res = client.get("/")
    assert res.status_code == 200
    assert "ChronoMine AI" in res.text
    assert "Bautagebuch" in res.text


def test_get_demo_field_notes():
    res = client.get("/api/demo/field-notes")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 3


def test_get_demo_suva_rules():
    res = client.get("/api/demo/suva-rules")
    assert res.status_code == 200
    data = res.json()
    assert "rules" in data
    assert len(data["rules"]) >= 4


def test_system_status():
    res = client.get("/api/system/status")
    assert res.status_code == 200
    data = res.json()
    assert data["data_residency_swiss"] is True
    assert data["nlpd_compliant"] is True
    assert data["connected"] is True


def test_bautagebuch_pdf_export():
    # Generate Bautagebuch data first
    req = {
        "raw_text": "A escavadora partiu uma tubagem de drenagem no PK 3.200, paragem 2h30.",
        "author_name": "Manuel Silva",
        "author_role": "Mineiro",
        "location_pk": "PK 3.200",
        "target_language": "de"
    }
    bautagebuch_res = client.post("/api/copilot/bautagebuch", json=req)
    assert bautagebuch_res.status_code == 200
    bautagebuch_data = bautagebuch_res.json()

    # Request PDF generation
    pdf_res = client.post("/api/copilot/bautagebuch/export-pdf", json=bautagebuch_data)
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert pdf_res.content.startswith(b"%PDF-")
    assert len(pdf_res.content) > 1000


def test_demo_images_static():
    for img_name in ["trench_hazard.svg", "scaffold_hazard.svg", "rockface_hazard.svg"]:
        res = client.get(f"/demo/images/{img_name}")
        assert res.status_code == 200
        assert "<svg" in res.text


def test_swiss_railway_tunnels_ogd():
    res = client.get("/api/geo/swiss-tunnels")
    assert res.status_code == 200
    data = res.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) >= 280
    # Check Gotthard-Basistunnel is in the list
    names = [f["properties"]["name"] for f in data["features"]]
    assert any("Gotthard-Basistunnel" in n for n in names)


def test_gotthard_base_tunnel_geometry():
    res = client.get("/api/geo/gotthard-line")
    assert res.status_code == 200
    data = res.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) == 5
    assert any("Sedrun" in f["properties"]["bp_anf_bez"] for f in data["features"])


def test_fedlex_and_suva_knowledge():
    res_fedlex = client.get("/api/knowledge/fedlex-bauav")
    assert res_fedlex.status_code == 200
    assert "SR 832.311.141" in res_fedlex.json()["systematic_compilation_id"]

    res_suva = client.get("/api/knowledge/suva-vital-rules")
    assert res_suva.status_code == 200
    assert len(res_suva.json()["rules"]) == 10

    res_sia = client.get("/api/knowledge/sia-118")
    assert res_sia.status_code == 200
    assert any("Art. 44" in a["article"] for a in res_sia.json()["articles"])


