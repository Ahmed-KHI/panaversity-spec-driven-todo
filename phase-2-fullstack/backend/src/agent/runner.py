"""
OpenAI Agent runner with MCP tool integration.
[Task]: T-006
[From]: specs/003-phase-iii-chatbot/spec.md §7, plan.md §2.1.3
"""

import openai
import json
from typing import List, Dict, Any, cast
from sqlmodel import Session
from uuid import UUID
from src.mcp.server import get_mcp_tools
from src.mcp import tools as mcp_tools
from src.config import settings


def run_agent(
    session: Session,
    user_id: UUID,
    messages: List[Dict[str, str]]
) -> Dict[str, Any]:
    """
    Run OpenAI agent with conversation history and MCP tools.
    
    Args:
        session: Database session for tool execution
        user_id: User UUID for tool calls (from JWT token)
        messages: Conversation history [{"role": "user/assistant", "content": "..."}]
    
    Returns:
        {
            "response": "Agent's text response",
            "tool_calls": [{"tool": "name", "arguments": {...}, "result": {...}}]
        }
    """
    
    # Configure OpenAI client
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    # System prompt
    system_message = {
        "role": "system",
        "content": """You are a helpful task management assistant. You help users manage their todo list through natural conversation.

Available actions:
- Create tasks when user mentions adding, creating, or remembering something
- List tasks when user asks to see, show, or list their tasks
- Mark tasks complete when user says they finished or completed something
- Update tasks when user wants to change or modify details
- Delete tasks when user wants to remove or cancel them

IMPORTANT: When users reference tasks, they will use the actual task ID number shown in the list.
For example: "complete task #5" or "mark task 3 as done" - use that exact ID number.

Always:
- Be concise and friendly
- Confirm actions with checkmarks (✅)
- When listing tasks, show the actual task ID (e.g., "Task #5: Buy groceries")
- Ask for clarification if ambiguous
- Handle errors gracefully with helpful messages"""
    }
    
    # Build full message history
    full_messages = [system_message] + messages
    
    # Get MCP tool definitions
    tools = get_mcp_tools()
    
    # Call OpenAI Chat Completions API
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # Updated to current stable model (was gpt-4-turbo-preview)
            messages=cast(Any, full_messages),
            tools=cast(Any, tools),
            tool_choice="auto",
            max_tokens=1000,
            temperature=0.7
        )
    except openai.AuthenticationError as e:
        return {
            "response": "⚠️ OpenAI API authentication failed. Please check your API key configuration.",
            "tool_calls": []
        }
    except openai.RateLimitError as e:
        return {
            "response": "⚠️ OpenAI API rate limit exceeded. Please try again in a moment.",
            "tool_calls": []
        }
    except openai.APIConnectionError as e:
        return {
            "response": "⚠️ Could not connect to OpenAI API. Please check your internet connection.",
            "tool_calls": []
        }
    except Exception as e:
        return {
            "response": f"⚠️ AI service error: {str(e)}",
            "tool_calls": []
        }
    
    # Extract response
    assistant_message = response.choices[0].message
    tool_calls_metadata = []
    
    # Handle tool calls if any
    if assistant_message.tool_calls:
        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            
            # CRITICAL: Inject user_id from token (NEVER trust user input)
            tool_args["user_id"] = str(user_id)
            
            # Execute tool
            try:
                if tool_name == "add_task":
                    result = mcp_tools.add_task(
                        session, 
                        UUID(tool_args["user_id"]), 
                        tool_args["title"],
                        tool_args.get("description")
                    )
                elif tool_name == "list_tasks":
                    result = mcp_tools.list_tasks(
                        session, 
                        UUID(tool_args["user_id"]), 
                        tool_args.get("status", "all")
                    )
                elif tool_name == "complete_task":
                    result = mcp_tools.complete_task(
                        session, 
                        UUID(tool_args["user_id"]), 
                        tool_args["task_id"]
                    )
                elif tool_name == "update_task":
                    result = mcp_tools.update_task(
                        session, 
                        UUID(tool_args["user_id"]), 
                        tool_args["task_id"],
                        tool_args.get("title"),
                        tool_args.get("description")
                    )
                elif tool_name == "delete_task":
                    result = mcp_tools.delete_task(
                        session, 
                        UUID(tool_args["user_id"]), 
                        tool_args["task_id"]
                    )
                else:
                    result = {"error": f"Unknown tool: {tool_name}"}
            except Exception as e:
                result = {"error": f"Tool execution failed: {str(e)}"}
            
            # Record tool call
            tool_calls_metadata.append({
                "tool": tool_name,
                "arguments": {k: v for k, v in tool_args.items() if k != "user_id"},  # Don't expose user_id
                "result": result
            })
        
        # Get final response from assistant
        if assistant_message.content:
            response_text = assistant_message.content
        else:
            # Generate confirmation based on tool results
            response_text = _generate_confirmation(tool_calls_metadata)
    else:
        response_text = assistant_message.content if assistant_message.content else "I'm here to help! What would you like to do?"
    
    return {
        "response": response_text,
        "tool_calls": tool_calls_metadata
    }


def _generate_confirmation(tool_calls: List[Dict]) -> str:
    """Generate friendly confirmation message from tool results."""
    if not tool_calls:
        return "I couldn't process that request. Could you try again?"
    
    last_call = tool_calls[-1]
    tool = last_call["tool"]
    result = last_call["result"]
    
    if "error" in result:
        return f"❌ {result['error']}"
    
    if tool == "add_task":
        return f"✅ Added '{result['title']}' to your task list."
    elif tool == "list_tasks":
        count = result["count"]
        if count == 0:
            return "You don't have any tasks yet. Would you like to add one?"
        tasks = result["tasks"]
        tasks_text = "\n".join([
            f"Task #{t['id']}: {t['title']} {'✅' if t['completed'] else '⏳'}"
            for t in tasks
        ])
        return f"Here are your {count} task(s):\n\n{tasks_text}\n\n💡 Use the task number (e.g., 'complete task #{tasks[0]['id']}') to manage them."
    elif tool == "complete_task":
        return f"✅ Marked '{result['title']}' as complete!"
    elif tool == "update_task":
        return f"✅ Updated '{result['title']}'"
    elif tool == "delete_task":
        return f"✅ Deleted '{result['title']}'"
    
    return "Done! ✅"
