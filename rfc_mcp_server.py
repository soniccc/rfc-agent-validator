#!/usr/bin/env python3
"""
RFC MCP Server

A standalone MCP server that exposes RFC analysis tools to any MCP client
(Claude Desktop, Claude Code CLI, or other applications).

Usage:
    python rfc_mcp_server.py

Or add to Claude Desktop config:
    {
      "mcpServers": {
        "rfc-tools": {
          "command": "python",
          "args": ["/path/to/rfc_mcp_server.py"]
        }
      }
    }
"""

import asyncio
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


# IETF Datatracker API base URL
DATATRACKER_API_BASE = "https://datatracker.ietf.org/api/v1"


# Create MCP server instance
app = Server("rfc-tools")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available RFC tools."""
    return [
        Tool(
            name="search_rfcs",
            description="Search for RFCs by keyword or topic",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'HTTP', 'DNS', 'TCP')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_rfc",
            description="Fetch detailed information about a specific RFC by number or name",
            inputSchema={
                "type": "object",
                "properties": {
                    "rfc_identifier": {
                        "type": "string",
                        "description": "RFC number or name (e.g., '7540', 'RFC7540', 'rfc7540')"
                    }
                },
                "required": ["rfc_identifier"]
            }
        ),
        Tool(
            name="get_rfc_text",
            description="Fetch the full text content of an RFC",
            inputSchema={
                "type": "object",
                "properties": {
                    "rfc_number": {
                        "type": "integer",
                        "description": "RFC number (e.g., 7540)"
                    }
                },
                "required": ["rfc_number"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute RFC tool calls."""

    if name == "search_rfcs":
        return await search_rfcs(arguments)
    elif name == "get_rfc":
        return await get_rfc(arguments)
    elif name == "get_rfc_text":
        return await get_rfc_text(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")


async def search_rfcs(args: dict[str, Any]) -> list[TextContent]:
    """Search for RFCs using the IETF Datatracker API."""
    query = args.get("query", "")
    limit = args.get("limit", 10)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{DATATRACKER_API_BASE}/doc/document/"
            params = {
                "limit": limit,
                "name__icontains": query,
                "type": "rfc"
            }

            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            results = []
            for doc in data.get("objects", []):
                results.append({
                    "name": doc.get("name", ""),
                    "title": doc.get("title", ""),
                    "rev": doc.get("rev", ""),
                    "abstract": doc.get("abstract", "")[:200] + "..." if doc.get("abstract") else ""
                })

            text = f"Found {len(results)} RFCs matching '{query}':\n\n" + "\n\n".join([
                f"**{r['name']}** - {r['title']}\n{r['abstract']}"
                for r in results
            ])

            return [TextContent(type="text", text=text)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error searching RFCs: {str(e)}")]


async def get_rfc(args: dict[str, Any]) -> list[TextContent]:
    """Get detailed RFC information from the IETF Datatracker API."""
    rfc_id = args.get("rfc_identifier", "")

    # Normalize RFC identifier
    if rfc_id.isdigit():
        rfc_id = f"rfc{rfc_id}"
    elif not rfc_id.lower().startswith("rfc"):
        rfc_id = f"rfc{rfc_id}"
    rfc_id = rfc_id.lower()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{DATATRACKER_API_BASE}/doc/document/{rfc_id}/"

            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            # Format the response
            result = {
                "name": data.get("name", ""),
                "title": data.get("title", ""),
                "abstract": data.get("abstract", ""),
                "rev": data.get("rev", ""),
                "pages": data.get("pages", ""),
                "authors": [author.get("person", "") for author in data.get("authors", [])],
                "stream": data.get("stream", ""),
                "group": data.get("group", ""),
                "std_level": data.get("std_level", ""),
                "intended_std_level": data.get("intended_std_level", ""),
                "rfc": data.get("rfc", ""),
            }

            formatted_output = f"""
# {result['name'].upper()}: {result['title']}

## Metadata
- **Authors**: {', '.join(result['authors']) if result['authors'] else 'N/A'}
- **Pages**: {result['pages']}
- **Stream**: {result['stream']}
- **Group**: {result['group']}
- **Standard Level**: {result['std_level'] or result['intended_std_level']}
- **RFC Number**: {result['rfc']}

## Abstract
{result['abstract']}
"""

            return [TextContent(type="text", text=formatted_output)]

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return [TextContent(type="text", text=f"RFC '{rfc_id}' not found. Please check the RFC number.")]
        return [TextContent(type="text", text=f"HTTP error fetching RFC: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error fetching RFC: {str(e)}")]


async def get_rfc_text(args: dict[str, Any]) -> list[TextContent]:
    """Fetch the full text of an RFC from the IETF website."""
    rfc_num = args.get("rfc_number", 0)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"https://www.rfc-editor.org/rfc/rfc{rfc_num}.txt"

            response = await client.get(url)
            response.raise_for_status()
            text_content = response.text

            # Truncate if too long
            if len(text_content) > 50000:
                text_content = text_content[:50000] + "\n\n[... content truncated for length ...]"

            return [TextContent(type="text", text=f"RFC {rfc_num} Full Text:\n\n{text_content}")]

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return [TextContent(type="text", text=f"RFC {rfc_num} text not found.")]
        return [TextContent(type="text", text=f"HTTP error fetching RFC text: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error fetching RFC text: {str(e)}")]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
