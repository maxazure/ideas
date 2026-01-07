# Ideas MCP Server

MCP (Model Context Protocol) server for the Ideas Execution Loop System. This allows Claude Desktop to manage ideas through natural language.

## Installation

### Option 1: Install as pip package (Recommended)

```bash
# Build from source
cd /path/to/ideas/mcp-server
pip install build
python -m build

# Install the wheel
pip install dist/ideas_mcp-1.0.0-py3-none-any.whl

# Or install from source
pip install dist/ideas_mcp-1.0.0.tar.gz
```

The package provides the `ideas-mcp` command:

```bash
ideas-mcp --help
```

### Option 2: From source (Development)

```bash
cd mcp-server
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Configure Claude Desktop

### Option 1: If installed as pip package

```json
{
  "mcpServers": {
    "ideas": {
      "command": "/full/path/to/venv/bin/python",
      "args": ["-m", "ideas_mcp.server"]
    }
  }
}
```

### Option 2: From source

```json
{
  "mcpServers": {
    "ideas": {
      "command": "/full/path/to/ideas/mcp-server/venv/bin/python",
      "args": ["-m", "ideas_mcp.server"]
    }
  }
}
```

**Config file locations:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

### Restart Claude Desktop

After updating the config, restart Claude Desktop to load the MCP server.

## Available Tools

### Idea Management

| Tool | Description |
|------|-------------|
| `idea_create` | Create a new idea |
| `idea_list` | List all ideas (optional status filter) |
| `idea_get` | Get idea details with message history |
| `idea_update` | Update idea content |
| `idea_execute` | Mark idea for execution (draft -> pending) |
| `idea_cancel` | Cancel idea execution |
| `idea_reply` | Add user message/instruction to idea |

### Agent Execution

| Tool | Description |
|------|-------------|
| `agent_poll` | Poll for available tasks |
| `agent_claim` | Claim a task for execution |
| `agent_start` | Start/resume task execution |
| `agent_feedback` | Submit progress feedback |
| `agent_ask` | Request user input (pause execution) |
| `agent_complete` | Mark task as completed |
| `agent_fail` | Mark task as failed |

## Example Usage in Claude

```
Create a new idea: "Build a REST API for user management"
```

```
Show me all pending ideas
```

```
Execute idea #1
```

```
What's the status of idea #3?
```

## API Endpoint

The MCP server connects to: `https://ideas.u.jayliu.co.nz`

## Development

### Test the server locally

```bash
cd mcp-server
source venv/bin/activate
mcp dev src/ideas_mcp/server.py
```

This opens the MCP Inspector for debugging.

### Build new package version

```bash
cd mcp-server
rm -rf dist build *.egg-info
python -m build
pip install dist/ideas_mcp-*.whl --force-reinstall
```

## Package Structure

```
mcp-server/
├── pyproject.toml              # Package configuration
├── src/ideas_mcp/
│   ├── __init__.py
│   └── server.py              # MCP server with 14 tools
├── README.md
└── dist/
    ├── ideas_mcp-1.0.0-py3-none-any.whl
    └── ideas_mcp-1.0.0.tar.gz
```

## Requirements

- Python 3.10+
- mcp>=1.0.0
- httpx>=0.28.0
