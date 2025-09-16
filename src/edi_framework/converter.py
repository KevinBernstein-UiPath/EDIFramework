"""
EDI X12 to JSON Converter for Insurance Industry
"""

import json
import time
from typing import Dict, Any, Optional
from .x12_parser import X12Parser
from .models import (
    TransactionType, EDIConversionRequest, EDIConversionResponse,
    Claim837, Remittance835, Enrollment834, Provider, Patient, Address,
    Diagnosis, Procedure, ClaimLine, RemittanceLine, EnrollmentMember
)


class EDIConverter:
    """Main converter class for EDI X12 to JSON transformations"""
    
    def __init__(self):
        self.parser = X12Parser()
    
    def convert_to_json(self, request: EDIConversionRequest) -> EDIConversionResponse:
        """Convert X12 EDI content to JSON format"""
        start_time = time.time()
        
        try:
            # Validate X12 content if requested
            if request.validate_content:
                validation_result = self.validate_x12(request.x12_content)
                if not validation_result["valid"]:
                    return EDIConversionResponse(
                        success=False,
                        error_message="X12 validation failed: " + "; ".join(validation_result["errors"]),
                        validation_errors=validation_result["errors"],
                        processing_time_ms=(time.time() - start_time) * 1000
                    )
            
            # Parse X12 content
            parsed_data = self.parser.parse_x12(request.x12_content)
            
            # Convert to structured JSON based on transaction type
            transaction_type = parsed_data.get('transaction_type', '837')
            
            if transaction_type == '837':
                json_data = self._convert_837_to_json(parsed_data)
            elif transaction_type == '835':
                json_data = self._convert_835_to_json(parsed_data)
            elif transaction_type == '834':
                json_data = self._convert_834_to_json(parsed_data)
            else:
                json_data = self._convert_generic_to_json(parsed_data)
            
            processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            return EDIConversionResponse(
                success=True,
                transaction_type=TransactionType(transaction_type),
                json_data=json_data,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            return EDIConversionResponse(
                success=False,
                error_message=str(e),
                processing_time_ms=processing_time
            )
    
    def _convert_837_to_json(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert 837 Claims data to structured JSON"""
        return {
            "transaction_type": "837",
            "transaction_name": "Health Care Claim",
            "control_number": parsed_data.get('control_number', ''),
            "submission_date": parsed_data.get('submission_date'),
            "provider": {
                "npi": parsed_data.get('provider', {}).get('npi', ''),
                "name": parsed_data.get('provider', {}).get('name', ''),
                "first_name": parsed_data.get('provider', {}).get('first_name', ''),
                "last_name": parsed_data.get('provider', {}).get('last_name', ''),
                "middle_name": parsed_data.get('provider', {}).get('middle_name', '')
            },
            "patient": {
                "member_id": parsed_data.get('patient', {}).get('member_id', ''),
                "first_name": parsed_data.get('patient', {}).get('first_name', ''),
                "last_name": parsed_data.get('patient', {}).get('last_name', ''),
                "middle_name": parsed_data.get('patient', {}).get('middle_name', '')
            },
            "diagnoses": parsed_data.get('diagnoses', []),
            "claim_lines": parsed_data.get('claim_lines', []),
            "total_charge_amount": parsed_data.get('total_charge_amount'),
            "metadata": {
                "parsed_at": time.time(),
                "version": "1.0"
            }
        }
    
    def _convert_835_to_json(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert 835 Remittance Advice data to structured JSON"""
        return {
            "transaction_type": "835",
            "transaction_name": "Health Care Claim Payment/Advice",
            "control_number": parsed_data.get('control_number', ''),
            "creation_date": parsed_data.get('creation_date'),
            "payer": {
                "name": parsed_data.get('payer_name', ''),
                "id": parsed_data.get('payer_id', '')
            },
            "provider": {
                "npi": parsed_data.get('provider', {}).get('npi', ''),
                "name": parsed_data.get('provider', {}).get('name', ''),
                "first_name": parsed_data.get('provider', {}).get('first_name', ''),
                "last_name": parsed_data.get('provider', {}).get('last_name', ''),
                "middle_name": parsed_data.get('provider', {}).get('middle_name', '')
            },
            "total_paid_amount": parsed_data.get('total_paid_amount'),
            "remittance_lines": parsed_data.get('remittance_lines', []),
            "metadata": {
                "parsed_at": time.time(),
                "version": "1.0"
            }
        }
    
    def _convert_834_to_json(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert 834 Enrollment data to structured JSON"""
        return {
            "transaction_type": "834",
            "transaction_name": "Benefit Enrollment and Maintenance",
            "control_number": parsed_data.get('control_number', ''),
            "creation_date": parsed_data.get('creation_date'),
            "sponsor": {
                "name": parsed_data.get('sponsor_name', ''),
                "id": parsed_data.get('sponsor_id', '')
            },
            "members": parsed_data.get('members', []),
            "member_count": len(parsed_data.get('members', [])),
            "metadata": {
                "parsed_at": time.time(),
                "version": "1.0"
            }
        }
    
    def _convert_generic_to_json(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert generic X12 data to structured JSON"""
        return {
            "transaction_type": parsed_data.get('transaction_type', 'unknown'),
            "segments": parsed_data.get('segments', []),
            "segment_count": len(parsed_data.get('segments', [])),
            "metadata": {
                "parsed_at": time.time(),
                "version": "1.0"
            }
        }
    
    def validate_x12(self, x12_content: str) -> Dict[str, Any]:
        """Validate X12 content structure"""
        validation_errors = []
        
        # Basic X12 structure validation
        if not x12_content.strip():
            validation_errors.append("Empty X12 content")
            return {"valid": False, "errors": validation_errors}
        
        # Check for ISA segment
        if not x12_content.strip().startswith('ISA'):
            validation_errors.append("Missing ISA segment")
        
        # Check for IEA segment
        if 'IEA' not in x12_content:
            validation_errors.append("Missing IEA segment")
        
        # Check for ST segment
        if 'ST' not in x12_content:
            validation_errors.append("Missing ST segment")
        
        # Check for SE segment
        if 'SE' not in x12_content:
            validation_errors.append("Missing SE segment")
        
        return {
            "valid": len(validation_errors) == 0,
            "errors": validation_errors
        }
