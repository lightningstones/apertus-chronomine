import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from openai import AsyncOpenAI
from src.backend.models import (
    BautagebuchRequest,
    BautagebuchResponse,
    RegierapportClaim,
    SuvaAuditRequest,
    SuvaAuditResponse,
    InfractedRule
)

logger = logging.getLogger("chronomine.provider")

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
KNOWLEDGE_PATH = BASE_DIR / "data" / "knowledge" / "suva_rules.json"


def load_suva_knowledge() -> List[Dict[str, Any]]:
    if KNOWLEDGE_PATH.exists():
        with open(KNOWLEDGE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("rules", [])
    return []


class ApertusProvider:
    def __init__(self):
        self.provider_mode = os.getenv("APERTUS_PROVIDER", "mock_offline").lower()
        self.base_url = os.getenv("APERTUS_BASE_URL", "https://api.inference.cscs.ch/v1")
        self.api_key = os.getenv("APERTUS_API_KEY", "")
        self.model = os.getenv("APERTUS_MODEL", "swiss-ai/Apertus-v1.5-8B")
        self.rules = load_suva_knowledge()

        if self.provider_mode in ("cscs", "ollama") and self.api_key:
            self.client = AsyncOpenAI(
                base_url=self.base_url,
                api_key=self.api_key or "not-needed-for-ollama"
            )
        else:
            self.client = None

    async def generate_bautagebuch(self, req: BautagebuchRequest) -> BautagebuchResponse:
        """Translates and structures frontline multilingual notes into official SIA 118 logs."""
        today = datetime.now().strftime("%Y-%m-%d")
        location = req.location_pk or "PK 3.200 (Galerie Nord)"

        if self.client and self.provider_mode == "cscs":
            try:
                system_prompt = (
                    "Tu es un ingénieur expert en génie civil souterrain suisse et norme SIA 118.\n"
                    "Transforme la note de chantier multilingue en un Bautagebuch officiel allemand ou français "
                    "avec bordereau de régie (Regierapport Art. 44).\n"
                    "Réponds exclusivement en format JSON correspondant au schéma attendu."
                )
                user_prompt = (
                    f"Auteur: {req.author_name} ({req.author_role})\n"
                    f"Localisation: {location}\n"
                    f"Langue cible: {req.target_language}\n"
                    f"Note brute: {req.raw_text}"
                )
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.2,
                )
                content = json.loads(response.choices[0].message.content)
                return BautagebuchResponse(**content)
            except Exception as e:
                logger.warning(f"Apertus CSCS error, falling back to sovereign offline engine: {e}")

        # Deterministic Sovereign Air-Gapped Fallback Engine
        raw_lower = req.raw_text.lower()

        # Detection heuristics
        delay_hours = 2.5 if ("2h" in raw_lower or "2h30" in raw_lower or "arrêt" in raw_lower or "paragem" in raw_lower) else 1.0
        is_water = "água" in raw_lower or "eau" in raw_lower or "wasser" in raw_lower or "lama" in raw_lower or "tubagem" in raw_lower
        is_rock = "roccia" in raw_lower or "rocha" in raw_lower or "fels" in raw_lower or "fissur" in raw_lower or "convergenza" in raw_lower

        if is_water:
            summary_de = "Schwerer Rohrbruch an der Hauptentwässerungsleitung bei PK 3.200. Wasser- und Schlammeinbruch. Arbeitsunterbruch 2.5 Stunden."
            summary_fr = "Rupture de la conduite de drainage principale au PK 3.200. Venue d'eau et de boue. Interruption de chantier de 2h30."
            events = [
                "14:15 - Rupture accidentelle conduite PE d200 lors du terrassement",
                "14:30 - Arrêt immédiat de la pelle mécanique et évacuation de la zone",
                "14:45 - Pompage d'urgence et curage de la boue accumulée",
                "16:45 - Rétablissement provisoire avec 4 sacs de ciment prompt et reprise"
            ]
            claim_reason = "Imprévu technique de chantier : Réparation d'urgence conduite de drainage non répertoriée et curage des boues."
            workforce = [
                {"role": "Machiniste / Operateur pelle", "hours": 2.5, "rate_chf": 115.0},
                {"role": "Mineur spécialisé (x2)", "hours": 5.0, "rate_chf": 95.0}
            ]
            equipment = ["Pelle mécanique Komatsu PC210 (2.5h)", "Pompe d'épuisement submersible Flygt (2.5h)"]
            materials = ["4 sacs de ciment à prise rapide (100 kg)", "Manchon de réparation PVC d200"]
            rule_infraction = "BauAV Art. 50 (Évacuation des eaux de chantier) & SIA 118 Art. 44"
        elif is_rock:
            summary_de = "Geologische Störzone bei PK 4.150 angetroffen. Erhöhter Gebirgsdruck und Gewölbedurchbiegung. Verstärkung des Ausbaus zwingend erforderlich."
            summary_fr = "Zone de faille géologique au PK 4.150. Poussée de terrain et convergence rapide. Renforcement immédiat du soutènement requis."
            events = [
                "Détection de roche friable et fissuration lors du marinage",
                "Mesure de convergence confirmant un resserrement de 15mm en 2h",
                "Manque de 4 ancrages radiaux par rapport au schéma de soutènement Classe III",
                "Arrêt du front et ordre de projection de béton fibré"
            ]
            claim_reason = "Imprévu géologique majeur (SIA 118/198) : Renforcement du profil d'excavation en classe de terrain dégradée."
            workforce = [
                {"role": "Chef mineur", "hours": 3.0, "rate_chf": 125.0},
                {"role": "Équipe de boulonnage (x3)", "hours": 9.0, "rate_chf": 95.0}
            ]
            equipment = ["Jumbo de foration Sandvik (3h)", "Machine à projeter le béton Meyco (2h)"]
            materials = ["4 boulons à friction Swellex Mn24", "6 m³ béton projeté C30/37 fibré acier"]
            rule_infraction = "SIA 198 / BauAV Art. 80 (Soutènement immédiat du front de taille)"
        else:
            summary_de = "Täglicher Arbeitsfortschritt im Stollen. Regiearbeiten nach SIA 118 Art. 44 erfasst."
            summary_fr = "Avancement quotidien des travaux. Prestations en régie consignées selon SIA 118 Art. 44."
            events = [f"Intervention documentée par {req.author_name} au {location}"]
            claim_reason = "Travaux d'adaptation imprévus sur ordre de la direction de travaux."
            workforce = [{"role": req.author_role or "Mineur", "hours": delay_hours, "rate_chf": 95.0}]
            equipment = ["Petit outillage de chantier"]
            materials = ["Consommables divers"]
            rule_infraction = None

        official_log = (
            f"=== BAUTAGEBUCH / JOURNAL DE CHANTIER (SIA 118) ===\n"
            f"Datum / Date : {today}\n"
            f"Ort / Localisation : {location}\n"
            f"Bauleiter / Responsable : {req.author_name} ({req.author_role})\n"
            f"Vorfälle / Événements : {summary_de if req.target_language == 'de' else summary_fr}\n"
            f"Unterbruch / Arrêt : {delay_hours} h\n"
            f"Regierapport SIA 118 Art. 44 : OUI (À soumettre pour visa)\n"
            f"====================================================="
        )

        return BautagebuchResponse(
            date=today,
            location_pk=location,
            summary_fr=summary_fr,
            summary_de=summary_de,
            events=events,
            delay_hours=delay_hours,
            regierapport=RegierapportClaim(
                is_required=True,
                sia_reference="SIA 118 Art. 44-53",
                claim_reason=claim_reason,
                workforce_hours=workforce,
                equipment_used=equipment,
                materials_used=materials
            ),
            safety_hazard_detected=True if rule_infraction else False,
            safety_rule_infraction=rule_infraction,
            official_log_entry=official_log
        )

    async def audit_suva_safety(self, req: SuvaAuditRequest) -> SuvaAuditResponse:
        """Audits an inspection image or field observation against Swiss SUVA/BauAV regulations."""
        desc = (req.description or "").lower()

        # Match against knowledge base rules
        infracted: List[InfractedRule] = []

        if "blindage" in desc or "fouille" in desc or "tranchée" in desc or "graben" in desc or "talus" in desc or "2m" in desc:
            r = next((x for x in self.rules if x["id"] == "BAUAV-ART-54"), None)
            if r:
                infracted.append(InfractedRule(
                    rule_id=r["id"],
                    norm=r["norm"],
                    title=r["title"],
                    critical_risk=r["critical_risk"],
                    corrective_action=r["corrective_action"]
                ))
            r_slope = next((x for x in self.rules if x["id"] == "BAUAV-ART-51"), None)
            if r_slope:
                infracted.append(InfractedRule(
                    rule_id=r_slope["id"],
                    norm=r_slope["norm"],
                    title=r_slope["title"],
                    critical_risk=r_slope["critical_risk"],
                    corrective_action=r_slope["corrective_action"]
                ))
        elif "gerüst" in desc or "échafaudage" in desc or "chute" in desc or "absturz" in desc or "garde-corps" in desc:
            r = next((x for x in self.rules if x["id"] == "BAUAV-ART-15"), None)
            if r:
                infracted.append(InfractedRule(
                    rule_id=r["id"],
                    norm=r["norm"],
                    title=r["title"],
                    critical_risk=r["critical_risk"],
                    corrective_action=r["corrective_action"]
                ))
        elif "ventil" in desc or "lueftung" in desc or "lüftung" in desc or "co" in desc or "gaz" in desc:
            r = next((x for x in self.rules if x["id"] == "BAUAV-ART-80"), None)
            if r:
                infracted.append(InfractedRule(
                    rule_id=r["id"],
                    norm=r["norm"],
                    title=r["title"],
                    critical_risk=r["critical_risk"],
                    corrective_action=r["corrective_action"]
                ))
        else:
            # Default tunnel face stability rule
            r = next((x for x in self.rules if x["id"] == "SIA-198-ROCK"), self.rules[0] if self.rules else None)
            if r:
                infracted.append(InfractedRule(
                    rule_id=r["id"],
                    norm=r["norm"],
                    title=r["title"],
                    critical_risk=r["critical_risk"],
                    corrective_action=r["corrective_action"]
                ))

        has_danger = len(infracted) > 0

        return SuvaAuditResponse(
            status="critical_danger" if has_danger else "compliant",
            stop_work_order=has_danger,
            identified_hazards=[f"Risque critique : {ir.critical_risk}" for ir in infracted],
            infracted_rules=infracted,
            immediate_actions=[ir.corrective_action for ir in infracted],
            diagnostic_fr=(
                f"AUDIT SUVA NÉGATIF — DANGER MORTEL IDENTIFIÉ : {len(infracted)} infraction(s) "
                f"aux prescriptions de la BauAV 2022. Arrêt immédiat des travaux prescrit selon SUVA 'STOPP bei Gefahr'."
            ),
            diagnostic_de=(
                f"SUVA SICHERHEITSAUDIT NEGATIV — LEBENSGEFAHR : {len(infracted)} Verstoss(e) "
                f"gegen die BauAV 2022 festgestellt. Sofortiger Arbeitsstopp gemäss 'STOPP bei Gefahr'."
            )
        )


apertus_engine = ApertusProvider()
