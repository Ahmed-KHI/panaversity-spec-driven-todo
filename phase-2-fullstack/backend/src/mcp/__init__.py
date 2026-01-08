"""
MCP (Model Context Protocol) package for AI agent tool integration.
[Task]: T-005
[From]: specs/003-phase-iii-chatbot/spec.md §6
"""

from .server import get_mcp_tools
from . import tools

__all__ = ["get_mcp_tools", "tools"]
