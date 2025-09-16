"""
Pydantic models for EDI X12 transactions in the insurance industry
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, date
from enum import Enum


class TransactionType(str, Enum):
    """Common insurance EDI transaction types"""
    CLAIMS_837 = "837"
    REMITTANCE_835 = "835"
    ENROLLMENT_834 = "834"
    ELIGIBILITY_270 = "270"
    ELIGIBILITY_RESPONSE_271 = "271"
    CLAIM_STATUS_276 = "276"
    CLAIM_STATUS_RESPONSE_277 = "277"


class Address(BaseModel):
    """Address information"""
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None


class Provider(BaseModel):
    """Healthcare provider information"""
    npi: Optional[str] = None
    name: Optional[str] = None
    address: Optional[Address] = None
    phone: Optional[str] = None
    tax_id: Optional[str] = None


class Patient(BaseModel):
    """Patient information"""
    member_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    address: Optional[Address] = None
    ssn: Optional[str] = None


class Diagnosis(BaseModel):
    """Diagnosis information"""
    code: str
    description: Optional[str] = None
    present_on_admission: Optional[str] = None


class Procedure(BaseModel):
    """Medical procedure information"""
    code: str
    description: Optional[str] = None
    modifier: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    total_amount: Optional[float] = None


class ClaimLine(BaseModel):
    """Individual claim line item"""
    line_number: int
    procedure: Procedure
    diagnosis_codes: List[str] = []
    service_date: Optional[date] = None
    place_of_service: Optional[str] = None
    units: Optional[float] = None


class Claim837(BaseModel):
    """837 Professional/Institutional Claims"""
    transaction_type: TransactionType = TransactionType.CLAIMS_837
    control_number: str
    submission_date: datetime
    provider: Provider
    patient: Patient
    diagnoses: List[Diagnosis] = []
    claim_lines: List[ClaimLine] = []
    total_charge_amount: Optional[float] = None
    claim_filing_indicator: Optional[str] = None
    patient_control_number: Optional[str] = None


class RemittanceLine(BaseModel):
    """835 Remittance advice line item"""
    claim_control_number: str
    line_number: Optional[int] = None
    procedure_code: Optional[str] = None
    paid_amount: Optional[float] = None
    adjustment_reason: Optional[str] = None
    adjustment_amount: Optional[float] = None


class Remittance835(BaseModel):
    """835 Remittance Advice"""
    transaction_type: TransactionType = TransactionType.REMITTANCE_835
    control_number: str
    creation_date: datetime
    payer_name: Optional[str] = None
    payer_id: Optional[str] = None
    provider: Provider
    total_paid_amount: Optional[float] = None
    remittance_lines: List[RemittanceLine] = []


class EnrollmentMember(BaseModel):
    """834 Enrollment member information"""
    member_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    ssn: Optional[str] = None
    effective_date: Optional[date] = None
    termination_date: Optional[date] = None
    coverage_level: Optional[str] = None


class Enrollment834(BaseModel):
    """834 Benefit Enrollment and Maintenance"""
    transaction_type: TransactionType = TransactionType.ENROLLMENT_834
    control_number: str
    creation_date: datetime
    sponsor_name: Optional[str] = None
    sponsor_id: Optional[str] = None
    members: List[EnrollmentMember] = []


class EDIConversionRequest(BaseModel):
    """Request model for EDI conversion"""
    x12_content: str = Field(..., description="Raw X12 EDI content to convert")
    transaction_type: Optional[TransactionType] = Field(None, description="Expected transaction type")
    validate_content: bool = Field(True, description="Whether to validate the X12 content")


class EDIConversionResponse(BaseModel):
    """Response model for EDI conversion"""
    success: bool
    transaction_type: Optional[TransactionType] = None
    json_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    validation_errors: List[str] = []
    processing_time_ms: Optional[float] = None
