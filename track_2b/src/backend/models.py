from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# ==============================================================================
# Bautagebuch & Regierapport (SIA 118) Schemas
# ==============================================================================

class BautagebuchRequest(BaseModel):
    raw_text: str = Field(..., description="Frontline note in Portuguese, Italian, Spanish, French, or German")
    author_name: Optional[str] = Field("Ouvrier de chantier", description="Name of supervisor or miner")
    author_role: Optional[str] = Field("Mineur / Chef de poste", description="Job title / role")
    location_pk: Optional[str] = Field(None, description="Kilometric point (e.g. PK 3.200) or sector")
    target_language: str = Field("de", description="Output official language: 'de' (German) or 'fr' (French)")


class RegierapportClaim(BaseModel):
    is_required: bool = Field(True, description="Whether unbudgeted work requires a formal Regierapport under SIA 118 Art. 44")
    sia_reference: str = Field("SIA 118 Art. 44-53", description="Contractual standard reference")
    claim_reason: str = Field(..., description="Justification of unforeseen work / force account")
    workforce_hours: List[Dict[str, Any]] = Field(default_factory=list, description="Hours breakdown per worker role")
    equipment_used: List[str] = Field(default_factory=list, description="Machinery mobilized")
    materials_used: List[str] = Field(default_factory=list, description="Consumables and materials deployed")


class BautagebuchResponse(BaseModel):
    date: str
    location_pk: str
    summary_fr: str
    summary_de: str
    events: List[str]
    delay_hours: float = 0.0
    regierapport: RegierapportClaim
    safety_hazard_detected: bool = False
    safety_rule_infraction: Optional[str] = None
    official_log_entry: str = Field(..., description="Formatted official journal entry ready to copy/print")


# ==============================================================================
# SUVA & BauAV Safety Audit Schemas
# ==============================================================================

class SuvaAuditRequest(BaseModel):
    description: Optional[str] = Field(None, description="Observation description or incident notes")
    image_base64: Optional[str] = Field(None, description="Base64 encoded JPEG/PNG inspection image")
    location_pk: Optional[str] = Field(None, description="Site location / sector")


class InfractedRule(BaseModel):
    rule_id: str
    norm: str
    title: str
    critical_risk: str
    corrective_action: str


class SuvaAuditResponse(BaseModel):
    status: str = Field(..., description="'compliant' | 'warning' | 'critical_danger'")
    stop_work_order: bool = Field(False, description="Whether immediate STOPP is required by SUVA")
    identified_hazards: List[str]
    infracted_rules: List[InfractedRule]
    immediate_actions: List[str]
    diagnostic_fr: str
    diagnostic_de: str


# ==============================================================================
# Infrastructure Decision Matrix (Pont vs Tunnel vs Tracé)
# ==============================================================================

class InfrastructureVariant(BaseModel):
    id: str
    name: str = Field(..., description="Nom de la variante d'emplacement ou de tracé (ex: Emplacement Nord - Plateau)")
    type: str = Field("surface", description="'surface' | 'tunnel' | 'bridge' | 'corridor' | 'site'")
    location_name: Optional[str] = Field(None, description="Nom du site géographique ou de la commune")
    coordinates: Optional[List[float]] = Field(None, description="[longitude, latitude] pour la cartographie")
    proximity_to_housing_m: Optional[int] = Field(500, description="Distance aux premières habitations en mètres")
    zoning_type: Optional[str] = Field("Zone mixte", description="Affectation du sol selon plan d'affectation LAT (SDA, habitat, industrie, forêt, ISOS)")
    estimated_cost_chf: float
    estimated_duration_months: int
    description: str


class InfrastructureDecisionRequest(BaseModel):
    project_name: str = Field("Implantation & Tracé Optimal d'Infrastructure", description="Nom du projet")
    location: str = Field("Canton du Valais / Uri / Vaud / Berne", description="Canton ou région")
    variants: List[InfrastructureVariant] = Field(default_factory=list)
    priorities: Dict[str, float] = Field(
        default_factory=lambda: {"cost": 0.25, "opposition_risk": 0.35, "environmental_impact": 0.25, "duration": 0.15}
    )


class VariantEvaluation(BaseModel):
    variant_id: str
    variant_name: str
    type: str
    location_name: Optional[str] = None
    coordinates: Optional[List[float]] = None
    cost_score: int
    opposition_risk_level: str
    estimated_litigation_delay_months: int
    environmental_score: int
    total_score: float
    key_legal_hurdles: List[str]
    pros: List[str]
    cons: List[str]
    mitigation_recommendations: List[str] = Field(default_factory=list)


class InfrastructureDecisionResponse(BaseModel):
    project_name: str
    recommended_variant: str
    optimal_location_name: Optional[str] = None
    optimal_coordinates: Optional[List[float]] = None
    decision_summary_fr: str
    decision_summary_de: str
    siting_tradeoff_analysis_fr: Optional[str] = None
    evaluations: List[VariantEvaluation]
    swiss_legal_basis: List[str]
    strategic_recommendation: str


# ==============================================================================
# Tender Comparison & Contractor Selection (SIA 118 / AIMP)
# ==============================================================================

class TenderBid(BaseModel):
    contractor_name: str
    total_price_chf: float
    duration_months: int
    experience_rating: int
    has_subcontractors: bool
    unforeseen_exclusion_clauses: List[str] = Field(default_factory=list)


class TenderComparisonRequest(BaseModel):
    lot_name: str = Field("Lot 101 - Génie Civil & Excavation", description="Intitulé du lot")
    owner_estimate_chf: float = Field(1500000.0, description="Devis estimatif du Maître d'Ouvrage")
    bids: List[TenderBid] = Field(default_factory=list)


class BidEvaluation(BaseModel):
    contractor_name: str
    price_deviation_pct: float
    is_abnormally_low: bool
    hidden_risk_flags: List[str]
    score_price: float
    score_quality: float
    score_timeline: float
    total_score: float


class TenderComparisonResponse(BaseModel):
    lot_name: str
    awarded_contractor: str
    award_rationale_fr: str
    award_rationale_de: str
    bids_analysis: List[BidEvaluation]
    contractual_recommendations: List[str]


# ==============================================================================
# Building Permit Opposition & Neighborhood Impact (LAT / OPB)
# ==============================================================================

class PermitOppositionRequest(BaseModel):
    project_title: str
    project_location: str
    opposition_raw_text: str = Field(..., description="Extrait du mémoire d'opposition du riverain")
    inquiry_deadline_days: int = 30


class QualifiedGrievance(BaseModel):
    category: str
    severity: str
    legal_basis: str
    claim_summary: str
    rebuttal_strategy: str


class PermitOppositionResponse(BaseModel):
    opposition_validity: str
    grievances: List[QualifiedGrievance]
    draft_rebuttal_letter_fr: str
    draft_rebuttal_letter_de: str
    estimated_delay_weeks: int

