"""Unit tests for the low-level X12 parser."""

from __future__ import annotations

from datetime import date

import pytest

from src.edi_framework.x12_parser import X12Parser
from tests.edi_payloads import (
    SAMPLE_270_ELIGIBILITY,
    SAMPLE_271_ELIGIBILITY_RESPONSE,
    SAMPLE_834_ENROLLMENT,
    SAMPLE_835_REMITTANCE,
    SAMPLE_837_INSTITUTIONAL,
    SAMPLE_837_PROFESSIONAL,
)


class TestX12Parser:
    """Validate parsing logic across supported transaction types."""

    def test_parse_837_professional(self):
        parser = X12Parser()
        parsed = parser.parse_x12(SAMPLE_837_PROFESSIONAL)

        assert parsed["transaction_type"] == "837"
        assert parsed["control_number"] == "1001"
        assert parsed["submission_date"] == date(2024, 3, 15)
        assert parsed["provider"]["npi"] == "1234567890"
        assert parsed["patient"]["member_id"] == "W123456789"
        assert parsed["total_charge_amount"] == pytest.approx(250.0)
        assert [diag["code"] for diag in parsed["diagnoses"]] == ["A1234", "B5678"]
        assert len(parsed["claim_lines"]) == 2
        assert parsed["claim_lines"][0]["procedure_code"] == "HC:99213"
        assert parsed["claim_lines"][1]["total_amount"] == pytest.approx(125.0)

    def test_parse_837_institutional_amount_formats(self):
        parser = X12Parser()
        parsed = parser.parse_x12(SAMPLE_837_INSTITUTIONAL)

        assert parsed["transaction_type"] == "837"
        assert parsed["control_number"] == "1002"
        # BHT02 uses mdy format which the parser should normalize
        assert parsed["submission_date"] == date(2024, 3, 15)
        assert parsed["total_charge_amount"] == pytest.approx(1234.56)
        assert [diag["code"] for diag in parsed["diagnoses"]] == [
            "C1234",
            "D5678",
            "E1111",
        ]
        assert parsed["claim_lines"][0]["quantity"] == pytest.approx(3.0)

    def test_parse_835_remittance(self):
        parser = X12Parser()
        parsed = parser.parse_x12(SAMPLE_835_REMITTANCE)

        assert parsed["transaction_type"] == "835"
        assert parsed["control_number"] == "2001"
        assert parsed["total_paid_amount"] == pytest.approx(1500.0)
        assert parsed["payer_name"] == "MAJOR PAYER"
        assert parsed["payer_id"] == "999888777"
        assert parsed["provider"]["npi"] == "1234567893"

    def test_parse_834_enrollment_members(self):
        parser = X12Parser()
        parsed = parser.parse_x12(SAMPLE_834_ENROLLMENT)

        assert parsed["transaction_type"] == "834"
        assert parsed["control_number"] == "3001"
        assert parsed["creation_date"] == date(2024, 4, 2)
        assert parsed["sponsor_name"] == "BIG EMPLOYER"
        assert parsed["sponsor_id"] == "EMP001"
        assert len(parsed["members"]) == 2
        subscriber = parsed["members"][0]
        dependent = parsed["members"][1]
        assert subscriber["member_id"] == "MEM001"
        assert subscriber["date_of_birth"] == date(1980, 1, 1)
        assert dependent["member_id"] == "DEP001"
        assert dependent["effective_date"] == date(2024, 2, 1)

    def test_parse_generic_transaction_includes_segments(self):
        parser = X12Parser()
        parsed = parser.parse_x12(SAMPLE_270_ELIGIBILITY)

        assert parsed["transaction_type"] == "unknown"
        assert len(parsed["segments"]) == 9
        assert parsed["segments"][2]["segment_id"].startswith("ST*270")

    def test_parser_state_not_shared_between_runs(self):
        parser = X12Parser()
        first = parser.parse_x12(SAMPLE_270_ELIGIBILITY)
        second = parser.parse_x12(SAMPLE_271_ELIGIBILITY_RESPONSE)

        # ensure parsing a generic transaction after another retains correct metadata
        assert first["transaction_type"] == "unknown"
        assert second["transaction_type"] == "unknown"
        assert second["segments"][2]["segment_id"].startswith("ST*271")

    def test_update_delimiters_reads_component_from_isa(self):
        parser = X12Parser()
        isa_segment = "ISA*00*AA*00*BB*ZZ*SENDER*ZZ*RECEIVER*20240406*1200*^*00501*000000061*P*|^"

        parser._update_delimiters(isa_segment)

        assert parser.element_delimiter == "|"
        assert parser.sub_element_delimiter == "^"
