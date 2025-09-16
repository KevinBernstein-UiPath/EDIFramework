#!/usr/bin/env python3
"""
EDI ToolKit - Main Entry Point
Fast MCP Server for X12 to JSON conversions in the insurance industry
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from edi_framework.mcp_server import main

if __name__ == "__main__":
    asyncio.run(main())
