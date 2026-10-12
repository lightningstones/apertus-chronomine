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


def test_infrastructure_arbitration_bridge_vs_tunnel():
    payload = {
        "project_name": "Liaison Traversée de la Vallée Alpine",
        "location": "Valais / Uri",
        "variants": [
            {
                "id": "var_bridge",
                "name": "Viaduc Suspendu des Crêtes (Pont)",
                "type": "bridge",
                "estimated_cost_chf": 42000000.0,
                "estimated_duration_months": 28,
                "description": "Grand viaduc métallique surplombant les habitations riveraines."
            },
            {
                "id": "var_tunnel",
                "name": "Tunnel de Base Souterrain",
                "type": "tunnel",
                "estimated_cost_chf": 78000000.0,
                "estimated_duration_months": 36,
                "description": "Ouvrage souterrain bitube creusé au tunnelier sous la montagne."
            }
        ],
        "priorities": {"cost": 0.25, "opposition_risk": 0.35, "environmental_impact": 0.25, "duration": 0.15}
    }
    res = client.post("/api/project/infrastructure-arbitration", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["project_name"] == "Liaison Traversée de la Vallée Alpine"
    assert len(data["recommended_variant"]) > 0
    assert len(data["evaluations"]) == 2
    assert len(data["swiss_legal_basis"]) > 0
    assert len(data["decision_summary_fr"]) > 0
    assert len(data["decision_summary_de"]) > 0
    types = [e["type"] for e in data["evaluations"]]
    assert "bridge" in types and "tunnel" in types


def test_tender_comparison_sia_118():
    payload = {
        "lot_name": "Lot 204 - Forage et Sécurisation Souterraine",
        "owner_estimate_chf": 5000000.0,
        "bids": [
            {
                "contractor_name": "SwissTunnel Bau AG",
                "total_price_chf": 4850000.0,
                "duration_months": 18,
                "experience_rating": 5,
                "has_subcontractors": False,
                "unforeseen_exclusion_clauses": []
            },
            {
                "contractor_name": "LowCost Excavations Sàrl",
                "total_price_chf": 3400000.0,
                "duration_months": 14,
                "experience_rating": 2,
                "has_subcontractors": True,
                "unforeseen_exclusion_clauses": ["Exclusion de garantie en cas d'infiltrations d'eau karstiques"]
            }
        ]
    }
    res = client.post("/api/project/tender-comparison", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["awarded_contractor"] == "SwissTunnel Bau AG"
    assert len(data["bids_analysis"]) == 2
    low_bid = next(b for b in data["bids_analysis"] if b["contractor_name"] == "LowCost Excavations Sàrl")
    assert low_bid["is_abnormally_low"] is True
    assert len(low_bid["hidden_risk_flags"]) >= 2
    assert any("SIA 118" in rec for rec in data["contractual_recommendations"])


def test_permit_opposition_evaluation():
    payload = {
        "project_title": "Portail Nord Tunnel Alpin",
        "project_location": "Sedrun (GR)",
        "opposition_raw_text": (
            "Nous formons opposition formelle contre le projet. Le passage continu de camions et le bruit assourdissant "
            "du concassage de nuit violent l'Ordonnance sur le bruit (OPB). De plus, la hauteur du silo de ventilation "
            "dépasse le gabarit et prive nos chalets d'ensoleillement selon l'art. 679/684 CC."
        ),
        "inquiry_deadline_days": 30
    }
    res = client.post("/api/project/permit-opposition", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["grievances"]) >= 2
    categories = [g["category"] for g in data["grievances"]]
    assert any("Bruit" in c for c in categories)
    assert "opposition" in data["draft_rebuttal_letter_fr"].lower() or "einsprache" in data["draft_rebuttal_letter_de"].lower()
    assert data["estimated_delay_weeks"] > 0


def test_export_decision_pdf():
    arb_payload = {
        "project_name": "Franchissement Valais-Uri",
        "location": "Valais / Uri",
        "variants": [
            {
                "id": "var_bridge",
                "name": "Viaduc Panoramique",
                "type": "bridge",
                "estimated_cost_chf": 35000000.0,
                "estimated_duration_months": 24,
                "description": "Viaduc en arc béton."
            },
            {
                "id": "var_tunnel",
                "name": "Tunnel de Faîte",
                "type": "tunnel",
                "estimated_cost_chf": 55000000.0,
                "estimated_duration_months": 30,
                "description": "Tunnel foré."
            }
        ],
        "priorities": {"cost": 0.3, "opposition_risk": 0.4, "environmental_impact": 0.2, "duration": 0.1}
    }
    arb_res = client.post("/api/project/infrastructure-arbitration", json=arb_payload)
    assert arb_res.status_code == 200
    arb_data = arb_res.json()

    pdf_res = client.post("/api/project/export-decision-pdf", json=arb_data)
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert pdf_res.content.startswith(b"%PDF-")
    assert len(pdf_res.content) > 1500


def test_optimal_siting_comparator_multi_candidate():
    """
    Tests finding the optimal geographic placement and siting position for infrastructure
    reconciling: 1. Oppositions & Recours (LAT/OPB), 2. Prix, 3. Délais, 4. Impact Voisinage.
    """
    payload = {
        "project_name": "Contournement Cantonal & Desserte Régionale",
        "location": "Valais / Vaud",
        "variants": [
            {
                "id": "var_nord",
                "name": "Tracé Nord (Crête & Semi-enterré)",
                "location_name": "Crête Nord (Contournement)",
                "coordinates": [8.7850, 46.6740],
                "proximity_to_housing_m": 950,
                "zoning_type": "Zone forestière & sous-sol",
                "type": "corridor",
                "estimated_cost_chf": 54000000.0,
                "estimated_duration_months": 28,
                "description": "Tracé en hauteur éloigné des agglomérations."
            },
            {
                "id": "var_median",
                "name": "Tracé Médian (Plateau Agricole)",
                "location_name": "Plateau d'Ergisch",
                "coordinates": [8.7730, 46.6680],
                "proximity_to_housing_m": 420,
                "zoning_type": "Surfaces d'assolement (SDA)",
                "type": "surface",
                "estimated_cost_chf": 38000000.0,
                "estimated_duration_months": 26,
                "description": "Tracé touchant des terres d'assolement protégées."
            },
            {
                "id": "var_sud",
                "name": "Tracé Sud (Fond de Vallée)",
                "location_name": "Fond de Vallée Résidentiel",
                "coordinates": [8.7610, 46.6620],
                "proximity_to_housing_m": 130,
                "zoning_type": "Zone résidentielle dense",
                "type": "surface",
                "estimated_cost_chf": 26000000.0,
                "estimated_duration_months": 20,
                "description": "Tracé économique mais longeant les habitations."
            }
        ],
        "priorities": {
            "cost": 0.25,
            "opposition_risk": 0.35,
            "environmental_impact": 0.25,
            "duration": 0.15
        }
    }
    res = client.post("/api/project/infrastructure-arbitration", json=payload)
    assert res.status_code == 200
    data = res.json()

    # Optimal placement assertions
    assert data["project_name"] == "Contournement Cantonal & Desserte Régionale"
    assert data["recommended_variant"] is not None
    assert data["optimal_location_name"] is not None
    assert len(data["evaluations"]) == 3
    assert len(data["siting_tradeoff_analysis_fr"]) > 20
    assert len(data["decision_summary_fr"]) > 20

    # Ensure evaluations contain candidate location names and legal mitigations
    eval_names = [e["variant_name"] for e in data["evaluations"]]
    assert any("Tracé Nord" in name for name in eval_names)
    assert any("Tracé Sud" in name for name in eval_names)
    for ev in data["evaluations"]:
        assert len(ev["mitigation_recommendations"]) > 0

    # Test PDF export with siting data
    pdf_res = client.post("/api/project/export-decision-pdf", json=data)
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert pdf_res.content.startswith(b"%PDF-")



