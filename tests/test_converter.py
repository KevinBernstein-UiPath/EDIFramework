"""
Tests for EDI Converter
"""

import pytest
from src.edi_framework.converter import EDIConverter
from src.edi_framework.models import EDIConversionRequest, TransactionType


class TestEDIConverter:
    """Test cases for EDIConverter"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.converter = EDIConverter()
        
        # Sample X12 837 content (minimal valid structure)
        self.sample_837 = """ISA*00*          *00*          *ZZ*SENDER         *ZZ*RECEIVER       *210101*1200*^*00501*000000001*0*P*:~
GS*HC*SENDER*RECEIVER*20210101*1200*1*X*005010X222A1~
ST*837*0001*005010X222A1~
BHT*0019*00*1*20210101*1200*CH~
NM1*41*2*ACME HEALTHCARE*****46*1234567890~
NM1*40*2*INSURANCE COMPANY*****46*9876543210~
HL*1**20*1~
NM1*85*2*ACME HEALTHCARE*****XX*1234567890~
NM1*QC*1*DOE*JOHN*M***MI*123456789~
CLM*123456*100.00***11:B:1*Y*A*Y*I~
SE*25*0001~
GE*1*1~
IEA*1*000000001~"""
    
    def test_convert_837_to_json_success(self):
        """Test successful 837 conversion"""
        request = EDIConversionRequest(
            x12_content=self.sample_837,
            transaction_type=TransactionType.CLAIMS_837,
            validate=True
        )
        
        response = self.converter.convert_to_json(request)
        
        assert response.success is True
        assert response.transaction_type == TransactionType.CLAIMS_837
        assert response.json_data is not None
        assert response.json_data["transaction_type"] == "837"
        assert response.processing_time_ms is not None
        assert response.processing_time_ms > 0
    
    def test_convert_837_auto_detect(self):
        """Test 837 conversion with auto-detection"""
        request = EDIConversionRequest(
            x12_content=self.sample_837,
            validate=True
        )
        
        response = self.converter.convert_to_json(request)
        
        assert response.success is True
        assert response.transaction_type == TransactionType.CLAIMS_837
    
    def test_convert_empty_content(self):
        """Test conversion with empty content"""
        request = EDIConversionRequest(
            x12_content="",
            validate=True
        )
        
        response = self.converter.convert_to_json(request)
        
        assert response.success is False
        assert response.error_message is not None
    
    def test_validate_x12_valid(self):
        """Test X12 validation with valid content"""
        validation_result = self.converter.validate_x12(self.sample_837)
        
        assert validation_result["valid"] is True
        assert len(validation_result["errors"]) == 0
    
    def test_validate_x12_invalid(self):
        """Test X12 validation with invalid content"""
        invalid_x12 = "INVALID X12 CONTENT"
        validation_result = self.converter.validate_x12(invalid_x12)
        
        assert validation_result["valid"] is False
        assert len(validation_result["errors"]) > 0
    
    def test_validate_x12_empty(self):
        """Test X12 validation with empty content"""
        validation_result = self.converter.validate_x12("")
        
        assert validation_result["valid"] is False
        assert "Empty X12 content" in validation_result["errors"]
    
    def test_processing_time_measurement(self):
        """Test that processing time is measured correctly"""
        request = EDIConversionRequest(
            x12_content=self.sample_837,
            validate=True
        )
        
        response = self.converter.convert_to_json(request)
        
        assert response.processing_time_ms is not None
        assert response.processing_time_ms >= 0
        assert response.processing_time_ms < 1000  # Should be fast
    
    def test_json_data_structure_837(self):
        """Test that 837 JSON data has correct structure"""
        request = EDIConversionRequest(
            x12_content=self.sample_837,
            transaction_type=TransactionType.CLAIMS_837
        )
        
        response = self.converter.convert_to_json(request)
        
        assert response.success is True
        json_data = response.json_data
        
        # Check required fields
        assert "transaction_type" in json_data
        assert "control_number" in json_data
        assert "provider" in json_data
        assert "patient" in json_data
        assert "diagnoses" in json_data
        assert "claim_lines" in json_data
        assert "metadata" in json_data
        
        # Check transaction type
        assert json_data["transaction_type"] == "837"
        assert json_data["transaction_name"] == "Health Care Claim"
        
        # Check metadata
        assert "parsed_at" in json_data["metadata"]
        assert "version" in json_data["metadata"]
