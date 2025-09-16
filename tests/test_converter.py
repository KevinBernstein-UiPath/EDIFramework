"""Tests for EDI Converter"""

import pytest

from src.edi_framework.converter import EDIConverter
from src.edi_framework.models import EDIConversionRequest, TransactionType
from tests.edi_payloads import (
    SAMPLE_834_ENROLLMENT,
    SAMPLE_835_REMITTANCE,
    SAMPLE_837_PROFESSIONAL,
)


class TestEDIConverter:
    """Test cases for EDIConverter"""

    def setup_method(self):
        """Setup test fixtures"""
        self.converter = EDIConverter()
        self.sample_837 = SAMPLE_837_PROFESSIONAL
        self.sample_835 = SAMPLE_835_REMITTANCE
        self.sample_834 = SAMPLE_834_ENROLLMENT

    def test_convert_837_to_json_success(self):
        """Test successful 837 conversion"""
        request = EDIConversionRequest(
            x12_content=self.sample_837,
            transaction_type=TransactionType.CLAIMS_837,
            validate_content=True,
        )

        response = self.converter.convert_to_json(request)

        assert response.success is True
        assert response.transaction_type == TransactionType.CLAIMS_837
        assert response.json_data is not None
        assert response.json_data["transaction_type"] == "837"
        assert response.json_data["control_number"] == "1001"
        assert response.json_data["provider"]["npi"] == "1234567890"
        assert response.processing_time_ms is not None
        assert response.processing_time_ms > 0

    def test_convert_837_auto_detect(self):
        """Test 837 conversion with auto-detection"""
        request = EDIConversionRequest(
            x12_content=self.sample_837,
            validate_content=True,
        )

        response = self.converter.convert_to_json(request)

        assert response.success is True
        assert response.transaction_type == TransactionType.CLAIMS_837

    def test_convert_835_to_json_success(self):
        """Test successful 835 conversion"""
        request = EDIConversionRequest(
            x12_content=self.sample_835,
            transaction_type=TransactionType.REMITTANCE_835,
            validate_content=True,
        )

        response = self.converter.convert_to_json(request)

        assert response.success is True
        assert response.transaction_type == TransactionType.REMITTANCE_835
        assert response.json_data["transaction_type"] == "835"
        assert response.json_data["control_number"] == "2001"
        assert response.json_data["total_paid_amount"] == pytest.approx(1500.0)
        assert response.json_data["payer"]["name"] == "MAJOR PAYER"

    def test_convert_834_to_json_success(self):
        """Test successful 834 conversion"""
        request = EDIConversionRequest(
            x12_content=self.sample_834,
            transaction_type=TransactionType.ENROLLMENT_834,
            validate_content=True,
        )

        response = self.converter.convert_to_json(request)

        assert response.success is True
        assert response.transaction_type == TransactionType.ENROLLMENT_834
        assert response.json_data["transaction_type"] == "834"
        assert response.json_data["sponsor"]["name"] == "BIG EMPLOYER"
        assert response.json_data["member_count"] == 2

    def test_convert_empty_content(self):
        """Test conversion with empty content"""
        request = EDIConversionRequest(
            x12_content="",
            validate_content=True,
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
            validate_content=True,
        )

        response = self.converter.convert_to_json(request)

        assert response.processing_time_ms is not None
        assert response.processing_time_ms >= 0
        assert response.processing_time_ms < 1000  # Should be fast

    def test_json_data_structure_837(self):
        """Test that 837 JSON data has correct structure"""
        request = EDIConversionRequest(
            x12_content=self.sample_837,
            transaction_type=TransactionType.CLAIMS_837,
            validate_content=True,
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
