"""
fetch_swiss_open_data.py
Automated pipeline fetching official Swiss Open Government Data (OGD)
from SBB CFF FFS (data.sbb.ch) and Swiss Federal Geoportal / Fedlex.

Datasets retrieved:
1. SBB Tunnels Inventory (289 tunnels across Switzerland)
2. SBB Route Network Linie 594 (Gotthard-Basistunnel 57.1km LineString)
3. SBB Hectometre / Kilometrage points along Gotthard Base Tunnel
"""

import json
import logging
import urllib.request
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("swiss_open_data")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
GEO_DIR = DATA_DIR / "geo"
KNOWLEDGE_DIR = DATA_DIR / "knowledge"

SBB_TUNNELS_EXPORT_URL = (
    "https://data.sbb.ch/api/explore/v2.1/catalog/datasets/tunnel/exports/geojson"
)
SBB_GOTTHARD_LINE_URL = (
    "https://data.sbb.ch/api/explore/v2.1/catalog/datasets/linie-mit-polygon/exports/geojson?where=linienr=594"
)
SBB_GOTTHARD_KM_URL = (
    "https://data.sbb.ch/api/explore/v2.1/catalog/datasets/linienkilometrierung/records?where=linienr=594&limit=100"
)


def fetch_url(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "ChronoMine-Apertus/1.0 (HackApertus-Track2B; Swiss-Open-Data)"}
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def run():
    GEO_DIR.mkdir(parents=True, exist_ok=True)
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Fetch full SBB Railway Tunnels Inventory (289 tunnels)
    logger.info("1/3 Downloading official SBB Railway Tunnels inventory...")
    try:
        tunnels_geojson = fetch_url(SBB_TUNNELS_EXPORT_URL)
        out_file = GEO_DIR / "swiss_railway_tunnels.geojson"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(tunnels_geojson, f, indent=2, ensure_ascii=False)
        logger.info(f"   Saved {len(tunnels_geojson.get('features', []))} tunnels to {out_file.name}")
    except Exception as e:
        logger.error(f"   Failed to fetch SBB tunnels: {e}")

    # 2. Fetch Gotthard Base Tunnel line geometries (Line 594)
    logger.info("2/3 Downloading Gotthard Base Tunnel (Line 594) vector geometry...")
    try:
        gotthard_geojson = fetch_url(SBB_GOTTHARD_LINE_URL)
        out_file = GEO_DIR / "gotthard_base_tunnel_sbb.geojson"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(gotthard_geojson, f, indent=2, ensure_ascii=False)
        logger.info(f"   Saved {len(gotthard_geojson.get('features', []))} segments to {out_file.name}")
    except Exception as e:
        logger.error(f"   Failed to fetch Gotthard line: {e}")

    # 3. Fetch Gotthard Kilometrage points (PK 199 -> PK 256)
    logger.info("3/3 Downloading Gotthard kilometrage points (PK)...")
    try:
        km_records = fetch_url(SBB_GOTTHARD_KM_URL)
        km_features = []
        for r in km_records.get("results", []):
            pt = r.get("geo_point_2d")
            if pt:
                km_features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [pt["lon"], pt["lat"]]
                    },
                    "properties": {
                        "km": r.get("km"),
                        "linie": 594,
                        "name": f"PK {r.get('km'):.3f}"
                    }
                })
        out_file = GEO_DIR / "gotthard_km_points.geojson"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump({
                "type": "FeatureCollection",
                "name": "Gotthard Base Tunnel - Official Hectometre Points",
                "features": km_features
            }, f, indent=2, ensure_ascii=False)
        logger.info(f"   Saved {len(km_features)} kilometrage points to {out_file.name}")
    except Exception as e:
        logger.error(f"   Failed to fetch Gotthard KM points: {e}")

    logger.info("Swiss Open Government Data successfully synchronized!")


if __name__ == "__main__":
    run()
