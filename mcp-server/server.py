#!/usr/bin/env python3
"""
Ideas MCP Server - Model Context Protocol server for Ideas Execution Loop System

This MCP server provides tools for AI agents to manage ideas through the Ideas API.
"""

import httpx
from typing import Optional
from mcp.server.fastmcp import FastMCP

# API Configuration
API_BASE_URL = "https://ideas.u.jayliu.co.nz"
AGENT_ID = "claude-mcp-agent"

# Create MCP server
mcp = FastMCP("ideas")

# HTTP client for API calls
def get_client():
    return httpx.Client(base_url=API_BASE_URL, timeout=30.0)


# ============================================================================
# Idea Management Tools
# ============================================================================

@mcp.tool()
def idea_create(content: str) -> str:
    """
    Create a new idea.
    
    Args:
        content: The idea content/description
    
    Returns:
        JSON response with created idea details including id and status
    """
    with get_client() as client:
        response = client.post("/api/ideas", json={"content": content})
        response.raise_for_status()
        return response.text


@mcp.tool()
def idea_list(status_filter: Optional[str] = None) -> str:
    """
    List all ideas, optionally filtered by status.
    
    Args:
        status_filter: Optional status to filter by. 
                      Valid values: draft, pending, claimed, executing, 
                      waiting_user, waiting_agent, completed, failed, cancelled
    
    Returns:
        JSON array of ideas
    """
    with get_client() as client:
        params = {}
        if status_filter:
            params["status_filter"] = status_filter
        response = client.get("/api/ideas", params=params)
        response.raise_for_status()
        return response.text


@mcp.tool()
def idea_get(idea_id: int) -> str:
    """
    Get a single idea with its complete message history.
    
    Args:
        idea_id: The ID of the idea to retrieve
    
    Returns:
        JSON object with idea details and messages array
    """
    with get_client() as client:
        response = client.get(f"/api/ideas/{idea_id}")
        response.raise_for_status()
        return response.text


@mcp.tool()
def idea_update(idea_id: int, content: str) -> str:
    """
    Update an idea's content.
    
    Args:
        idea_id: The ID of the idea to update
        content: The new content for the idea
    
    Returns:
        JSON object with updated idea details
    """
    with get_client() as client:
        response = client.put(f"/api/ideas/{idea_id}", json={"content": content})
        response.raise_for_status()
        return response.text


@mcp.tool()
def idea_execute(idea_id: int) -> str:
    """
    Mark an idea for execution. Changes status from 'draft' to 'pending'.
    This makes the idea available for agents to claim and execute.
    
    Args:
        idea_id: The ID of the idea to execute
    
    Returns:
        JSON object with status change details
    """
    with get_client() as client:
        response = client.post(f"/api/ideas/{idea_id}/execute")
        response.raise_for_status()
        return response.text


@mcp.tool()
def idea_cancel(idea_id: int) -> str:
    """
    Cancel an idea's execution.
    Cannot cancel ideas that are already completed, failed, or cancelled.
    
    Args:
        idea_id: The ID of the idea to cancel
    
    Returns:
        JSON object with status change details
    """
    with get_client() as client:
        response = client.post(f"/api/ideas/{idea_id}/cancel")
        response.raise_for_status()
        return response.text


@mcp.tool()
def idea_reply(idea_id: int, content: str) -> str:
    """
    Add a user message/instruction to an idea's thread.
    If the idea is waiting for user input, this will transition it to waiting_agent.
    
    Args:
        idea_id: The ID of the idea
        content: The message content to add
    
    Returns:
        JSON object with created message details
    """
    with get_client() as client:
        response = client.post(f"/api/ideas/{idea_id}/messages", json={"content": content})
        response.raise_for_status()
        return response.text


# ============================================================================
# Agent Execution Tools
# ============================================================================

@mcp.tool()
def agent_poll() -> str:
    """
    Poll for available tasks. Returns ideas with status 'pending' or 'waiting_agent'.
    
    Returns:
        JSON array of ideas available for execution
    """
    with get_client() as client:
        response = client.get("/api/agent/poll")
        response.raise_for_status()
        return response.text


@mcp.tool()
def agent_claim(idea_id: int) -> str:
    """
    Claim an idea for execution. The idea must be in 'pending' status.
    Once claimed, other agents cannot work on this idea.
    
    Args:
        idea_id: The ID of the idea to claim
    
    Returns:
        JSON object with status change details
    """
    with get_client() as client:
        response = client.post(
            f"/api/agent/claim/{idea_id}",
            json={"agent_id": AGENT_ID}
        )
        response.raise_for_status()
        return response.text


@mcp.tool()
def agent_start(idea_id: int) -> str:
    """
    Start or resume execution of a claimed idea.
    The idea must be in 'claimed' or 'waiting_agent' status.
    
    Args:
        idea_id: The ID of the idea to start executing
    
    Returns:
        JSON object with status change details
    """
    with get_client() as client:
        response = client.post(
            f"/api/agent/start/{idea_id}",
            json={"agent_id": AGENT_ID}
        )
        response.raise_for_status()
        return response.text


@mcp.tool()
def agent_feedback(idea_id: int, content: str) -> str:
    """
    Submit progress feedback during execution.
    The idea must be in 'executing' status.
    
    Args:
        idea_id: The ID of the idea
        content: Feedback content describing current progress
    
    Returns:
        JSON object confirming feedback was recorded
    """
    with get_client() as client:
        response = client.post(
            f"/api/agent/feedback/{idea_id}",
            json={"agent_id": AGENT_ID, "content": content}
        )
        response.raise_for_status()
        return response.text


@mcp.tool()
def agent_ask(idea_id: int, question: str) -> str:
    """
    Request user input/decision. Pauses execution and waits for user response.
    The idea must be in 'executing' status.
    
    Args:
        idea_id: The ID of the idea
        question: The question or request for the user
    
    Returns:
        JSON object with status change to 'waiting_user'
    """
    with get_client() as client:
        response = client.post(
            f"/api/agent/ask/{idea_id}",
            json={"agent_id": AGENT_ID, "question": question}
        )
        response.raise_for_status()
        return response.text


@mcp.tool()
def agent_complete(idea_id: int, summary: Optional[str] = None) -> str:
    """
    Mark an idea as completed.
    The idea must be in 'executing' status.
    
    Args:
        idea_id: The ID of the idea
        summary: Optional summary of what was accomplished
    
    Returns:
        JSON object with status change to 'completed'
    """
    with get_client() as client:
        payload = {"agent_id": AGENT_ID}
        if summary:
            payload["summary"] = summary
        response = client.post(f"/api/agent/complete/{idea_id}", json=payload)
        response.raise_for_status()
        return response.text


@mcp.tool()
def agent_fail(idea_id: int, reason: str) -> str:
    """
    Mark an idea as failed.
    The idea must be in 'executing' status.
    
    Args:
        idea_id: The ID of the idea
        reason: Explanation of why the task failed
    
    Returns:
        JSON object with status change to 'failed'
    """
    with get_client() as client:
        response = client.post(
            f"/api/agent/fail/{idea_id}",
            json={"agent_id": AGENT_ID, "reason": reason}
        )
        response.raise_for_status()
        return response.text


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    mcp.run()
