# EDI ToolKit

A fast, agentic EDI framework for X12 to JSON conversions specifically designed for the insurance industry. This toolkit provides high-performance conversion of popular EDI transactions through an MCP (Model Context Protocol) server interface.

## Features

- **Fast X12 to JSON Conversion**: Optimized parsing and conversion for insurance industry EDI transactions
- **MCP Server Integration**: Expose conversion capabilities through Model Context Protocol
- **Insurance-Focused**: Specialized support for the most common insurance EDI transactions
- **High Performance**: Sub-millisecond conversion times for typical transactions
- **Comprehensive Validation**: Built-in X12 structure validation and error handling

## Supported Transaction Types

| Code | Name | Description |
|------|------|-------------|
| 837 | Health Care Claim | Professional and institutional claims submission |
| 835 | Health Care Claim Payment/Advice | Remittance advice and payment information |
| 834 | Benefit Enrollment and Maintenance | Member enrollment and benefit maintenance |
| 270 | Health Care Eligibility/Benefit Inquiry | Eligibility verification request |
| 271 | Health Care Eligibility/Benefit Response | Eligibility verification response |
| 276 | Health Care Claim Status Request | Claim status inquiry |
| 277 | Health Care Claim Status Response | Claim status response |

## Installation

### Prerequisites

- Python 3.8 or higher
- pip or poetry for package management

### Install from Source

```bash
# Clone the repository
git clone <repository-url>
cd EDIToolKit

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

## Quick Start

### Running the MCP Server

```bash
# Start the MCP server
python main.py

# Or use the installed script
edi-converter
```

### Using the Conversion Tools

The MCP server exposes several tools for EDI conversion:

#### 1. Convert X12 to JSON
```json
{
  "tool": "convert_x12_to_json",
  "arguments": {
    "x12_content": "ISA*00*          *00*          *ZZ*SENDER         *ZZ*RECEIVER       *210101*1200*^*00501*000000001*0*P*:~...",
    "transaction_type": "837",
    "validate": true
  }
}
```

#### 2. Validate X12 Content
```json
{
  "tool": "validate_x12",
  "arguments": {
    "x12_content": "ISA*00*          *00*          *ZZ*SENDER         *ZZ*RECEIVER       *210101*1200*^*00501*000000001*0*P*:~..."
  }
}
```

#### 3. Get Supported Transactions
```json
{
  "tool": "get_supported_transactions",
  "arguments": {}
}
```

## API Reference

### Models

#### EDIConversionRequest
```python
{
  "x12_content": str,           # Raw X12 EDI content
  "transaction_type": str,      # Optional transaction type
  "validate": bool              # Whether to validate content
}
```

#### EDIConversionResponse
```python
{
  "success": bool,              # Conversion success status
  "transaction_type": str,      # Detected/used transaction type
  "json_data": dict,           # Converted JSON data
  "error_message": str,        # Error message if failed
  "validation_errors": list,   # Validation errors
  "processing_time_ms": float  # Processing time in milliseconds
}
```

### Transaction-Specific Tools

#### 837 Claims Conversion
```json
{
  "tool": "convert_837_claims",
  "arguments": {
    "x12_content": "ISA*00*..."
  }
}
```

#### 835 Remittance Conversion
```json
{
  "tool": "convert_835_remittance",
  "arguments": {
    "x12_content": "ISA*00*..."
  }
}
```

#### 834 Enrollment Conversion
```json
{
  "tool": "convert_834_enrollment",
  "arguments": {
    "x12_content": "ISA*00*..."
  }
}
```

## Example Usage

### Python Client Example

```python
import asyncio
from edi_framework.converter import EDIConverter
from edi_framework.models import EDIConversionRequest, TransactionType

async def convert_edi():
    converter = EDIConverter()
    
    # Sample X12 content (truncated for brevity)
    x12_content = """ISA*00*          *00*          *ZZ*SENDER         *ZZ*RECEIVER       *210101*1200*^*00501*000000001*0*P*:~
GS*HC*SENDER*RECEIVER*20210101*1200*1*X*005010X222A1~
ST*837*0001*005010X222A1~
BHT*0019*00*1*20210101*1200*CH~
NM1*41*2*ACME HEALTHCARE*****46*1234567890~
PER*IC*JOHN DOE*TE*555-123-4567~
NM1*40*2*INSURANCE COMPANY*****46*9876543210~
HL*1**20*1~
PRV*BI*PXC*207Q00000X~
NM1*85*2*ACME HEALTHCARE*****XX*1234567890~
N3*123 MAIN ST~
N4*CITY*ST*12345~
REF*EI*123456789~
NM1*QC*1*DOE*JOHN*M***MI*123456789~
N3*456 OAK AVE~
N4*CITY*ST*54321~
DMG*D8*19800101*M~
CLM*123456*100.00***11:B:1*Y*A*Y*I~
DTP*431*D8*20210101~
CL1*1*1*01~
HI*BK:Z123*BF:789~
LX*1~
SV2*0300*1*UN*100.00*100.00~
DTP*472*D8*20210101~
SE*25*0001~
GE*1*1~
IEA*1*000000001~"""
    
    request = EDIConversionRequest(
        x12_content=x12_content,
        transaction_type=TransactionType.CLAIMS_837,
        validate=True
    )
    
    response = converter.convert_to_json(request)
    
    if response.success:
        print(f"Conversion successful!")
        print(f"Transaction Type: {response.transaction_type}")
        print(f"Processing Time: {response.processing_time_ms}ms")
        print(f"JSON Data: {response.json_data}")
    else:
        print(f"Conversion failed: {response.error_message}")

# Run the example
asyncio.run(convert_edi())
```

## Development

### Project Structure

```
EDIToolKit/
├── src/
│   └── edi_framework/
│       ├── __init__.py
│       ├── models.py          # Pydantic models
│       ├── x12_parser.py      # X12 parsing logic
│       ├── converter.py       # JSON conversion logic
│       └── mcp_server.py      # MCP server implementation
├── tests/                     # Test files
├── main.py                    # Main entry point
├── requirements.txt           # Dependencies
├── pyproject.toml            # Project configuration
└── README.md                 # This file
```

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=src/edi_framework

# Run specific test
pytest tests/test_converter.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/
```

## Performance

The EDI ToolKit is optimized for high-performance conversion:

- **Typical 837 Claims**: < 1ms conversion time
- **Typical 835 Remittance**: < 1ms conversion time
- **Typical 834 Enrollment**: < 2ms conversion time
- **Memory Efficient**: Minimal memory footprint for large files
- **Streaming Support**: Can handle large EDI files efficiently

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:

- Create an issue in the GitHub repository
- Contact: support@editoolkit.com

## Roadmap

- [ ] Support for additional EDI transaction types
- [ ] Batch processing capabilities
- [ ] Web UI for testing conversions
- [ ] REST API endpoints
- [ ] Database integration for conversion history
- [ ] Advanced validation rules
- [ ] Custom field mapping configuration
