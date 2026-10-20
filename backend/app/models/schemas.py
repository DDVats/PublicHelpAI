"""
Pydantic models for API request/response schemas.
"""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl


class UserProfile(BaseModel):
    state: Optional[str] = None
    age: Optional[int] = Field(None, ge=0, le=120)
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    caste_category: Optional[str] = Field(None, pattern="^(SC|ST|OBC|EWS|General)$")
    annual_income: Optional[int] = Field(None, ge=0)
    is_rural: Optional[bool] = None
    education: Optional[str] = None
    occupation: Optional[str] = None
    goals: Optional[list[str]] = None
    documents: Optional[list[str]] = None


class SearchFilters(BaseModel):
    state: Optional[str] = None
    level: Optional[str] = None
    category: Optional[str] = None


class RecommendRequest(BaseModel):
    query: str = Field("", max_length=500)
    profile: Optional[UserProfile] = None
    filters: Optional[SearchFilters] = None
    top_k: int = Field(10, ge=1, le=50)
    page: int = Field(1, ge=1)


class EligibilityInfo(BaseModel):
    status: str
    score: float
    matched_rules: list[str]
    failed_rules: list[str]
    unknown_rules: list[str]
    explanation: str


class SchemeCard(BaseModel):
    id: int
    name: str
    slug: str
    level: str
    state_ministry: str
    categories_raw: Optional[str]
    description: str
    benefits: str
    official_link: str
    myscheme_url: str
    eligibility: EligibilityInfo
    ranking_score: float
    semantic_score: float
    data_completeness_score: float
    required_documents: Optional[list[str]] = Field(default_factory=list)
    cross_encoder_score: Optional[float] = None
    why_recommended: Optional[list[str]] = Field(default_factory=list)
    rrf_score: Optional[float] = None


class SchemeDetail(BaseModel):
    id: int
    name: str
    slug: str
    level: str
    state_ministry: str
    categories_raw: Optional[str]
    categories_list: Optional[list[str]]
    description: str
    eligibility_text: str
    eligibility_general: Optional[str]
    exclusions_text: Optional[str]
    benefits: str
    application_process: str
    documents_required: Optional[str]
    faqs: Optional[str]
    official_link: str
    myscheme_url: str
    application_mode: Optional[str]
    source_dataset: str
    ingested_at: str
    verified: bool
    data_completeness_score: float
    required_documents: Optional[list[str]] = Field(default_factory=list)


class RecommendResponse(BaseModel):
    total: int
    page: int
    page_size: int
    query: str
    results: list[SchemeCard]
    has_embeddings: bool
    model_used: str


class QARequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)


class QAAnswer(BaseModel):
    scheme_id: int
    scheme_name: str
    snippet: str
    official_link: str
    myscheme_url: str
    relevance_score: float


class QAResponse(BaseModel):
    query: str
    answers: list[QAAnswer]
    note: str


class StatsResponse(BaseModel):
    total_schemes: int
    central_schemes: int
    state_schemes: int
    total_states_uts: int
    top_states: dict[str, int]
    has_embeddings: bool
    has_tfidf: bool


class SavedScheme(BaseModel):
    scheme_id: int
    session_id: str


class CompareRequest(BaseModel):
    scheme_ids: list[int] = Field(..., min_length=2, max_length=5)
    profile: Optional[UserProfile] = None


class SimilarSchemeItem(BaseModel):
    id: int
    name: str
    slug: str
    level: str
    state_ministry: str
    categories_raw: Optional[str] = None
    description: str
    benefits: str
    similarity_score: float
    match_pct: float
    shared_categories: list[str] = Field(default_factory=list)
    official_link: str
    myscheme_url: str
    required_documents: list[str] = Field(default_factory=list)


class BundleSchemeItem(BaseModel):
    id: int
    name: str
    slug: str
    level: str
    state_ministry: str
    benefit_role: str
    rationale: str
    eligibility: EligibilityInfo
    official_link: str
    myscheme_url: str
    required_documents: list[str] = Field(default_factory=list)


class ComplementaryBundle(BaseModel):
    bundle_id: str
    title: str
    description: str
    target_persona: str
    icon: str
    schemes: list[BundleSchemeItem]


class PersonaItem(BaseModel):
    persona_id: str
    name: str
    tagline: str
    avatar: str
    description: str
    profile: UserProfile


class FeedRequest(BaseModel):
    profile: Optional[UserProfile] = None
    saved_ids: Optional[list[int]] = Field(default_factory=list)
    top_k: int = Field(8, ge=1, le=50)


class PersonalizedFeedResponse(BaseModel):
    top_matches: list[SchemeCard]
    bundles: list[ComplementaryBundle]
    similar_to_saved: list[SchemeCard]
    state_spotlight: list[SchemeCard]
    algorithm_info: dict
    active_profile_summary: Optional[str] = None

