"""
MCP Server for EDI X12 to JSON Conversion
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource,
    CallToolRequest, CallToolResult, ListResourcesRequest, ListResourcesResult,
    ListToolsRequest, ListToolsResult, ReadResourceRequest, ReadResourceResult
)

from .converter import EDIConverter
from .models import EDIConversionRequest, TransactionType


class EDIMCPServer:
    """MCP Server for EDI X12 to JSON conversion"""
    
    def __init__(self):
        self.server = Server("edi-converter")
        self.converter = EDIConverter()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List available EDI conversion tools"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="convert_x12_to_json",
                        description="Convert X12 EDI content to JSON format for insurance industry transactions",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "x12_content": {
                                    "type": "string",
                                    "description": "Raw X12 EDI content to convert"
                                },
                                "transaction_type": {
                                    "type": "string",
                                    "enum": ["837", "835", "834", "270", "271", "276", "277"],
                                    "description": "Expected transaction type (optional, will auto-detect if not provided)"
                                },
                                "validate": {
                                    "type": "boolean",
                                    "description": "Whether to validate the X12 content structure",
                                    "default": True
                                }
                            },
                            "required": ["x12_content"]
                        }
                    ),
                    Tool(
                        name="validate_x12",
                        description="Validate X12 EDI content structure and format",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "x12_content": {
                                    "type": "string",
                                    "description": "Raw X12 EDI content to validate"
                                }
                            },
                            "required": ["x12_content"]
                        }
                    ),
                    Tool(
                        name="get_supported_transactions",
                        description="Get list of supported EDI transaction types",
                        inputSchema={
                            "type": "object",
                            "properties": {}
                        }
                    ),
                    Tool(
                        name="convert_837_claims",
                        description="Convert 837 Health Care Claim transaction to JSON",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "x12_content": {
                                    "type": "string",
                                    "description": "Raw X12 837 EDI content"
                                }
                            },
                            "required": ["x12_content"]
                        }
                    ),
                    Tool(
                        name="convert_835_remittance",
                        description="Convert 835 Health Care Claim Payment/Advice transaction to JSON",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "x12_content": {
                                    "type": "string",
                                    "description": "Raw X12 835 EDI content"
                                }
                            },
                            "required": ["x12_content"]
                        }
                    ),
                    Tool(
                        name="convert_834_enrollment",
                        description="Convert 834 Benefit Enrollment and Maintenance transaction to JSON",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "x12_content": {
                                    "type": "string",
                                    "description": "Raw X12 834 EDI content"
                                }
                            },
                            "required": ["x12_content"]
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls"""
            try:
                if name == "convert_x12_to_json":
                    return await self._handle_convert_x12_to_json(arguments)
                elif name == "validate_x12":
                    return await self._handle_validate_x12(arguments)
                elif name == "get_supported_transactions":
                    return await self._handle_get_supported_transactions()
                elif name == "convert_837_claims":
                    return await self._handle_convert_837_claims(arguments)
                elif name == "convert_835_remittance":
                    return await self._handle_convert_835_remittance(arguments)
                elif name == "convert_834_enrollment":
                    return await self._handle_convert_834_enrollment(arguments)
                else:
                    return CallToolResult(
                        content=[TextContent(
                            type="text",
                            text=f"Unknown tool: {name}"
                        )],
                        isError=True
                    )
            except Exception as e:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Error executing tool {name}: {str(e)}"
                    )],
                    isError=True
                )
    
    async def _handle_convert_x12_to_json(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle X12 to JSON conversion"""
        x12_content = arguments.get("x12_content", "")
        transaction_type = arguments.get("transaction_type")
        validate = arguments.get("validate", True)
        
        if not x12_content:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Error: x12_content is required"
                )],
                isError=True
            )
        
        # Create conversion request
        request = EDIConversionRequest(
            x12_content=x12_content,
            transaction_type=TransactionType(transaction_type) if transaction_type else None,
            validate=validate
        )
        
        # Perform conversion
        response = self.converter.convert_to_json(request)
        
        if response.success:
            result_text = f"""✅ EDI Conversion Successful

Transaction Type: {response.transaction_type.value if response.transaction_type else 'Auto-detected'}
Processing Time: {response.processing_time_ms:.2f}ms

JSON Output:
{json.dumps(response.json_data, indent=2, default=str)}"""
        else:
            result_text = f"""❌ EDI Conversion Failed

Error: {response.error_message}
Processing Time: {response.processing_time_ms:.2f}ms"""
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=result_text
            )]
        )
    
    async def _handle_validate_x12(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle X12 validation"""
        x12_content = arguments.get("x12_content", "")
        
        if not x12_content:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Error: x12_content is required"
                )],
                isError=True
            )
        
        validation_result = self.converter.validate_x12(x12_content)
        
        if validation_result["valid"]:
            result_text = "✅ X12 Content is Valid\n\nStructure validation passed successfully."
        else:
            errors = "\n".join([f"• {error}" for error in validation_result["errors"]])
            result_text = f"❌ X12 Content is Invalid\n\nValidation Errors:\n{errors}"
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=result_text
            )]
        )
    
    async def _handle_get_supported_transactions(self) -> CallToolResult:
        """Handle getting supported transaction types"""
        transactions = [
            {
                "code": "837",
                "name": "Health Care Claim",
                "description": "Professional and institutional claims submission"
            },
            {
                "code": "835",
                "name": "Health Care Claim Payment/Advice",
                "description": "Remittance advice and payment information"
            },
            {
                "code": "834",
                "name": "Benefit Enrollment and Maintenance",
                "description": "Member enrollment and benefit maintenance"
            },
            {
                "code": "270",
                "name": "Health Care Eligibility/Benefit Inquiry",
                "description": "Eligibility verification request"
            },
            {
                "code": "271",
                "name": "Health Care Eligibility/Benefit Response",
                "description": "Eligibility verification response"
            },
            {
                "code": "276",
                "name": "Health Care Claim Status Request",
                "description": "Claim status inquiry"
            },
            {
                "code": "277",
                "name": "Health Care Claim Status Response",
                "description": "Claim status response"
            }
        ]
        
        result_text = "📋 Supported EDI Transaction Types\n\n"
        for tx in transactions:
            result_text += f"**{tx['code']} - {tx['name']}**\n"
            result_text += f"{tx['description']}\n\n"
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=result_text
            )]
        )
    
    async def _handle_convert_837_claims(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle 837 claims conversion"""
        return await self._handle_convert_x12_to_json({
            **arguments,
            "transaction_type": "837"
        })
    
    async def _handle_convert_835_remittance(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle 835 remittance conversion"""
        return await self._handle_convert_x12_to_json({
            **arguments,
            "transaction_type": "835"
        })
    
    async def _handle_convert_834_enrollment(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle 834 enrollment conversion"""
        return await self._handle_convert_x12_to_json({
            **arguments,
            "transaction_type": "834"
        })
    
    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="edi-converter",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None
                    )
                )
            )


async def main():
    """Main entry point"""
    server = EDIMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
