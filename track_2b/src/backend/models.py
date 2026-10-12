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
