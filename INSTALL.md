# Installation Guide

## Quick Start

### 1. Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

### 2. Test the Installation

```bash
# Run the test conversion script
python test_conversion.py
```

### 3. Start the MCP Server

```bash
# Start the MCP server
python main.py

# Or use the installed command
edi-converter
```

## Development Setup

### 1. Clone and Setup

```bash
git clone <repository-url>
cd EDIToolKit
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### 2. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/edi_framework

# Run specific test file
pytest tests/test_converter.py -v
```

### 3. Code Quality

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

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're in the project root directory and have installed dependencies
2. **MCP Server Not Starting**: Check that all MCP dependencies are installed correctly
3. **X12 Parsing Errors**: Ensure your X12 content follows proper EDI format with ISA/IEA envelope

### Dependencies

If you encounter dependency issues, try:

```bash
# Upgrade pip
pip install --upgrade pip

# Install with specific versions
pip install mcp==1.0.0 pydantic==2.0.0

# Or use the exact requirements
pip install -r requirements.txt --force-reinstall
```

### Testing Without MCP

If you want to test the conversion functionality without the MCP server:

```python
from src.edi_framework.converter import EDIConverter
from src.edi_framework.models import EDIConversionRequest, TransactionType

converter = EDIConverter()
request = EDIConversionRequest(x12_content="your_x12_content_here")
response = converter.convert_to_json(request)
print(response.json_data)
```
