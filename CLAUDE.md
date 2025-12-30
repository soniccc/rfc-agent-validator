# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

An AI-powered RFC analysis agent demonstrating empirical validation of architectural approaches: custom API tools vs WebSearch-only vs MCP server patterns. This project validates that custom tools provide superior structured output for production use cases.

## Three Implementation Variants

1. **`main.py`** - Full agent using external MCP server (`rfc_mcp_server.py`)
   - Production architecture with clean separation of concerns
   - Agent logic separate from tool implementation

2. **`main_simple.py`** - Simplified agent using only WebSearch/WebFetch
   - Validation tool to empirically test if custom tools add value
   - Real-world testing confirmed custom tools produce superior structured output

3. **`rfc_mcp_server.py`** - Standalone MCP server (model-agnostic)
   - Reusable tool service for any MCP client (Claude Desktop, custom clients)
   - Works with any LLM supporting function calling (Claude, GPT-4, Gemini, DeepSeek, etc.)

## Development Commands

### Environment Setup

```bash
# Install dependencies (fast, uses uv.lock for reproducibility)
uv sync

# Verify Python version
uv run python --version

# Check installed dependencies
uv pip list
```

### Running the Agents

```bash
# Run full agent (custom API tools via MCP server)
uv run python main.py

# Run simplified agent (WebSearch/WebFetch only)
uv run python main_simple.py

# Run standalone MCP server (for testing/debugging)
uv run python rfc_mcp_server.py
```

### Testing & Validation

```bash
# Syntax verification
uv run python -m py_compile main.py
uv run python -m py_compile main_simple.py
uv run python -m py_compile rfc_mcp_server.py

# Test MCP server with interactive inspector
npx @modelcontextprotocol/inspector uv run python rfc_mcp_server.py

# Manual MCP server protocol test
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | uv run python rfc_mcp_server.py
```

### Environment Variables

Required: `ANTHROPIC_API_KEY` - Get from https://console.anthropic.com/

```bash
# Set via .env file
cp .env.example .env
# Edit .env and add your key

# Or export directly
export ANTHROPIC_API_KEY='your_api_key_here'
```

## Architecture

### Full Version Architecture (`main.py`)

```
┌─────────────────────┐
│   main.py           │  ← Conversational agent (ClaudeSDKClient)
│   (Claude Agent)    │
└──────────┬──────────┘
           │ MCP Protocol (stdio)
           │
┌──────────▼──────────┐
│ rfc_mcp_server.py   │  ← External tool server (spawned as subprocess)
│ - search_rfcs       │     Single source of truth for tools
│ - get_rfc           │
│ - get_rfc_text      │
└──────────┬──────────┘
           │ HTTPS
           │
┌──────────▼──────────────────┐
│ IETF Datatracker API        │
│ datatracker.ietf.org/api/v1 │
│ www.rfc-editor.org/rfc/     │
└─────────────────────────────┘
```

**Key Design Decisions:**

- **MCP server spawned as subprocess**: Agent spawns `rfc_mcp_server.py` using `uv run python`
- **Stdio communication**: MCP protocol uses stdin/stdout, not HTTP
- **Tool naming**: MCP tools prefixed with `mcp__<server_name>__<tool_name>` (e.g., `mcp__rfc__search_rfcs`)
- **Separation of concerns**: Agent logic in `main.py`, tool implementation in `rfc_mcp_server.py`
- **Reusability**: Same MCP server used by agent, Claude Desktop, and custom clients

### MCP Server Design (`rfc_mcp_server.py`)

**Model-agnostic tool provider:**
- Implements MCP protocol using `mcp.server` package
- Three tools: `search_rfcs`, `get_rfc`, `get_rfc_text`
- Stateless - each tool call is independent
- Uses `httpx` for async HTTP requests to IETF Datatracker API
- Returns structured `TextContent` responses

**Integration points:**
- Claude Desktop: Add to `~/Library/Application Support/Claude/claude_desktop_config.json`
- Custom clients: Spawn as subprocess, communicate via MCP protocol
- Works with any LLM: Claude, GPT-4, Gemini, DeepSeek, local models

## Tool Definitions

### `search_rfcs`
- **API**: `GET https://datatracker.ietf.org/api/v1/doc/document/?name__icontains={query}`
- **Returns**: Structured list of RFCs with titles and abstracts
- **Limit**: Default 10 results, configurable

### `get_rfc`
- **API**: `GET https://datatracker.ietf.org/api/v1/doc/document/rfc{number}/`
- **Returns**: Full RFC metadata (authors, pages, stream, standard level, abstract)
- **Handles**: Various RFC identifier formats (7540, RFC7540, rfc7540)

### `get_rfc_text`
- **API**: `GET https://www.rfc-editor.org/rfc/rfc{number}.txt`
- **Returns**: Complete RFC text content
- **Limit**: Truncates at 50,000 characters if necessary

