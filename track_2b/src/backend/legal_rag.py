import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

from openai import AsyncOpenAI
from src.backend.models import (
    InfrastructureDecisionRequest,
    InfrastructureDecisionResponse,
    VariantEvaluation,
    InfrastructureVariant,
    TenderComparisonRequest,
    TenderComparisonResponse,
    BidEvaluation,
    TenderBid,
    PermitOppositionRequest,
    PermitOppositionResponse,
    QualifiedGrievance,
)
from src.backend.provider import apertus_engine

logger = logging.getLogger("chronomine.legal_rag")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
KNOWLEDGE_DIR = BASE_DIR / "data" / "knowledge"


class LegalDecisionEngine:
    """
    Swiss Infrastructure & Legal Decision Engine powered by Apertus v1.5-70B.
    Integrates Swiss Federal Laws (LAT RS 700, OPB RS 814.41, LPE RS 814.01, CC RS 210),
    BauAV 2022 (RS 832.311.141), SIA 118 / SIA 198 norms, and AIMP public procurement rules.
    """

    def __init__(self):
        self.bauav_data = self._load_json("fedlex_bauav_2022.json")
        self.sia_118_data = self._load_json("sia_118_articles.json")
        self.suva_rules = self._load_json("suva_vital_rules_underground.json")

    def _load_json(self, filename: str) -> Dict[str, Any]:
        p = KNOWLEDGE_DIR / filename
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load {filename}: {e}")
        return {}

    async def arbitrate_infrastructure(
        self, req: InfrastructureDecisionRequest
    ) -> InfrastructureDecisionResponse:
        """
        Multicriteria comparative arbitration for optimal infrastructure siting and alignment.
        Evaluates candidate geographic positions/variants across:
        1. Oppositions & Recours riverains (LAT Art. 33, OPB Art. 7, proximity to housing, zoning type)
        2. Prix & Coûts d'investissement (CapEx, acquisitions foncières, expropriations LAT Art. 5)
        3. Délais & Planning de réalisation (procédure d'enquête, conciliation, retards de litige)
        4. Impact sur le voisinage & Environnement (bruit nocturne OPB, protection SDA LAT 15, paysage ISOS/IFP)
        Identifies and recommends the optimal siting position (optimal_location_name, optimal_coordinates).
        """
        # If Apertus Live Client is configured, attempt LLM synthesis
        if apertus_engine.client and apertus_engine.provider_mode in ("swisscom", "cscs", "ollama"):
            try:
                system_prompt = (
                    "Tu es un ingénieur en chef et juriste en aménagement du territoire suisse (LAT, OPB, LPE, ISOS, Tribunal fédéral).\n"
                    "Tu aides un Maître d'Ouvrage (Bauherr) ou Développeur de projet à identifier l'EMPLACEMENT ou le TRACÉ OPTIMAL pour implanter une infrastructure.\n"
                    "Pour chaque site ou variante candidate, tu évalues rigoureusement les 4 piliers de décision suisses :\n"
                    "1. Oppositions & Recours juridiques (proximité des habitations riveraines, recours d'associations ou voisins sous LAT Art. 33, OPB Art. 7, ISOS, blocage au Tribunal administratif cantonal ou Tribunal fédéral).\n"
                    "2. Prix & Coûts d'investissement (CapEx, acquisitions foncières, expropriations LAT Art. 5, mesures de compensation).\n"
                    "3. Délais & Planning de réalisation (durée des enquêtes publiques, négociations de conciliation, retards suspensifs de litige, travaux).\n"
                    "4. Impact sur le voisinage & Environnement (bruit nocturne OPB, protection des surfaces d'assolement SDA LAT Art. 15, paysage ISOS/IFP, déblais LPE).\n\n"
                    "Tu dois désigner la position optimale (recommended_variant, optimal_location_name, optimal_coordinates) qui réconcilie au mieux ces 4 critères selon les priorités du maître d'ouvrage, et justifier le compromis (siting_tradeoff_analysis_fr).\n\n"
                    "Réponds STRICTEMENT sous format JSON respectant ce schéma exact:\n"
                    "{\n"
                    '  "project_name": "string",\n'
                    '  "recommended_variant": "string",\n'
                    '  "optimal_location_name": "string",\n'
                    '  "optimal_coordinates": [float, float],\n'
                    '  "decision_summary_fr": "string",\n'
                    '  "decision_summary_de": "string",\n'
                    '  "siting_tradeoff_analysis_fr": "string",\n'
                    '  "evaluations": [\n'
                    "    {\n"
                    '      "variant_id": "string",\n'
                    '      "variant_name": "string",\n'
                    '      "type": "surface|tunnel|bridge|corridor|site",\n'
                    '      "location_name": "string",\n'
                    '      "coordinates": [float, float],\n'
                    '      "cost_score": int (0-100),\n'
                    '      "opposition_risk_level": "Faible|Moyen|Élevé|Critique",\n'
                    '      "estimated_litigation_delay_months": int,\n'
                    '      "environmental_score": int (0-100),\n'
                    '      "total_score": float (0-100),\n'
                    '      "key_legal_hurdles": ["string"],\n'
                    '      "pros": ["string"],\n'
                    '      "cons": ["string"],\n'
                    '      "mitigation_recommendations": ["string"]\n'
                    "    }\n"
                    "  ],\n"
                    '  "swiss_legal_basis": ["string"],\n'
                    '  "strategic_recommendation": "string"\n'
                    "}"
                )
                user_prompt = (
                    f"Projet: {req.project_name} ({req.location})\n"
                    f"Pondérations: {req.priorities}\n"
                    f"Variantes et sites candidats: {json.dumps([v.model_dump() for v in req.variants], ensure_ascii=False)}"
                )
                response = await apertus_engine.client.chat.completions.create(
                    model=apertus_engine.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.15,
                    max_tokens=2500,
                )
                raw = response.choices[0].message.content or ""
                clean_json = raw.strip()
                if "```json" in clean_json:
                    clean_json = clean_json.split("```json")[1].split("```")[0].strip()
                elif "```" in clean_json:
                    clean_json = clean_json.split("```")[1].split("```")[0].strip()
                data = json.loads(clean_json)
                data["project_name"] = req.project_name
                return InfrastructureDecisionResponse(**data)
            except Exception as e:
                logger.warning(f"Apertus live arbitration error ({e}), switching to sovereign rule-based model.")

        # Deterministic sovereign analysis based on Swiss legal precedents (LAT / OPB / ISOS / LPE)
        weights = req.priorities or {"cost": 0.25, "opposition_risk": 0.35, "environmental_impact": 0.25, "duration": 0.15}
        evaluations: List[VariantEvaluation] = []

        # Find min and max costs for normalization
        costs = [v.estimated_cost_chf for v in req.variants] or [1.0]
        min_cost, max_cost = min(costs), max(costs)
        durations = [v.estimated_duration_months for v in req.variants] or [1]
        min_dur, max_dur = min(durations), max(durations)

        for v in req.variants:
            v_type = (v.type or "surface").lower()
            proximity = v.proximity_to_housing_m if v.proximity_to_housing_m is not None else 500
            zoning = (v.zoning_type or "Zone mixte").lower()

            # Cost score (cheaper gets higher score)
            if max_cost > min_cost:
                cost_score = int(100 - ((v.estimated_cost_chf - min_cost) / (max_cost - min_cost)) * 60)
            else:
                cost_score = 75

            # Duration score
            if max_dur > min_dur:
                dur_score = int(100 - ((v.estimated_duration_months - min_dur) / (max_dur - min_dur)) * 50)
            else:
                dur_score = 70

            hurdles: List[str] = []
            pros: List[str] = []
            cons: List[str] = []
            mitigations: List[str] = []

            # 1. Opposition risk & litigation delay derived from proximity, zoning, and type
            if proximity < 250:
                opp_level = "Élevé"
                litigation_months = 24
                hurdles.append("OPB Art. 7 & 25 : Dépassement prévisible des valeurs limites d'immission nocturnes (< 250m des habitations)")
                cons.append(f"Forte proximité résidentielle ({proximity}m) générant un risque massif d'oppositions riveraines")
                mitigations.append("Implantation d'écrans acoustiques absorbants haute performance et limitation de vitesse nocturne")
            elif proximity <= 600:
                opp_level = "Moyen"
                litigation_months = 14
                cons.append(f"Distance modérée aux habitations ({proximity}m), concertation publique préalable indispensable")
                mitigations.append("Convention de servitudes et mesures de compensation antibruit avec la commune")
            else:
                opp_level = "Faible"
                litigation_months = 6
                pros.append(f"Éloignement protecteur des habitations ({proximity}m), minimisant le risque de plaintes pour nuisances")

            # 2. Zoning impact (LAT Art. 15 SDA, ISOS, zone industrielle)
            if "sda" in zoning or "agricole" in zoning:
                hurdles.append("LAT Art. 15 & 30 : Consommation de surfaces d'assolement (SDA) sous contingent fédéral strict")
                cons.append("Obligation de compensation surfacique 1:1 pour les parcelles agricoles protégées déclassées")
                mitigations.append("Accord de compensation foncière avec la Chambre cantonale d'agriculture")
                if opp_level == "Faible":
                    opp_level = "Moyen"
                litigation_months = max(litigation_months, 18)
            elif "isos" in zoning or "paysage" in zoning or "protég" in zoning:
                hurdles.append("ISOS (Inventaire fédéral des sites construits) : Atteinte au paysage d'importance nationale")
                cons.append("Risque élevé de recours associatif devant le Tribunal cantonal et le Tribunal fédéral")
                mitigations.append("Mandat d'étude parallèle (MEP) et intégration paysagère supervisée par la commission des monuments")
                opp_level = "Critique" if opp_level == "Élevé" else "Élevé"
                litigation_months = max(litigation_months, 28)
            elif "industri" in zoning or "activit" in zoning or "ferroviaire" in zoning:
                pros.append("Affectation conforme au plan de zones communal : absence d'incompatibilité d'usage")
                mitigations.append("Coordination standard avec les réseaux industriels existants")
                if opp_level in ("Élevé", "Moyen"):
                    opp_level = "Faible" if opp_level == "Moyen" else "Moyen"
                    litigation_months = max(6, litigation_months - 6)

            # 3. Infrastructure type specificities
            if "bridge" in v_type or "pont" in v_type:
                hurdles.append("LAT Art. 33 : Recours de riverains contre la covisibilité de l'ouvrage d'art et le bruit aérien")
                pros.append("Emprise foncière au sol réduite aux piles d'appui")
                cons.append("Maintenance anticorrosion et exposition aux intempéries (gel, verglas, vent)")
                env_score = 55 if "isos" not in zoning else 35
                if opp_level == "Faible":
                    opp_level = "Moyen"
            elif "tunnel" in v_type or "souterrain" in v_type:
                hurdles.append("LPE Art. 30 & BauAV 2022 : Plan cantonal de valorisation et de mise en décharge des déblais rocheux")
                pros.append("Suppression totale des nuisances sonores de surface et préservation intégrale du site")
                pros.append("Exploitation pérenne 365 j/an à l'abri des risques naturels de surface (chutes de pierres, neige)")
                cons.append("Investissement CapEx initial plus élevé et aléas géologiques résiduels sous roche")
                mitigations.append("Valorisation circulaire des matériaux d'excavation pour remblais ferroviaires")
                env_score = 88
                # Underground siting drastically reduces neighbor opposition
                opp_level = "Faible"
                litigation_months = min(litigation_months, 8)
            else:
                # Surface / corridor
                hurdles.append("LAT Art. 33 : Risque de blocage juridique pour fragmentation du territoire communal")
                pros.append("Facilité d'accès pour les phases de terrassement et coût kilométrique standard")
                cons.append("Coupure spatiale et fragmentation des continuités écologiques et agricoles")
                env_score = 45 if "sda" not in zoning else 30

            hurdles.append("LAT Art. 33 : Risque de recours suspensif devant le Tribunal administratif cantonal et le Tribunal fédéral")

            # Calculate opposition numeric score
            opp_score_map = {"Faible": 90, "Moyen": 65, "Élevé": 40, "Critique": 15}
            opp_num = opp_score_map.get(opp_level, 50)

            total_score = round(
                (cost_score * weights.get("cost", 0.25))
                + (opp_num * weights.get("opposition_risk", 0.35))
                + (env_score * weights.get("environmental_impact", 0.25))
                + (dur_score * weights.get("duration", 0.15)),
                1,
            )

            evaluations.append(
                VariantEvaluation(
                    variant_id=v.id,
                    variant_name=v.name,
                    type=v.type,
                    location_name=v.location_name or v.name,
                    coordinates=v.coordinates,
                    cost_score=cost_score,
                    opposition_risk_level=opp_level,
                    estimated_litigation_delay_months=litigation_months,
                    environmental_score=env_score,
                    total_score=total_score,
                    key_legal_hurdles=hurdles,
                    pros=pros,
                    cons=cons,
                    mitigation_recommendations=mitigations,
                )
            )

        # Sort evaluations by total_score descending
        evaluations.sort(key=lambda x: x.total_score, reverse=True)
        best = evaluations[0] if evaluations else None
        recommended = best.variant_name if best else "Variante A"
        opt_loc = best.location_name if best else None
        opt_coords = best.coordinates if best else None

        # Build detailed tradeoff analysis
        tradeoff_analysis = (
            f"L'arbitrage multicritères désigne l'emplacement '{recommended}'"
            + (f" ({opt_loc})" if opt_loc and opt_loc != recommended else "")
            + f" comme la position optimale avec une note globale de {best.total_score if best else 0}/100. "
            f"Ce choix présente un risque d'oppositions riveraines '{best.opposition_risk_level if best else 'Faible'}' "
            f"(délai d'instruction juridique estimé à {best.estimated_litigation_delay_months if best else 0} mois), "
            f"ce qui offre le meilleur compromis suisse entre coût d'investissement, célérité d'autorisation LAT et impact environnemental."
        )

        return InfrastructureDecisionResponse(
            project_name=req.project_name,
            recommended_variant=recommended,
            optimal_location_name=opt_loc,
            optimal_coordinates=opt_coords,
            decision_summary_fr=(
                f"L'optimisation d'implantation désigne la variante '{recommended}' comme la position optimale. "
                f"Ce positionnement garantit le meilleur équilibre entre acceptabilité riveraine (LAT/OPB), "
                f"sécurisation des délais de recours au Tribunal fédéral et maîtrise du budget global."
            ),
            decision_summary_de=(
                f"Die multikriterielle Standortoptimierung bestimmt die Variante '{recommended}' als optimalen Standort. "
                f"Diese Positionierung sichert das beste Gleichgewicht zwischen Nachbarschaftsakzeptanz (RPG/LSV), "
                f"Planungssicherheit vor Bundesgericht und Gesamtinvestition."
            ),
            siting_tradeoff_analysis_fr=tradeoff_analysis,
            evaluations=evaluations,
            swiss_legal_basis=[
                "LAT (RS 700) - Loi fédérale sur l'aménagement du territoire (Art. 3, 15, 33)",
                "OPB (RS 814.41) - Ordonnance sur la protection contre le bruit (Art. 7, 25 & Valeurs limites)",
                "LPE (RS 814.01) - Loi sur la protection de l'environnement (Valorisation des déblais)",
                "ISOS - Inventaire fédéral des sites construits d'importance nationale",
                "SIA 198 (2004) - Norme suisse pour les travaux souterrains et excavation"
            ],
            strategic_recommendation=(
                "Privilégier la variante recommandée en engageant immédiatement la concertation préalable "
                "avec la commune et les riverains. Préparer le dossier d'impact sur l'environnement (EIE) et le plan de gestion "
                "des déblais pour purger tout motif de recours avant la mise à l'enquête publique formelle."
            ),
        )

    async def compare_tender_bids(self, req: TenderComparisonRequest) -> TenderComparisonResponse:
        """
        Analyzes contractor tender bids according to SIA 118 (Art. 4, 24, 38, 44) & AIMP public procurement.
        Detects abnormally low prices, hidden exclusion clauses, and ranks bidders.
        """
        if apertus_engine.client and apertus_engine.provider_mode in ("swisscom", "cscs", "ollama"):
            try:
                system_prompt = (
                    "Tu es un ingénieur expert en adjudication de marchés publics suisses (AIMP, norme SIA 118).\n"
                    "Tu compares les offres d'entrepreneurs pour le compte d'un Maître d'Ouvrage (Bauherr).\n"
                    "Détecte les offres anormalement basses (>15% sous devis), les clauses de réserve géologiques abusives, "
                    "et classe les offres selon le meilleur rapport qualité-prix suisse (adjudication de l'offre la plus avantageuse).\n"
                    "Réponds STRICTEMENT sous format JSON respectant ce schéma exact:\n"
                    "{\n"
                    '  "lot_name": "string",\n'
                    '  "awarded_contractor": "string",\n'
                    '  "award_rationale_fr": "string",\n'
                    '  "award_rationale_de": "string",\n'
                    '  "bids_analysis": [\n'
                    "    {\n"
                    '      "contractor_name": "string",\n'
                    '      "price_deviation_pct": float,\n'
                    '      "is_abnormally_low": bool,\n'
                    '      "hidden_risk_flags": ["string"],\n'
                    '      "score_price": float,\n'
                    '      "score_quality": float,\n'
                    '      "score_timeline": float,\n'
                    '      "total_score": float\n'
                    "    }\n"
                    "  ],\n"
                    '  "contractual_recommendations": ["string"]\n'
                    "}"
                )
                user_prompt = (
                    f"Lot: {req.lot_name}\n"
                    f"Devis estimatif MO: {req.owner_estimate_chf} CHF\n"
                    f"Offres: {json.dumps([b.model_dump() for b in req.bids], ensure_ascii=False)}"
                )
                response = await apertus_engine.client.chat.completions.create(
                    model=apertus_engine.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.1,
                    max_tokens=2200,
                )
                raw = response.choices[0].message.content or ""
                clean_json = raw.strip()
                if "```json" in clean_json:
                    clean_json = clean_json.split("```json")[1].split("```")[0].strip()
                elif "```" in clean_json:
                    clean_json = clean_json.split("```")[1].split("```")[0].strip()
                data = json.loads(clean_json)
                data["lot_name"] = req.lot_name
                return TenderComparisonResponse(**data)
            except Exception as e:
                logger.warning(f"Apertus live tender comparison error ({e}), switching to sovereign engine.")

        # Deterministic sovereign analysis
        bids_eval: List[BidEvaluation] = []
        estimate = req.owner_estimate_chf or 1.0

        for b in req.bids:
            deviation_pct = round(((b.total_price_chf - estimate) / estimate) * 100, 1)
            is_abnormally_low = deviation_pct <= -18.0

            flags: List[str] = []
            if is_abnormally_low:
                flags.append("Alerte AIMP/SIA 118 : Prix anormalement bas (>18% sous le devis). Risque de surcoûts en régie Art. 44.")
            if b.unforeseen_exclusion_clauses:
                for cl in b.unforeseen_exclusion_clauses:
                    flags.append(f"Clause restrictive : {cl}")
            if b.has_subcontractors:
                flags.append("Recours à la sous-traitance : exiger la liste des sous-traitants agréés selon SIA 118 Art. 29.")

            # Scoring: Price (ideal is between -10% and +5%)
            if is_abnormally_low:
                score_price = 45.0  # Penalized for dumping / risk of claim
            elif -15.0 <= deviation_pct <= 0.0:
                score_price = 95.0
            elif 0.0 < deviation_pct <= 10.0:
                score_price = 85.0
            else:
                score_price = max(20.0, 80.0 - abs(deviation_pct))

            score_quality = min(100.0, b.experience_rating * 20.0)
            score_timeline = 85.0 if b.duration_months <= 24 else 70.0

            total = round((score_price * 0.45) + (score_quality * 0.35) + (score_timeline * 0.20), 1)

            bids_eval.append(
                BidEvaluation(
                    contractor_name=b.contractor_name,
                    price_deviation_pct=deviation_pct,
                    is_abnormally_low=is_abnormally_low,
                    hidden_risk_flags=flags,
                    score_price=score_price,
                    score_quality=score_quality,
                    score_timeline=score_timeline,
                    total_score=total,
                )
            )

        bids_eval.sort(key=lambda x: x.total_score, reverse=True)
        winner = bids_eval[0].contractor_name if bids_eval else "Aucun soumissionnaire"

        return TenderComparisonResponse(
            lot_name=req.lot_name,
            awarded_contractor=winner,
            award_rationale_fr=(
                f"L'entreprise '{winner}' présente l'offre la plus avantageuse économiquement selon les critères SIA 118 & AIMP. "
                f"Son prix est équilibré par rapport au devis estimatif du Maître d'Ouvrage, sans risque d'éviction par dumping, "
                f"et ses garanties techniques et de solvabilité sont conformes aux exigences du cahier des charges."
            ),
            award_rationale_de=(
                f"Die Unternehmung '{winner}' legt das wirtschaftlich günstigste Angebot gemäss SIA 118 und BöB/IVöB vor. "
                f"Der Preis ist marktgerecht kalkuliert ohne unzulässiges Preisdumping, und die Qualitätsnachweise "
                f"erfüllen die Anforderungen des Bauherrn vollumfänglich."
            ),
            bids_analysis=bids_eval,
            contractual_recommendations=[
                "Intégrer expressément la norme SIA 118 (Édition 2013) comme partie intégrante du contrat d'entreprise.",
                "Neutraliser par avenant préalable toute tentative d'exclusion de l'Art. 58 SIA 118 (Responsabilité du sol et des imprévus géologiques).",
                "Fixer une garantie bancaire de bonne exécution de 10% (SIA 118 Art. 111) et exiger l'engagement formel sur le respect des CCT locales.",
                "Établir un barème d'heures de régie forfaitisé (Art. 44) pour désamorcer les demandes d'avenants imprévus."
            ],
        )

    async def evaluate_permit_opposition(
        self, req: PermitOppositionRequest
    ) -> PermitOppositionResponse:
        """
        Analyzes neighbor/association building permit oppositions under Swiss Planning & Environmental Laws
        (LAT RS 700, OPB RS 814.41, CC RS 210 Art. 679/684). Provides qualified rebuttal strategy and formal letters.
        """
        if apertus_engine.client and apertus_engine.provider_mode in ("swisscom", "cscs", "ollama"):
            try:
                system_prompt = (
                    "Tu es un avocat spécialisé en droit suisse des constructions, de l'aménagement du territoire (LAT RS 700) "
                    "et de la protection de l'environnement (OPB RS 814.41, LPE RS 814.01).\n"
                    "Tu analyses le mémoire d'opposition d'un voisin contre un projet d'infrastructure ou de bâtiment.\n"
                    "Qualifie chaque grief, cite les articles de lois suisses applicables, détermine les chances de succès, "
                    "et rédige un projet de lettre de conciliation et levée d'opposition formel et courtois.\n"
                    "Réponds STRICTEMENT sous format JSON respectant ce schéma exact:\n"
                    "{\n"
                    '  "opposition_validity": "Irrecevable|Partiellement recevable|Recevable avec conditions",\n'
                    '  "grievances": [\n'
                    "    {\n"
                    '      "category": "Bruit|Gabarit & Hauteur|Ensoleillement|Circulation|Environnement",\n'
                    '      "severity": "Faible|Moyenne|Majeure",\n'
                    '      "legal_basis": "string",\n'
                    '      "claim_summary": "string",\n'
                    '      "rebuttal_strategy": "string"\n'
                    "    }\n"
                    "  ],\n"
                    '  "draft_rebuttal_letter_fr": "string",\n'
                    '  "draft_rebuttal_letter_de": "string",\n'
                    '  "estimated_delay_weeks": int\n'
                    "}"
                )
                user_prompt = (
                    f"Projet: {req.project_title} ({req.project_location})\n"
                    f"Délai d'enquête: {req.inquiry_deadline_days} jours\n"
                    f"Texte de l'opposition reçue:\n{req.opposition_raw_text}"
                )
                response = await apertus_engine.client.chat.completions.create(
                    model=apertus_engine.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.15,
                    max_tokens=2500,
                )
                raw = response.choices[0].message.content or ""
                clean_json = raw.strip()
                if "```json" in clean_json:
                    clean_json = clean_json.split("```json")[1].split("```")[0].strip()
                elif "```" in clean_json:
                    clean_json = clean_json.split("```")[1].split("```")[0].strip()
                data = json.loads(clean_json)
                return PermitOppositionResponse(**data)
            except Exception as e:
                logger.warning(f"Apertus live opposition evaluation error ({e}), switching to sovereign engine.")

        # Sovereign deterministic analysis
        text_lower = req.opposition_raw_text.lower()
        grievances: List[QualifiedGrievance] = []

        if any(w in text_lower for w in ["bruit", "lärm", "décibel", "decibel", "nuisance sonore", "chantier nuit"]):
            grievances.append(
                QualifiedGrievance(
                    category="Bruit de chantier & Exploitation",
                    severity="Moyenne",
                    legal_basis="OPB (RS 814.41) Art. 7 & Directive fédérale sur le bruit de chantier de l'OFEV",
                    claim_summary="Allégation de dépassement des valeurs limites d'immission sonores et nuisances nocturnes.",
                    rebuttal_strategy=(
                        "Produire l'attestation de conformité du concept acoustique, engagement formel à respecter "
                        "l'horaire 07h00-12h00 / 13h15-18h00 sans travaux bruyants le samedi/dimanche, et mise en place de capteurs de suivi sonométrique."
                    ),
                )
            )

        if any(w in text_lower for w in ["hauteur", "gabarit", "vue", "ensoleillement", "ombre", "abstand", "höhe", "distance"]):
            grievances.append(
                QualifiedGrievance(
                    category="Gabarits, Hauteur & Ensoleillement",
                    severity="Faible",
                    legal_basis="Code Civil Suisse (CC RS 210) Art. 679/684 & Loi cantonale sur les constructions (LConst)",
                    claim_summary="Contestation de l'impact volumétrique et perte prétendue d'ensoleillement sur les parcelles voisines.",
                    rebuttal_strategy=(
                        "Démontrer que le projet s'inscrit rigoureusement à l'intérieur des gabarits réglementaires et des distances aux limites "
                        "définies par le plan d'affectation communal (PGA). Joindre l'étude d'ombrage solaire aux équinoxes."
                    ),
                )
            )

        if any(w in text_lower for w in ["trafic", "camion", "circulation", "verkehr", "lkw", "sécurité piéton", "stationnement"]):
            grievances.append(
                QualifiedGrievance(
                    category="Circulation & Sécurité routière",
                    severity="Moyenne",
                    legal_basis="Loi fédérale sur la circulation routière (LCR RS 741.01) & Normes VSS 640",
                    claim_summary="Inquiétudes quant à la saturation du réseau de quartier par les poids lourds d'évacuation des déblais.",
                    rebuttal_strategy=(
                        "Fournir le concept de gestion du trafic de chantier (plan de circulation à sens unique, "
                        "évacuation hors des heures de ramassage scolaire, régulateurs de trafic agréés aux carrefours clés)."
                    ),
                )
            )

        if not grievances:
            grievances.append(
                QualifiedGrievance(
                    category="Conformité générale d'aménagement",
                    severity="Faible",
                    legal_basis="LAT (RS 700) Art. 22 (Conditions d'autorisation de construire)",
                    claim_summary="Opposition de principe sans démonstration de violation d'une norme de protection des tiers.",
                    rebuttal_strategy=(
                        "Rappeler la conformité absolue à la zone d'affectation et conclure au rejet pour défaut d'intérêt digne de protection."
                    ),
                )
            )

        draft_letter_fr = (
            f"Monsieur le Président de la Commission des constructions,\n\n"
            f"En réponse à l'opposition formée par les riverains à l'encontre du projet '{req.project_title}' sis à {req.project_location}, "
            f"nous avons l'honneur de vous exposer nos déterminations.\n\n"
            f"Le projet respecte scrupuleusement les prescriptions du plan d'affectation communal ainsi que les normes fédérales (OPB, LAT). "
            f"Afin de lever les inquiétudes des opposants, le Maître d'Ouvrage a d'ores et déjà intégré des mesures concrètes d'atténuation :\n"
            f"- Respect strict des horaires de chantier de l'OFEV et monitoring acoustique permanent.\n"
            f"- Plan de circulation optimisé pour canaliser les poids lourds hors des zones sensibles.\n\n"
            f"Au vu de ces éléments, nous vous prions de bien vouloir convoquer les parties à une séance de conciliation "
            f"ou, à défaut d'accord, de lever formellement l'opposition et de délivrer le permis de construire sollicité.\n\n"
            f"Veuillez agréer, Monsieur le Président, l'expression de nos salutations distinguées.\n\n"
            f"-- Pour le Maître d'Ouvrage / Direction de projet"
        )

        draft_letter_de = (
            f"An die Baukommission der Gemeinde {req.project_location},\n\n"
            f"Bezugnehmend auf die Einsprache gegen das Bauvorhaben '{req.project_title}' nehmen wir wie folgt Stellung:\n\n"
            f"Das Baugesuch entspricht in allen Teilen der Bau- und Zonenordnung sowie den übergeordneten eidgenössischen Bestimmungen (RPG, LSV). "
            f"Zur Wahrung der Nachbarschaftsinteressen werden verbindliche Schallschutzmassnahmen gemäss Baurichtlinie Lärm BAFU sowie "
            f"ein Baustellenverkehrskonzept umgesetzt.\n\n"
            f"Wir beantragen daher höflich, die Einsprache im Rahmen der Einigungsverhandlung gütlich beizulegen "
            f"oder diese vollumfänglich abzuweisen und die Baubewilligung zu erteilen.\n\n"
            f"Mit freundlichen Grüssen,\n"
            f"-- Im Auftrag der Bauherrschaft"
        )

        return PermitOppositionResponse(
            opposition_validity="Partiellement recevable (conciliation recommandée)",
            grievances=grievances,
            draft_rebuttal_letter_fr=draft_letter_fr,
            draft_rebuttal_letter_de=draft_letter_de,
            estimated_delay_weeks=6,
        )


swiss_decision_engine = LegalDecisionEngine()
