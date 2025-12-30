# RFC Analysis Agent

An AI-powered conversational agent for searching, browsing, and analyzing IETF RFCs using Claude.

**Includes empirical validation:** This project deliberately implements both custom API tools AND a simplified WebSearch-only version to test which approach produces better results. Real-world testing confirmed custom tools provide superior structured output.

## Three Ways to Use This Project

This project provides **three different implementations** demonstrating different architectural approaches:

### 1. Full Agent (`main.py`) - Uses External MCP Server
- Complete conversational RFC assistant
- Connects to `rfc_mcp_server.py` for RFC tools
- Clean separation of concerns (agent logic vs tool implementation)
- Best for: **Production use, modular architecture**

### 2. Simplified Agent (`main_simple.py`) - Built-in Tools Only
- **Validation tool** - Created to test if custom tools actually add value
- Uses only WebSearch and WebFetch (no custom API integration)
- Relies on Claude's knowledge + web access
- **Real-world testing proved custom tools produce clearer, more structured output**
- Best for: **Quick prototypes, personal use, learning, comparison testing**

### 3. MCP Server (`rfc_mcp_server.py`) - Reusable Tool Service
- Standalone server exposing RFC tools via MCP protocol
- Can be used by Claude Desktop, other agents, any MCP client
- Stateless, reusable across multiple applications
- Best for: **Sharing tools, Claude Desktop integration, microservices**

See [MCP_SERVER.md](MCP_SERVER.md) for detailed instructions on running the MCP server.

**Try all three to see the architectural trade-offs!** Run both `main.py` and `main_simple.py` side-by-side with the same query to validate the structured output benefits yourself.

## Features

- **Search RFCs**: Search through IETF RFCs by keywords or topics
- **Fetch RFC Details**: Retrieve comprehensive metadata and abstracts for specific RFCs
- **Read RFC Content**: Fetch and analyze full RFC text content
- **AI-Powered Analysis**: Ask questions, compare RFCs, and get expert explanations
- **Conversational Interface**: Maintain context across multiple queries in a session

## Tech Stack

- **Python 3.12+**: Modern Python with async/await support
- **Claude Agent SDK**: Official SDK for building AI agents with Claude
- **IETF Datatracker API**: Official API for RFC metadata and documents
- **httpx**: Modern async HTTP client for API requests
- **uv**: Fast Python package manager

## Prerequisites

- Python 3.12 or higher
- Claude Code CLI (installed via npm or homebrew)
- Anthropic API key

## Installation

### 1. Clone or navigate to the project directory

```bash
cd rfc-agent-validator
```

### 2. Install Claude Code CLI

Choose one of the following methods:

**Using npm:**
```bash
npm install -g @anthropic-ai/claude-code
```

**Using Homebrew (macOS):**
```bash
brew install --cask claude-code
```

**Using curl (macOS/Linux/WSL):**
```bash
curl -fsSL https://claude.ai/install.sh | bash
```

### 3. Install Python dependencies

Using `uv` (recommended):
```bash
uv sync
```

Or using pip:
```bash
pip install -r requirements.txt
```

### 4. Set up your API key