## Key Implementation Details

### Agent Conversation Loop (`main.py`)

- Uses `ClaudeSDKClient` async context manager
- Maintains conversation history across turns
- Supports special commands: `exit`, `quit`, `new` (clears history)
- System prompt emphasizes FULL ACCESS to RFC tools (no artificial restrictions)

### MCP Server Startup

```python
# In main.py - how MCP server is configured
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
)
```

### Error Handling

- HTTP errors from IETF API are caught and returned as user-friendly messages
- RFC number normalization handles various input formats
- Connection errors suggest checking network or API availability

## Empirical Validation Findings

**Key Question**: Do custom API tools actually add value vs frontier LLM with WebSearch?

**Answer** (from real-world testing):
- **Custom tools version** (`main.py`): Structured, consistent output; predictable field formatting
- **WebSearch version** (`main_simple.py`): Technically correct but unstructured; varying format each time

**Use Cases**:
- **Production (e.g., FastAPI RFC Browser)**: Custom tools essential for structured JSON responses
- **Personal research**: WebSearch version surprisingly effective for ad-hoc exploration
- **Bottom line**: Build custom tools when structured, consistent output matters

## Adding New Tools

To add a new RFC tool to the MCP server:

1. **Add tool definition** in `rfc_mcp_server.py` → `list_tools()`:
   ```python
   Tool(
       name="new_tool",
       description="Tool description",
       inputSchema={...}
   )
   ```

2. **Implement handler function**:
   ```python
   async def new_tool(args: dict[str, Any]) -> list[TextContent]:
       # Implementation
       return [TextContent(type="text", text=result)]
   ```

3. **Add to dispatcher** in `call_tool()`:
   ```python
   elif name == "new_tool":
       return await new_tool(arguments)
   ```

4. **Update allowed_tools** in `main.py`:
   ```python
   allowed_tools=[
       # ... existing tools ...
       "mcp__rfc__new_tool",
   ]
   ```

All clients (agent, Claude Desktop, custom clients) automatically get the new tool.

## Dependencies

**Core dependencies** (see `pyproject.toml`):
- `claude-agent-sdk>=0.1.18` - Claude Agent SDK for building conversational agents
- `httpx>=0.27.0` - Modern async HTTP client for API requests

**Implicit dependencies** (from SDK):
- `mcp` - Model Context Protocol implementation
- Standard library: `asyncio`, `os`, `pathlib`, `json`

**Package manager**: Uses `uv` for 10-100x faster installs and deterministic dependency resolution via `uv.lock`

## Configuration Files

- **`pyproject.toml`**: Project metadata and dependencies
- **`uv.lock`**: Locked dependency versions (commit this)
- **`.env`**: API keys (NEVER commit this)
- **`.env.example`**: Template for environment variables

## External Integrations

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "rfc-tools": {
      "command": "uv",
      "args": ["run", "python", "/absolute/path/to/rfc_mcp_server.py"]
    }
  }
}
```

### Custom LLM Clients

The MCP server works with any LLM supporting function calling:
- OpenAI GPT-4: Use OpenAI SDK with MCP tool discovery
- DeepSeek: OpenAI-compatible API, cheaper for production
- Google Gemini: Use Gemini SDK with MCP tools
- Local models: Llama 3+, Mistral via adapters

## Production Considerations

**For FastAPI RFC Browser or similar:**
- Use DeepSeek instead of Claude for cost optimization (same tools, 90% cheaper)
- Deploy `rfc_mcp_server.py` as microservice
- Horizontally scalable (stateless design)
- Consider caching RFC responses (RFCs rarely change)

**Model Selection**:
- Development/testing: Claude Sonnet (best quality)
- Production: DeepSeek (best cost/performance)
- High complexity: Claude Opus (premium quality)

## Common Patterns

**Making changes that affect tools:**
1. Modify `rfc_mcp_server.py` only (single source of truth)
2. Test with MCP Inspector
3. Restart agent or Claude Desktop to pick up changes
4. No changes needed in `main.py` for tool modifications

**Testing different architectures:**
```bash
# Terminal 1: Full version
uv run python main.py

# Terminal 2: Simplified version (same query)
uv run python main_simple.py

# Compare output structure and quality
```

## Troubleshooting

**"ModuleNotFoundError: No module named 'claude_agent_sdk'"**
- Run `uv sync` to install dependencies

**"ANTHROPIC_API_KEY environment variable not set"**
- Create `.env` file or export variable

**MCP server not connecting:**
- Test manually: `npx @modelcontextprotocol/inspector uv run python rfc_mcp_server.py`
- Check absolute paths in config
- Verify `uv` is in PATH

**Claude Desktop doesn't show tools:**
- Use absolute paths (not relative) in config
- Restart Claude Desktop completely
- Check JSON syntax is valid
