#!/usr/bin/env python3
"""
Test script to demonstrate EDI conversion functionality
"""

import sys
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from edi_framework.converter import EDIConverter
from edi_framework.models import EDIConversionRequest, TransactionType


def test_conversion():
    """Test EDI conversion with sample files"""
    converter = EDIConverter()
    
    # Test 837 Claims conversion
    print("=== Testing 837 Claims Conversion ===")
    with open("samples/sample_837.txt", "r") as f:
        x12_837 = f.read()
    
    request_837 = EDIConversionRequest(
        x12_content=x12_837,
        transaction_type=TransactionType.CLAIMS_837,
        validate_content=True
    )
    
    response_837 = converter.convert_to_json(request_837)
    
    if response_837.success:
        print(f"✅ 837 Conversion successful!")
        print(f"Transaction Type: {response_837.transaction_type}")
        print(f"Processing Time: {response_837.processing_time_ms:.2f}ms")
        print(f"JSON Structure:")
        print(json.dumps(response_837.json_data, indent=2, default=str)[:500] + "...")
    else:
        print(f"❌ 837 Conversion failed: {response_837.error_message}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 835 Remittance conversion
    print("=== Testing 835 Remittance Conversion ===")
    with open("samples/sample_835.txt", "r") as f:
        x12_835 = f.read()
    
    request_835 = EDIConversionRequest(
        x12_content=x12_835,
        transaction_type=TransactionType.REMITTANCE_835,
        validate_content=True
    )
    
    response_835 = converter.convert_to_json(request_835)
    
    if response_835.success:
        print(f"✅ 835 Conversion successful!")
        print(f"Transaction Type: {response_835.transaction_type}")
        print(f"Processing Time: {response_835.processing_time_ms:.2f}ms")
        print(f"JSON Structure:")
        print(json.dumps(response_835.json_data, indent=2, default=str)[:500] + "...")
    else:
        print(f"❌ 835 Conversion failed: {response_835.error_message}")
    
    print("\n" + "="*50 + "\n")
    
    # Test validation
    print("=== Testing X12 Validation ===")
    validation_result = converter.validate_x12(x12_837)
    
    if validation_result["valid"]:
        print("✅ X12 Content is valid")
    else:
        print("❌ X12 Content is invalid:")
        for error in validation_result["errors"]:
            print(f"  - {error}")


if __name__ == "__main__":
    test_conversion()