Get your Anthropic API key from [https://console.anthropic.com/](https://console.anthropic.com/)

Create a `.env` file:
```bash
cp .env.example .env
```

Edit `.env` and add your API key:
```
ANTHROPIC_API_KEY=your_api_key_here
```

Or export it directly:
```bash
export ANTHROPIC_API_KEY='your_api_key_here'
```

## Usage

### Running the Agents

**Full Version (Custom API Tools):**
```bash
uv run python main.py
```

**Simplified Version (Built-in Tools Only):**
```bash
uv run python main_simple.py
```

Or with your virtual environment activated:
```bash
python main.py           # Full version
python main_simple.py    # Simplified version
```

### Interactive Commands

Once the agent starts, you can interact with it using natural language:

**Search for RFCs:**
```
You: Find RFCs about HTTP/2
```

**Get RFC details:**
```
You: Tell me about RFC 7540
```

**Analyze RFC content:**
```
You: What are the main security considerations in RFC 7540?
```

**Compare RFCs:**
```
You: How does HTTP/2 differ from HTTP/3?
```

### Special Commands

- `exit` or `quit`: End the session
- `new`: Start a fresh conversation (clears context)

## How It Works

### Architecture

```
┌─────────────────────┐
│   main.py           │  ← Conversational agent
│   (Claude Agent)    │
└──────────┬──────────┘
           │ MCP Protocol
           │
┌──────────▼──────────┐
│ rfc_mcp_server.py   │  ← External tool server
│ - search_rfcs       │
│ - get_rfc           │
│ - get_rfc_text      │
└──────────┬──────────┘
           │ HTTPS
           │
┌──────────▼──────────────────┐
│ IETF Datatracker API        │
│ datatracker.ietf.org/api/v1 │
└─────────────────────────────┘
```

**Benefits of this architecture:**
- ✅ **Single source of truth** - Tools defined once in `rfc_mcp_server.py`
- ✅ **Reusable** - Same server used by agent, Claude Desktop, other clients
- ✅ **Modular** - Agent logic separate from tool implementation
- ✅ **Production-ready** - Mirrors how you'd deploy in real systems

The agent (`main.py`) connects to the external MCP server (`rfc_mcp_server.py`), which provides three tools:

1. **search_rfcs**: Searches the IETF Datatracker API for RFCs matching keywords
2. **get_rfc**: Fetches detailed metadata and abstracts for specific RFCs
3. **get_rfc_text**: Retrieves full RFC text content from the official RFC repository

## Example Session

```
============================================================
RFC Analysis Agent
============================================================

AI-powered assistant for IETF RFC research and analysis

Commands:
  - Type your question or request
  - 'exit' or 'quit' to end the session
  - 'new' to start a fresh conversation
============================================================

[Turn 1] You: Find RFCs about DNS security

[Turn 1] Agent: I'll search for RFCs related to DNS security...
Found 10 RFCs matching 'dnssec':

**rfc4033** - DNS Security Introduction and Requirements
This document introduces DNS Security Extensions (DNSSEC)...

**rfc4034** - Resource Records for DNS Security Extensions
This document describes the DNS resource records used in DNSSEC...

[Turn 2] You: Tell me more about RFC 4033

[Turn 2] Agent: Let me fetch the details for RFC 4033...

# RFC4033: DNS Security Introduction and Requirements

## Metadata
- **Authors**: R. Arends, R. Austein, M. Larson, D. Massey, S. Rose
- **Pages**: 21
- **Stream**: IETF
- **Standard Level**: Proposed Standard

## Abstract
This document introduces DNS Security Extensions (DNSSEC). It describes the
DNS security problem and the DNSSEC solution architecture...
```

## Project Structure

```
rfc-agent-validator/
├── main.py              # Full agent with custom tools (conversational)
├── main_simple.py       # Simplified agent with built-in tools only
├── rfc_mcp_server.py    # Standalone MCP server for tool sharing
├── pyproject.toml       # Project dependencies and metadata
├── .env.example         # Example environment variables
├── .gitignore           # Git ignore rules
├── README.md            # This file
├── MCP_SERVER.md        # MCP server usage guide
└── .venv/               # Virtual environment (created by uv)
```

## Configuration

### Agent Configuration (`main.py`)

The agent connects to the external MCP server:

```python
# Get path to MCP server
current_dir = Path(__file__).parent.absolute()
mcp_server_path = current_dir / "rfc_mcp_server.py"

# Configure agent to use external server
options = ClaudeAgentOptions(
    system_prompt=RFC_SYSTEM_PROMPT,
    model="sonnet",
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
```

**Key points:**
- Tools are implemented in `rfc_mcp_server.py` (single source of truth)
- Agent spawns the MCP server as a subprocess
- Same server can be used by Claude Desktop or other clients
- Update tools once, all clients benefit

### MCP Server Tools

Tools are defined in `rfc_mcp_server.py` using the MCP protocol.
See [MCP_SERVER.md](MCP_SERVER.md) for implementation details and how to use the server standalone.

## API Endpoints Used

- **IETF Datatracker API**: `https://datatracker.ietf.org/api/v1/doc/document/`
- **RFC Text Repository**: `https://www.rfc-editor.org/rfc/rfc{number}.txt`

## Troubleshooting

### "ANTHROPIC_API_KEY environment variable not set"

Make sure you've created a `.env` file with your API key or exported it:
```bash
export ANTHROPIC_API_KEY='your_api_key_here'
```

### "Claude Code CLI not found"

Install the Claude Code CLI:
```bash
npm install -g @anthropic-ai/claude-code
```

### Import errors

Make sure dependencies are installed:
```bash
uv sync
```

## Development

### Running Tests

```bash
# Verify agent syntax
uv run python -m py_compile main.py
uv run python -m py_compile main_simple.py

# Verify MCP server
uv run python -m py_compile rfc_mcp_server.py

# Test MCP server with inspector
npx @modelcontextprotocol/inspector uv run python rfc_mcp_server.py
```

### Adding New Tools

To add new RFC tools:

1. Edit `rfc_mcp_server.py`:
   - Add tool definition to `list_tools()`
   - Implement the tool handler function
   - Add case to `call_tool()`

2. Update `main.py`:
   - Add tool name to `allowed_tools` (e.g., `"mcp__rfc__new_tool"`)

3. Both the agent AND Claude Desktop will automatically get the new tool

**Example:**
```python
# In rfc_mcp_server.py
@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        # ... existing tools ...
        Tool(
            name="compare_rfcs",
            description="Compare two RFCs side by side",
            inputSchema={"type": "object", "properties": {...}}
        )
    ]
```

## Comparison: Full vs Simplified

### Empirical Validation: Why We Built Both

**`main_simple.py` was created as a validation tool** to answer the question: "Do custom API tools actually add value, or can a frontier LLM handle this with just WebSearch/WebFetch?"

**Result:** Real-world testing confirmed custom tools produce **significantly better output**.

### The Key Difference: Structure vs Flexibility

The real difference between these versions isn't just **data access** - it's about **structured, consistent output**:

**Full Version (Custom API Tools):**
```
# RFC7540: Hypertext Transfer Protocol Version 2 (HTTP/2)

## Metadata
- **Authors**: M. Belshe, R. Peon, M. Thomson
- **Pages**: 96
- **Stream**: IETF
- **Standard Level**: Proposed Standard

## Abstract
[Consistently formatted abstract here...]
```
→ Same structure every time, predictable fields, flows logically

**Simplified Version (WebSearch/WebFetch):**
```
Claude outputs: "RFC 7540 is the HTTP/2 specification. It was written by
Mike Belshe and others in 2015. The document describes..."
```
→ Free-form output, varies each time, harder to parse programmatically

### When to Use Full Version (`main.py`)

✅ **Use when:**
- **Building a production application or API** - Your FastAPI needs consistent JSON responses
- **Structured output matters** - Frontend expects predictable field names and types
- **Better UX/flow** - Information presented logically and consistently
- Need reliable, structured metadata (authors, publication dates, status)
- Querying obscure or recent RFCs (post-April 2024)
- Performing bulk operations or systematic RFC analysis
- Integrating into a larger system (e.g., your FastAPI RFC Browser)
- Data accuracy is critical

❌ **Drawbacks:**
- More complex code (~340 lines vs ~130 lines)
- Requires httpx dependency
- Custom MCP tools need maintenance

### When to Use Simplified Version (`main_simple.py`)

✅ **Use when:**
- **Ad-hoc research and exploration** - Free-form output is actually better for conversation
- Quick prototyping or personal research
- Researching well-known RFCs (HTTP, DNS, TLS, etc.)
- Learning the Claude Agent SDK
- Don't need structured data output
- Want minimal dependencies

❌ **Limitations:**
- **Inconsistent formatting** - Output varies, LLM decides presentation each time
- **Harder to parse** - "The LLM mentioned authors... somewhere in this text?"
- No guaranteed metadata accuracy (may hallucinate)
- Web search can be slower than direct API
- Less suitable for programmatic/bulk operations
- May struggle with very recent or obscure RFCs

### Real-World Test Results

Try both with these queries to see the difference:

```
1. "Find RFCs about QUIC protocol"
   - Full: Structured search with exact metadata
   - Simple: Web search, may miss some results

2. "Tell me about RFC 9000"
   - Full: Direct API fetch, guaranteed accurate
   - Simple: Web fetch or training data, usually accurate

3. "What RFCs were published in December 2024?"
   - Full: Can query by date filters
   - Simple: Must rely on web search results

4. "Compare RFC 793 and RFC 9293" (TCP specs)
   - Both work well - Claude knows these from training
```

### Bottom Line: When Custom Tools Actually Matter

**We Built Both Versions to Find Out - Here's What We Learned:**

This project includes `main_simple.py` as a **deliberate validation experiment**. The question was: "Do custom API tools actually add value, or can Claude Sonnet handle RFC queries well enough with just WebSearch/WebFetch?"

**The Answer (from Real Testing):**

Custom tools aren't just about *getting* the data (frontier LLMs can do that via web). They're about:

1. ✅ **Structured Output** - Consistent format every single time
2. ✅ **Predictable Fields** - Always get authors, title, abstract in the same place
3. ✅ **Better Information Flow** - Data presented logically, not scattered in prose
4. ✅ **Production Integration** - Your FastAPI can parse responses reliably
5. ✅ **Superior UX** - Users get clean, scannable information

**Real-World Testing Results (Side-by-Side Comparison):**
- **Custom tools version** (main.py): **Structured flow** - easy to read, consistent formatting, information flows logically
- **WebSearch version** (main_simple.py): **Throws information** - technically correct, but unstructured, varying format each time

*Quote from testing:* "The Datatracker API method was more structured and easier to read. It flowed whereas the other script output was more like throwing information at me."

**When to Use Which:**

**For production (RFC Browser):** Full version is essential. Your React frontend needs predictable JSON structure, not "Claude mentioned the authors somewhere in this paragraph."

**For personal research:** Simplified version works surprisingly well! Free-form conversation is actually nice for ad-hoc exploration. Claude Sonnet knows most major RFCs.

**The Validated Lesson:** Don't build custom tools just because you can. Build them when **structured, consistent output** matters for your use case. We tested both approaches empirically - custom tools won for production use.

## Resources

- [Claude Agent SDK Documentation](https://platform.claude.com/docs/en/api/agent-sdk/python)
- [IETF Datatracker API](https://datatracker.ietf.org/api/)
- [Anthropic API Console](https://console.anthropic.com/)

## License

MIT

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.
