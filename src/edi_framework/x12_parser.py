"""
X12 EDI Parser for Insurance Industry Transactions
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, date
from .models import (
    TransactionType, Claim837, Remittance835, Enrollment834,
    Provider, Patient, Address, Diagnosis, Procedure, ClaimLine,
    RemittanceLine, EnrollmentMember
)


class X12Parser:
    """Parser for X12 EDI transactions"""
    
    def __init__(self):
        self.segment_delimiter = '~'
        self.element_delimiter = '*'
        self.sub_element_delimiter = ':'
        
    def parse_x12(self, x12_content: str) -> Dict[str, Any]:
        """Parse X12 content and return structured data"""
        # Clean and normalize X12 content
        x12_content = x12_content.strip()
        
        # Extract ISA header to get delimiters
        isa_segment = self._extract_isa_segment(x12_content)
        if isa_segment:
            self._update_delimiters(isa_segment)
        
        # Split into segments
        segments = self._split_segments(x12_content)
        
        # Determine transaction type
        transaction_type = self._determine_transaction_type(segments)
        
        # Parse based on transaction type
        if transaction_type == TransactionType.CLAIMS_837:
            return self._parse_837(segments)
        elif transaction_type == TransactionType.REMITTANCE_835:
            return self._parse_835(segments)
        elif transaction_type == TransactionType.ENROLLMENT_834:
            return self._parse_834(segments)
        else:
            return self._parse_generic(segments)
    
    def _extract_isa_segment(self, x12_content: str) -> Optional[str]:
        """Extract ISA segment from X12 content"""
        lines = x12_content.split('\n')
        for line in lines:
            if line.startswith('ISA'):
                return line.strip()
        return None
    
    def _update_delimiters(self, isa_segment: str):
        """Update delimiters based on ISA segment"""
        elements = isa_segment.split(self.element_delimiter)
        if len(elements) >= 16:
            # The 16th element contains the delimiter information
            delimiter_info = elements[15]
            if len(delimiter_info) >= 2:
                self.element_delimiter = delimiter_info[0]
                self.sub_element_delimiter = delimiter_info[1]
    
    def _split_segments(self, x12_content: str) -> List[str]:
        """Split X12 content into segments"""
        # Remove newlines and split by segment delimiter
        content = x12_content.replace('\n', '').replace('\r', '')
        segments = content.split(self.segment_delimiter)
        return [seg for seg in segments if seg.strip()]
    
    def _determine_transaction_type(self, segments: List[str]) -> TransactionType:
        """Determine transaction type from segments"""
        for segment in segments:
            if segment.startswith('ST'):
                elements = segment.split(self.element_delimiter)
                if len(elements) >= 2:
                    st01 = elements[1]
                    if st01 == '837':
                        return TransactionType.CLAIMS_837
                    elif st01 == '835':
                        return TransactionType.REMITTANCE_835
                    elif st01 == '834':
                        return TransactionType.ENROLLMENT_834
                    elif st01 == '270':
                        return TransactionType.ELIGIBILITY_270
                    elif st01 == '271':
                        return TransactionType.ELIGIBILITY_RESPONSE_271
        return TransactionType.CLAIMS_837  # Default
    
    def _parse_837(self, segments: List[str]) -> Dict[str, Any]:
        """Parse 837 Claims transaction"""
        result = {
            'transaction_type': '837',
            'control_number': '',
            'submission_date': None,
            'provider': {},
            'patient': {},
            'diagnoses': [],
            'claim_lines': [],
            'total_charge_amount': None
        }
        
        for segment in segments:
            if segment.startswith('ST'):
                elements = segment.split(self.element_delimiter)
                if len(elements) >= 3:
                    result['control_number'] = elements[2]
            elif segment.startswith('BHT'):
                elements = segment.split(self.element_delimiter)
                if len(elements) >= 4:
                    result['submission_date'] = self._parse_date(elements[3])
            elif segment.startswith('NM1'):
                elements = segment.split(self.element_delimiter)
                if len(elements) >= 4:
                    if elements[1] == '41':  # Provider
                        result['provider'] = self._parse_provider_nm1(elements)
                    elif elements[1] == 'QC':  # Patient
                        result['patient'] = self._parse_patient_nm1(elements)
            elif segment.startswith('CLM'):
                elements = segment.split(self.element_delimiter)
                if len(elements) >= 3:
                    result['total_charge_amount'] = self._parse_amount(elements[2])
            elif segment.startswith('HI'):
                elements = segment.split(self.element_delimiter)
                result['diagnoses'].extend(self._parse_diagnosis_codes(elements))
            elif segment.startswith('LX'):
                # Start of claim line
                pass
            elif segment.startswith('SV2'):
                elements = segment.split(self.element_delimiter)
                if len(elements) >= 3:
                    claim_line = self._parse_claim_line(elements)
                    result['claim_lines'].append(claim_line)
        
        return result
    
    def _parse_835(self, segments: List[str]) -> Dict[str, Any]:
        """Parse 835 Remittance Advice transaction"""
        result = {
            'transaction_type': '835',
            'control_number': '',
            'creation_date': None,
            'payer_name': '',
            'payer_id': '',
            'provider': {},
            'total_paid_amount': None,
            'remittance_lines': []
        }
        
        for segment in segments:
            if segment.startswith('ST'):
                elements = segment.split(self.element_delimiter)
                if len(elements) >= 3:
                    result['control_number'] = elements[2]
            elif segment.startswith('BPR'):
                elements = segment.split(self.element_delimiter)
                if len(elements) >= 3:
                    result['total_paid_amount'] = self._parse_amount(elements[2])
            elif segment.startswith('NM1'):
                elements = segment.split(self.element_delimiter)
                if len(elements) >= 4:
                    if elements[1] == '41':  # Payer
                        result['payer_name'] = elements[3] if len(elements) > 3 else ''
                        result['payer_id'] = elements[9] if len(elements) > 9 else ''
                    elif elements[1] == '85':  # Provider
                        result['provider'] = self._parse_provider_nm1(elements)
        
        return result
    
    def _parse_834(self, segments: List[str]) -> Dict[str, Any]:
        """Parse 834 Enrollment transaction"""
        result = {
            'transaction_type': '834',
            'control_number': '',
            'creation_date': None,
            'sponsor_name': '',
            'sponsor_id': '',
            'members': []
        }
        
        for segment in segments:
            if segment.startswith('ST'):
                elements = segment.split(self.element_delimiter)
                if len(elements) >= 3:
                    result['control_number'] = elements[2]
            elif segment.startswith('BGN'):
                elements = segment.split(self.element_delimiter)
                if len(elements) >= 3:
                    result['creation_date'] = self._parse_date(elements[2])
            elif segment.startswith('NM1'):
                elements = segment.split(self.element_delimiter)
                if len(elements) >= 4:
                    if elements[1] == '38':  # Sponsor
                        result['sponsor_name'] = elements[3] if len(elements) > 3 else ''
                        result['sponsor_id'] = elements[9] if len(elements) > 9 else ''
            elif segment.startswith('INS'):
                elements = segment.split(self.element_delimiter)
                member = self._parse_enrollment_member(elements)
                result['members'].append(member)
        
        return result
    
    def _parse_generic(self, segments: List[str]) -> Dict[str, Any]:
        """Parse generic X12 transaction"""
        result = {
            'transaction_type': 'unknown',
            'segments': []
        }
        
        for segment in segments:
            elements = segment.split(self.segment_delimiter)
            result['segments'].append({
                'segment_id': elements[0] if elements else '',
                'elements': elements[1:] if len(elements) > 1 else []
            })
        
        return result
    
    def _parse_provider_nm1(self, elements: List[str]) -> Dict[str, Any]:
        """Parse NM1 segment for provider"""
        return {
            'npi': elements[9] if len(elements) > 9 else '',
            'name': elements[3] if len(elements) > 3 else '',
            'last_name': elements[3] if len(elements) > 3 else '',
            'first_name': elements[4] if len(elements) > 4 else '',
            'middle_name': elements[5] if len(elements) > 5 else ''
        }
    
    def _parse_patient_nm1(self, elements: List[str]) -> Dict[str, Any]:
        """Parse NM1 segment for patient"""
        return {
            'member_id': elements[9] if len(elements) > 9 else '',
            'last_name': elements[3] if len(elements) > 3 else '',
            'first_name': elements[4] if len(elements) > 4 else '',
            'middle_name': elements[5] if len(elements) > 5 else ''
        }
    
    def _parse_diagnosis_codes(self, elements: List[str]) -> List[Dict[str, str]]:
        """Parse diagnosis codes from HI segment"""
        diagnoses = []
        for i in range(1, len(elements), 2):
            if i + 1 < len(elements):
                diagnoses.append({
                    'code': elements[i + 1],
                    'description': ''
                })
        return diagnoses
    
    def _parse_claim_line(self, elements: List[str]) -> Dict[str, Any]:
        """Parse claim line from SV2 segment"""
        return {
            'procedure_code': elements[1] if len(elements) > 1 else '',
            'quantity': self._parse_amount(elements[2]) if len(elements) > 2 else None,
            'unit_price': self._parse_amount(elements[3]) if len(elements) > 3 else None,
            'total_amount': self._parse_amount(elements[4]) if len(elements) > 4 else None
        }
    
    def _parse_enrollment_member(self, elements: List[str]) -> Dict[str, Any]:
        """Parse enrollment member from INS segment"""
        return {
            'member_id': elements[2] if len(elements) > 2 else '',
            'first_name': elements[3] if len(elements) > 3 else '',
            'last_name': elements[4] if len(elements) > 4 else '',
            'date_of_birth': self._parse_date(elements[5]) if len(elements) > 5 else None,
            'gender': elements[6] if len(elements) > 6 else '',
            'effective_date': self._parse_date(elements[7]) if len(elements) > 7 else None
        }
    
    def _parse_date(self, date_str: str) -> Optional[date]:
        """Parse date string in various formats"""
        if not date_str:
            return None
        
        # Common X12 date formats
        formats = ['%Y%m%d', '%Y%m', '%m%d%Y', '%d%m%Y']
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        return None
    
    def _parse_amount(self, amount_str: str) -> Optional[float]:
        """Parse amount string to float"""
        if not amount_str:
            return None
        
        try:
            # Remove any non-numeric characters except decimal point and minus
            cleaned = re.sub(r'[^\d.-]', '', amount_str)
            return float(cleaned)
        except (ValueError, TypeError):
            return None
