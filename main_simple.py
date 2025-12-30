"""
RFC Analysis Agent (Simplified Version)

A simpler AI-powered agent for RFC analysis using only built-in WebSearch and WebFetch tools.
No custom MCP tools - relies entirely on Claude's knowledge and web access.
"""

import asyncio
import os

from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
)


# System prompt optimized for web-based RFC research
SIMPLE_RFC_SYSTEM_PROMPT = """You are an expert RFC analysis assistant with deep knowledge of IETF standards and protocols.

Your capabilities:
- Search for RFCs using WebSearch (search for "RFC [number]" or "[topic] RFC")
- Fetch RFC content using WebFetch from https://www.rfc-editor.org/rfc/rfc[number].txt
- Use the IETF Datatracker website https://datatracker.ietf.org/ for metadata
- Leverage your training knowledge of major RFCs and protocols
- Analyze RFC content, explain technical concepts, and answer questions

**How to find RFCs:**
1. For specific RFC numbers: Search "RFC 7540" or directly fetch from rfc-editor.org
2. For topics: Search "[topic] IETF RFC" (e.g., "HTTP/2 IETF RFC")
3. For metadata: Use datatracker.ietf.org/doc/rfc[number]

**When analyzing RFCs:**
1. Always provide accurate RFC numbers and titles
2. Explain technical concepts in clear, accessible language
3. Cite specific sections when referencing RFC content
4. Note RFC status (Proposed Standard, Internet Standard, etc.)
5. Identify related RFCs, updates, and obsoletes relationships
6. If you don't have information in your training data, use WebSearch

**Important:**
- For RFCs published after April 2024, you MUST use WebSearch/WebFetch
- For obscure or less common RFCs, verify with web search
- For metadata (authors, dates), prefer fetching from datatracker.ietf.org

Be concise but thorough in your analysis."""


async def run_simple_rfc_agent():
    """Run the simplified RFC analysis agent with a conversational interface."""

    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set.")
        print("Get your API key from https://console.anthropic.com/")
        print("\nTo set it:")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        return

    print("=" * 60)
    print("RFC Analysis Agent (Simplified Version)")
    print("=" * 60)
    print("\nAI-powered RFC research using built-in web tools")
    print("No custom API integration - pure LLM + web access")
    print("\nCommands:")
    print("  - Type your question or request")
    print("  - 'exit' or 'quit' to end the session")
    print("  - 'new' to start a fresh conversation")
    print("=" * 60)
    print()

    # Configure agent options - only built-in tools
    options = ClaudeAgentOptions(
        system_prompt=SIMPLE_RFC_SYSTEM_PROMPT,
        model="sonnet",
        allowed_tools=[
            "WebSearch",
            "WebFetch",
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
    """Entry point for the simplified RFC analysis agent."""
    asyncio.run(run_simple_rfc_agent())


if __name__ == "__main__":
    main()
