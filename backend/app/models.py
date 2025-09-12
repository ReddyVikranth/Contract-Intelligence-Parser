from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ContractStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class PartyInfo(BaseModel):
    name: Optional[str] = None
    legal_entity: Optional[str] = None
    registration_details: Optional[str] = None
    signatories: Optional[List[str]] = None
    roles: Optional[List[str]] = None

class AccountInfo(BaseModel):
    billing_details: Optional[str] = None
    account_numbers: Optional[List[str]] = None
    contact_info: Optional[Dict[str, str]] = None

class FinancialDetails(BaseModel):
    line_items: Optional[List[Dict[str, Any]]] = None
    total_value: Optional[float] = None
    currency: Optional[str] = None
    tax_info: Optional[Dict[str, Any]] = None
    additional_fees: Optional[List[Dict[str, Any]]] = None

class PaymentStructure(BaseModel):
    payment_terms: Optional[str] = None
    due_dates: Optional[List[str]] = None
    payment_methods: Optional[List[str]] = None
    banking_details: Optional[Dict[str, str]] = None

class RevenueClassification(BaseModel):
    payment_type: Optional[str] = None  # recurring, one-time, both
    billing_cycle: Optional[str] = None
    renewal_terms: Optional[str] = None
    auto_renewal: Optional[bool] = None

class ServiceLevelAgreement(BaseModel):
    performance_metrics: Optional[List[str]] = None
    penalty_clauses: Optional[List[str]] = None
    support_terms: Optional[str] = None
    maintenance_terms: Optional[str] = None

class ExtractedData(BaseModel):
    party_identification: Optional[PartyInfo] = None
    account_information: Optional[AccountInfo] = None
    financial_details: Optional[FinancialDetails] = None
    payment_structure: Optional[PaymentStructure] = None
    revenue_classification: Optional[RevenueClassification] = None
    service_level_agreements: Optional[ServiceLevelAgreement] = None

class ConfidenceScores(BaseModel):
    financial_completeness: float = 0.0
    party_identification: float = 0.0
    payment_terms_clarity: float = 0.0
    sla_definition: float = 0.0
    contact_information: float = 0.0
    overall_score: float = 0.0

class GapAnalysis(BaseModel):
    missing_fields: List[str] = []
    incomplete_sections: List[str] = []
    recommendations: List[str] = []

class ContractResponse(BaseModel):
    contract_id: str
    filename: str
    file_size: int
    status: ContractStatus
    created_at: datetime
    updated_at: datetime
    progress_percentage: int = 0
    error_message: Optional[str] = None
    extracted_data: Optional[ExtractedData] = None
    confidence_scores: Optional[ConfidenceScores] = None
    gap_analysis: Optional[GapAnalysis] = None

class ContractUploadResponse(BaseModel):
    contract_id: str
    message: str
    status: ContractStatus

class ContractStatusResponse(BaseModel):
    contract_id: str
    status: ContractStatus
    progress_percentage: int
    error_message: Optional[str] = None

class ContractListResponse(BaseModel):
    contracts: List[ContractResponse]
    total: int
    page: int
    page_size: int
    total_pages: int