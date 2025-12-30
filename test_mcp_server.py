#!/usr/bin/env python3
"""
Quick test to verify the RFC MCP server is working.
"""

import asyncio
from pathlib import Path
from claude_agent_sdk import query, ClaudeAgentOptions


async def test_rfc_server():
    """Test that the MCP server starts and tools are available."""

    current_dir = Path(__file__).parent.absolute()
    mcp_server_path = current_dir / "rfc_mcp_server.py"

    print("Testing RFC MCP Server...")
    print(f"Server path: {mcp_server_path}")
    print()

    options = ClaudeAgentOptions(
        mcp_servers={
            "rfc": {
                "command": "uv",
                "args": ["run", "python", str(mcp_server_path)]
            }
        },
        allowed_tools=[
            "mcp__rfc__search_rfcs",
            "mcp__rfc__get_rfc",
            "mcp__rfc__get_rfc_text",
        ],
        permission_mode="bypassPermissions",
    )

    print("Attempting to fetch RFC 4271 (BGP) text...")
    print()

    async for message in query(
        prompt="Use the get_rfc_text tool to fetch RFC 4271. Just show me the first 100 characters of the text.",
        options=options
    ):
        if hasattr(message, 'content'):
            print(message)
        elif hasattr(message, 'result'):
            print("Result:", message.result)


if __name__ == "__main__":
    asyncio.run(test_rfc_server())
