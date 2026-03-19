"""Data models for The CISO Council.

All structured data flows through these pydantic models.
Personas, scenarios, responses, scores, and reports.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class RiskAppetite(int, Enum):
    """Risk appetite scale from ultra-conservative to aggressive."""
    ULTRA_CONSERVATIVE = 1
    CONSERVATIVE = 2
    MODERATE = 3
    TOLERANT = 4
    AGGRESSIVE = 5


class DecisionStyle(str, Enum):
    """How the persona approaches decisions."""
    DATA_DRIVEN = "data_driven"
    COMPLIANCE_FIRST = "compliance_first"
    RELATIONSHIP_FIRST = "relationship_first"
    COST_OPTIMISED = "cost_optimised"
    RISK_BALANCED = "risk_balanced"
    PRAGMATIC = "pragmatic"


class OrgContext(BaseModel):
    """Organisational context for a persona."""
    sector: str = Field(description="Industry sector, e.g. 'fintech', 'healthcare', 'banking'")
    size: str = Field(description="Organisation size, e.g. 'startup', 'mid-market', 'enterprise'")
    maturity: str = Field(description="GRC maturity level, e.g. 'early', 'developing', 'mature'")
    region: str = Field(default="global", description="Primary regulatory region")


class Persona(BaseModel):
    """A council member's persona definition."""
    id: str = Field(description="Unique identifier, e.g. 'ciso_fintech_startup'")
    title: str = Field(description="Role title, e.g. 'CISO'")
    name: str = Field(description="Fictional name for the persona")
    risk_appetite: RiskAppetite
    org_context: OrgContext
    regulatory_lens: list[str] = Field(
        description="Frameworks and regulations this persona prioritises, e.g. ['SOC 2', 'PCI DSS']"
    )
    decision_style: DecisionStyle
    background: str = Field(description="Brief professional background, 1-2 sentences")


class Scenario(BaseModel):
    """A GRC dilemma for the council to debate."""
    title: str
    domain: str = Field(description="Category: incident_response, risk_acceptance, vendor_risk, etc.")
    context: str = Field(description="Background situation, 2-4 sentences")
    dilemma: str = Field(description="The specific decision or question the council must address")
    constraints: list[str] = Field(
        default_factory=list,
        description="Real-world constraints: budget, timeline, regulatory deadlines, etc."
    )
    stakeholders: list[str] = Field(
        default_factory=list,
        description="Key stakeholders affected by the decision"
    )
    expected_dimensions: list[str] = Field(
        default_factory=list,
        description="What a good answer should address"
    )


class CouncilResponse(BaseModel):
    """A single council member's response to a scenario."""
    persona_id: str
    persona_title: str
    persona_name: str
    provider: str
    model: str
    response_text: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    latency_seconds: float = Field(default=0.0)
    error: Optional[str] = Field(default=None)


class DimensionScore(BaseModel):
    """Score for a single dimension of a response."""
    dimension: str
    score: float = Field(ge=0.0, le=10.0, description="Score from 0 to 10 (0 means scoring failed)")
    rationale: str = Field(description="Brief explanation for the score")


class ScoredResponse(BaseModel):
    """A council response with scoring attached."""
    response: CouncilResponse
    scores: list[DimensionScore]
    overall_score: float = Field(ge=0.0, le=10.0)


class ConsensusPoint(BaseModel):
    """A point where the council broadly agrees."""
    summary: str
    supporting_members: list[str]
    confidence: str = Field(description="high, moderate, or low")


class DissentPoint(BaseModel):
    """A point where one or more members diverge from the majority."""
    summary: str
    dissenting_members: list[str]
    majority_position: str
    dissent_rationale: str


class AmbiguityInsight(BaseModel):
    """What a disagreement reveals about the decision's complexity."""
    insight: str
    contributing_factors: list[str]


class CouncilReport(BaseModel):
    """The final output of a council session."""
    scenario: Scenario
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    responses: list[ScoredResponse]
    consensus: list[ConsensusPoint]
    dissent: list[DissentPoint]
    ambiguity_analysis: list[AmbiguityInsight]
    risk_appetite_distribution: dict[str, int] = Field(
        default_factory=dict,
        description="Distribution of risk appetites across council members"
    )
    top_recommendation: str = Field(
        default="",
        description="The single strongest recommendation from the council"
    )
    metadata: dict = Field(default_factory=dict)
