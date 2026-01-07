# Ideas MCP Server

MCP (Model Context Protocol) server for the Ideas Execution Loop System. This allows Claude Desktop to manage ideas through natural language.

## Installation

### 1. Install Dependencies

```bash
cd mcp-server
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Claude Desktop

Add to your Claude Desktop config file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ideas": {
      "command": "/path/to/ideas/mcp-server/venv/bin/python",
      "args": ["/path/to/ideas/mcp-server/server.py"]
    }
  }
}
```

Replace `/path/to/ideas` with your actual path.

### 3. Restart Claude Desktop

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

Test the server locally:

```bash
cd mcp-server
source venv/bin/activate
mcp dev server.py
```

This opens the MCP Inspector for debugging.
