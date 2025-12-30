# RFC MCP Server - Complete Guide

The RFC tools can be exposed as a **standalone MCP server** that any MCP client can use with any LLM that supports function calling.

## Table of Contents

- [Understanding the Architecture](#understanding-the-architecture)
- [MCP is Model-Agnostic](#mcp-is-model-agnostic)
- [Running the MCP Server](#running-the-mcp-server)
- [Integration Options](#integration-options)
- [Available Tools](#available-tools)
- [Use Cases](#use-cases)
- [Debugging](#debugging)

## Understanding the Architecture

### What is What?

**`main.py` - RFC Agent (also an MCP client)**
- Conversational AI assistant with autonomous behavior
- Connects to `rfc_mcp_server.py` for tools
- Interactive CLI for RFC research
- Uses Claude (via Agent SDK)

**`rfc_mcp_server.py` - MCP Server**
- Standalone service exposing RFC tools
- Model-agnostic (works with any LLM)
- Stateless tool provider
- Can serve multiple clients simultaneously

**Claude Desktop - MCP Client**
- Application that connects to MCP servers
- Not an "agent" (no autonomous behavior)
- Uses Claude models

### Architecture Diagram

```
┌─────────────────────────────┐
│   Any MCP Client            │
│   ┌─────────────────────┐   │
│   │  Any LLM:           │   │
│   │  - Claude           │   │
│   │  - GPT-4            │   │
│   │  - Gemini           │   │
│   │  - DeepSeek         │   │
│   │  - Llama, etc.      │   │
│   └─────────────────────┘   │
└──────────┬──────────────────┘
           │
           │ MCP Protocol (model-agnostic)
           │
┌──────────▼──────────────────┐
│  rfc_mcp_server.py          │
│  (Exposes RFC tools)        │
│  - search_rfcs              │
│  - get_rfc                  │
│  - get_rfc_text             │
└──────────┬──────────────────┘
           │
           │ HTTPS
           │
┌──────────▼──────────────────┐
│  IETF Datatracker API       │
│  datatracker.ietf.org       │
└─────────────────────────────┘
```

## MCP is Model-Agnostic

**Key Insight:** Your RFC MCP server works with **ANY LLM**, not just Claude!

The MCP (Model Context Protocol) is a **protocol standard**, not tied to any specific model or vendor. Any LLM that supports function/tool calling can use your RFC tools.

### Supported Models

✅ **Anthropic Claude** (Sonnet, Opus, Haiku)
✅ **OpenAI** (GPT-4, GPT-4 Turbo, GPT-3.5)
✅ **Google Gemini** (Pro, Ultra)
✅ **DeepSeek** (supports OpenAI-compatible function calling)
✅ **Local Models** (Llama 3+, Mistral via adapters)
✅ **Any model with function calling support**

### Example: Using RFC Tools with Different Models

**With Claude (via main.py):**
```bash
uv run python main.py
```
→ Uses Claude Sonnet via Agent SDK

**With GPT-4 (custom client):**
```python
from openai import OpenAI
import subprocess

client = OpenAI()

# Start your RFC MCP server
mcp_process = subprocess.Popen(
    ["uv", "run", "python", "rfc_mcp_server.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE
)

# Discover tools from MCP server
# Convert to OpenAI function format
# Use with GPT-4
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Tell me about RFC 7540"}],
    tools=[...]  # Your RFC tools from MCP server
)
```

**With DeepSeek (for your RFC Browser backend):**
```python
from openai import OpenAI  # DeepSeek uses OpenAI-compatible API

client = OpenAI(
    api_key="your-deepseek-api-key",
    base_url="https://api.deepseek.com"
)

# Connect to rfc_mcp_server.py
# Use DeepSeek with RFC tools
# Much cheaper than Claude for production!
```

**With Google Gemini:**
```python
import google.generativeai as genai

genai.configure(api_key="your-api-key")
model = genai.GenerativeModel('gemini-pro')

# Connect to your RFC MCP server
# Use Gemini with RFC tools
```

### Why This Matters

**For Your RFC Browser Application:**
- Use DeepSeek (cheaper) for production Q&A
- Same RFC tools, different model
- No code changes to the MCP server
- Switch models based on cost/performance needs

**Architecture Benefits:**
1. ✅ **Vendor independence** - Not locked into Claude
2. ✅ **Cost optimization** - Use cheaper models when appropriate
3. ✅ **Model diversity** - Try different models without rewriting tools
4. ✅ **Future-proof** - Works with new models as they're released

## Running the MCP Server

### Method 1: Direct Execution (for testing)

```bash
# Run the server (it will communicate via stdio)
uv run python rfc_mcp_server.py
```

The server starts and waits for MCP protocol messages on stdin/stdout.

### Method 2: Test with MCP Inspector (recommended for development)

```bash
# Install MCP inspector globally (first time only)
npm install -g @modelcontextprotocol/inspector

# Inspect your RFC MCP server
npx @modelcontextprotocol/inspector uv run python rfc_mcp_server.py
```

This opens a web UI where you can:
- Test tools interactively
- See request/response JSON
- Debug tool implementations
- Verify the server is working correctly

## Integration Options

### Option 1: Claude Desktop

**Location of config file:**
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

**Configuration (using uv):**
```json
{
  "mcpServers": {
    "rfc-tools": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "/absolute/path/to/rfc-agent-validator/rfc_mcp_server.py"
      ]
    }
  }
}
```

**Configuration (using virtual environment Python):**
```json
{
  "mcpServers": {
    "rfc-tools": {
      "command": "/absolute/path/to/rfc-agent-validator/.venv/bin/python",
      "args": [
        "/absolute/path/to/rfc-agent-validator/rfc_mcp_server.py"
      ]
    }
  }
}
```

**After configuration:**
1. Save the config file
2. Restart Claude Desktop completely
3. The RFC tools will appear in any conversation
4. Ask Claude: "Tell me about RFC 7540" and it will use your tools!

### Option 2: Claude Code CLI

**Add to project's `.claude/settings.json`:**
```json
{
  "mcpServers": {
    "rfc-tools": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "/absolute/path/to/rfc-agent-validator/rfc_mcp_server.py"
      ]
    }
  }
}
```

### Option 3: Agent SDK Applications (like main.py)

**Python example:**
```python
from pathlib import Path
from claude_agent_sdk import query, ClaudeAgentOptions

# Get absolute path to MCP server
current_dir = Path(__file__).parent.absolute()
mcp_server_path = current_dir / "rfc_mcp_server.py"

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
    ]
)

async for message in query(
    prompt="Find RFCs about QUIC protocol",
    options=options
):
    print(message)
```

**TypeScript example:**
```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";
import path from "path";

const mcpServerPath = path.join(__dirname, "rfc_mcp_server.py");

for await (const message of query({
  prompt: "Find RFCs about QUIC protocol",
  options: {
    mcpServers: {
      rfc: {
        command: "uv",
        args: ["run", "python", mcpServerPath]
      }
    },
    allowedTools: [
      "mcp__rfc__search_rfcs",
      "mcp__rfc__get_rfc",
      "mcp__rfc__get_rfc_text"
    ]
  }
})) {
  console.log(message);
}
```

### Option 4: Custom Client with Any LLM

See the [MCP is Model-Agnostic](#mcp-is-model-agnostic) section above for examples with GPT-4, DeepSeek, and Gemini.

## Available Tools

Once connected, any MCP client can use these tools:

### 1. `search_rfcs`

Search for RFCs by keyword or topic using the IETF Datatracker API.

**Input Schema:**
```json
{
  "query": "string (required) - Search term (e.g., 'HTTP', 'DNS', 'QUIC')",
  "limit": "integer (optional) - Maximum results to return (default: 10)"
}
```

**Example Input:**
```json
{
  "query": "QUIC",
  "limit": 5
}
```

**Example Output:**
```
Found 5 RFCs matching 'QUIC':

**rfc9000** - QUIC: A UDP-Based Multiplexed and Secure Transport
This document defines the core QUIC transport protocol...

**rfc9001** - Using TLS to Secure QUIC
This document describes how Transport Layer Security (TLS) is used...
```

### 2. `get_rfc`

Fetch detailed metadata and abstract for a specific RFC.

**Input Schema:**
```json
{
  "rfc_identifier": "string (required) - RFC number or name (e.g., '7540', 'RFC7540', 'rfc7540')"
}
```

**Example Input:**
```json
{
  "rfc_identifier": "7540"
}
```

**Example Output:**
```markdown
# RFC7540: Hypertext Transfer Protocol Version 2 (HTTP/2)

## Metadata
- **Authors**: M. Belshe, R. Peon, M. Thomson
- **Pages**: 96
- **Stream**: IETF
- **Standard Level**: Proposed Standard

## Abstract
This specification describes an optimized expression of the semantics
of the Hypertext Transfer Protocol (HTTP), referred to as HTTP version 2...
```

### 3. `get_rfc_text`

Fetch the complete text content of an RFC from the official RFC repository.

**Input Schema:**
```json
{
  "rfc_number": "integer (required) - RFC number (e.g., 7540)"
}
```

**Example Input:**
```json
{
  "rfc_number": 7540
}
```

**Example Output:**
```
RFC 7540 Full Text:

Internet Engineering Task Force (IETF)                        M. Belshe
Request for Comments: 7540                                      BitGo
Category: Standards Track                                     R. Peon
ISSN: 2070-1721                                              Google, Inc
                                                           M. Thomson, Ed.
                                                                  Mozilla
                                                                May 2015

            Hypertext Transfer Protocol Version 2 (HTTP/2)

[Full RFC text follows...]
```

**Note:** Content is truncated at 50,000 characters if the RFC is very large.

## Use Cases

### 1. Personal Research (Claude Desktop)

Add RFC tools to Claude Desktop for any conversation:

```
You: What's the difference between HTTP/2 and HTTP/3?

Claude: Let me search for the relevant RFCs...
[Uses search_rfcs to find HTTP/2 and HTTP/3 RFCs]
[Uses get_rfc to fetch metadata]
[Analyzes and compares the protocols]

Here's what I found:
- HTTP/2 (RFC 7540): Uses TCP with binary framing...
- HTTP/3 (RFC 9114): Uses QUIC (UDP-based)...
```

### 2. Development (Multiple Agents)

Multiple agents in your application share the same RFC MCP server:

```python
# Agent 1: RFC Researcher
researcher = ClaudeSDKClient(options=rfc_options)

# Agent 2: Protocol Analyzer
analyzer = ClaudeSDKClient(options=rfc_options)

# Agent 3: Security Auditor
auditor = ClaudeSDKClient(options=rfc_options)

# All three use the same rfc_mcp_server.py
# Update tools once, all agents benefit
```

### 3. Production (Microservice Architecture)

Deploy the MCP server as a backend service for your RFC Browser:

```
┌─────────────────────┐
│  React Frontend     │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  FastAPI Backend    │
│  (with DeepSeek)    │
└──────────┬──────────┘
           │ MCP Protocol
┌──────────▼──────────┐
│  rfc_mcp_server.py  │
│  (as a service)     │
└─────────────────────┘
```

Benefits:
- Use cheaper model (DeepSeek) for production
- Same RFC tools, lower costs
- Horizontally scalable (run multiple server instances)

### 4. Cross-Model Comparison

Test the same query with different models:

```bash
# With Claude
uv run python main.py

# With GPT-4 (custom client)
python gpt4_rfc_client.py

# With DeepSeek (custom client)
python deepseek_rfc_client.py

# All using the same RFC MCP server!
```

## Debugging

### Verify Server Starts Correctly

```bash
# Send initialize message
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | uv run python rfc_mcp_server.py
```

**Expected output:** JSON response with server capabilities
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "serverInfo": {
      "name": "rfc-tools",
      "version": "1.0.0"
    },
    "capabilities": {
      "tools": {}
    }
  }
}
```

### Test Tool Execution

```bash
# First initialize, then call a tool
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"search_rfcs","arguments":{"query":"HTTP","limit":3}}}' | uv run python rfc_mcp_server.py
```

### Common Issues

**Issue:** "Command not found: uv"
**Solution:** Install uv or use direct Python path: `python rfc_mcp_server.py`

**Issue:** "ModuleNotFoundError: No module named 'httpx'"
**Solution:** Install dependencies: `uv sync` or `pip install httpx mcp`

**Issue:** Claude Desktop doesn't show RFC tools
**Solution:**
1. Check config file path is absolute (not relative)
2. Verify JSON syntax is valid
3. Restart Claude Desktop completely
4. Check Claude Desktop logs for errors

**Issue:** "Server connection failed"
**Solution:** Test server manually with MCP Inspector first

## Comparison: Agent vs MCP Server vs Client

| Aspect | RFC Agent (main.py) | MCP Server (rfc_mcp_server.py) | MCP Client |
|--------|---------------------|--------------------------------|------------|
| **Type** | Agent + MCP client | MCP server | Application |
| **Purpose** | RFC research assistant | Tool provider | Tool consumer |
| **Autonomous** | Yes (conversational) | No (stateless) | Varies |
| **Interface** | Interactive CLI | MCP protocol (stdio) | Application-specific |
| **Conversation** | Yes, maintains context | No, stateless tools | Depends on client |
| **LLM Used** | Claude (Agent SDK) | None (model-agnostic) | Any LLM |
| **Best For** | End-user research | Tool sharing | Integration |

## Extending the Server

### Adding New Tools

To add new RFC-related tools:

1. **Define the tool in `list_tools()`:**
```python
@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        # ... existing tools ...
        Tool(
            name="compare_rfcs",
            description="Compare two RFCs side by side",
            inputSchema={
                "type": "object",
                "properties": {
                    "rfc1": {"type": "integer"},
                    "rfc2": {"type": "integer"}
                },
                "required": ["rfc1", "rfc2"]
            }
        )
    ]
```

2. **Implement the tool handler:**
```python
async def compare_rfcs(args: dict[str, Any]) -> list[TextContent]:
    rfc1_num = args.get("rfc1")
    rfc2_num = args.get("rfc2")

    # Fetch both RFCs
    # Compare them
    # Return comparison

    return [TextContent(type="text", text=comparison_text)]
```

3. **Add to call_tool() dispatcher:**
```python
@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    if name == "search_rfcs":
        return await search_rfcs(arguments)
    elif name == "get_rfc":
        return await get_rfc(arguments)
    elif name == "get_rfc_text":
        return await get_rfc_text(arguments)
    elif name == "compare_rfcs":
        return await compare_rfcs(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")
```

4. **Update main.py allowed_tools:**
```python
allowed_tools=[
    "mcp__rfc__search_rfcs",
    "mcp__rfc__get_rfc",
    "mcp__rfc__get_rfc_text",
    "mcp__rfc__compare_rfcs",  # Add new tool
]
```

All clients (main.py, Claude Desktop, custom clients) will automatically get the new tool!

## Next Steps

1. **Test the server:** Use MCP Inspector to verify all tools work
2. **Add to Claude Desktop:** Edit config and restart to use in conversations
3. **Build custom clients:** Create clients with GPT-4, DeepSeek, or other models
4. **Extend functionality:** Add more tools (RFC relationships, citation graphs, etc.)
5. **Deploy to production:** Package as a microservice for your RFC Browser
6. **Optimize costs:** Use cheaper models (DeepSeek) while keeping the same tools

## Resources

- **MCP Protocol Specification:** https://modelcontextprotocol.io/
- **MCP Inspector Tool:** https://github.com/modelcontextprotocol/inspector
- **Claude Agent SDK:** https://platform.claude.com/docs/en/api/agent-sdk/python
- **IETF Datatracker API:** https://datatracker.ietf.org/api/
- **This Project's README:** See README.md for agent usage and architecture

## Key Takeaways

✅ **MCP is model-agnostic** - Works with Claude, GPT-4, Gemini, DeepSeek, and more
✅ **Single source of truth** - Tools defined once, used everywhere
✅ **Vendor independence** - Not locked into any specific LLM provider
✅ **Cost optimization** - Use cheaper models while keeping quality tools
✅ **Future-proof** - Works with new models as they're released
✅ **Production-ready** - Same architecture you'd use in deployment
