"""
RFC Analysis Agent

An AI-powered agent for searching, browsing, and analyzing IETF RFCs using
the Claude Agent SDK and an external MCP server.

This agent connects to rfc_mcp_server.py for RFC tools, demonstrating
separation of concerns and tool reusability.
"""

import asyncio
import os
from pathlib import Path

from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
)


# System prompt for RFC analysis
RFC_SYSTEM_PROMPT = """You are an expert RFC analysis assistant with deep knowledge of IETF standards and protocols.

Your capabilities:
- Search for RFCs by keywords using the search_rfcs tool
- Retrieve detailed RFC metadata using the get_rfc tool
- Fetch full RFC text content using the get_rfc_text tool
- Analyze RFC content, explain technical concepts, and answer questions
- Compare multiple RFCs and identify relationships between standards
- Help users understand RFC status, obsolescence, and updates

**IMPORTANT: You have FULL ACCESS to all RFC tools. When asked about RFC content:**
1. ALWAYS use get_rfc_text to fetch the full RFC text when users ask for detailed information
2. You have permission to fetch ANY publicly available RFC
3. There are NO access restrictions - all RFCs are public documents
4. If get_rfc_text fails, report the actual error, don't assume there are restrictions

When analyzing RFCs:
1. Always provide accurate RFC numbers and titles
2. Explain technical concepts in clear, accessible language
3. Cite specific sections when referencing RFC content
4. Note RFC status (Proposed Standard, Draft Standard, Internet Standard, etc.)
5. Identify related RFCs, updates, and obsoletes relationships

Be concise but thorough in your analysis."""


async def run_rfc_agent():
    """Run the RFC analysis agent with a conversational interface."""

    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set.")
        print("Get your API key from https://console.anthropic.com/")
        print("\nTo set it:")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        return

    print("=" * 60)
    print("RFC Analysis Agent")
    print("=" * 60)
    print("\nAI-powered assistant for IETF RFC research and analysis")
    print("Using external MCP server for RFC tools")
    print("\nCommands:")
    print("  - Type your question or request")
    print("  - 'exit' or 'quit' to end the session")
    print("  - 'new' to start a fresh conversation")
    print("=" * 60)
    print()

    # Get absolute path to the MCP server
    current_dir = Path(__file__).parent.absolute()
    mcp_server_path = current_dir / "rfc_mcp_server.py"

    # Configure agent options to use external MCP server
    options = ClaudeAgentOptions(
        system_prompt=RFC_SYSTEM_PROMPT,
        model="sonnet",  # Use Claude Sonnet (recommended for most use cases)
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

    # Create and run the agent
    async with ClaudeSDKClient(options=options) as client:
        turn = 0

        while True:
            try:
                # Get user input
                user_input = input(f"\n[Turn {turn + 1}] You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["exit", "quit"]:
                    print("\nGoodbye!")
                    break

                if user_input.lower() == "new":
                    print("\n[Starting new conversation...]")
                    await client.disconnect()
                    await client.connect()
                    turn = 0
                    continue

                # Send query to agent
                await client.query(user_input)
                turn += 1

                # Process response
                print(f"\n[Turn {turn}] Agent: ", end="", flush=True)
                response_text = []

                async for message in client.receive_response():
                    if isinstance(message, AssistantMessage):
                        for block in message.content:
                            if isinstance(block, TextBlock):
                                print(block.text, end="", flush=True)
                                response_text.append(block.text)

                print()  # New line after response

            except KeyboardInterrupt:
                print("\n\nInterrupted. Type 'exit' to quit or continue chatting.")
                continue
            except Exception as e:
                print(f"\nError: {str(e)}")
                print("You can continue chatting or type 'exit' to quit.")


def main():
    """Entry point for the RFC analysis agent."""
    asyncio.run(run_rfc_agent())


if __name__ == "__main__":
    main()
