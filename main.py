#!/usr/bin/env python3
"""
Complete MCP Server Example using FastMCP
This server provides both resources and tools that can be tested with any MCP client.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional
from fastmcp import FastMCP, Context
from pydantic import BaseModel

# Create the MCP server instance
mcp = FastMCP("Demo MCP Server")

# In-memory data store for demonstration
users_db = {
    "1": {"id": "1", "name": "Alice Johnson", "email": "alice@example.com", "role": "admin"},
    "2": {"id": "2", "name": "Bob Smith", "email": "bob@example.com", "role": "user"},
    "3": {"id": "3", "name": "Charlie Brown", "email": "charlie@example.com", "role": "user"}
}

documents_db = {
    "doc1": {"id": "doc1", "title": "Welcome Guide", "content": "Welcome to our platform!", "updated": "2024-01-01"},
    "doc2": {"id": "doc2", "title": "API Documentation", "content": "Here's how to use our API...", "updated": "2024-01-15"}
}

# Pydantic models for complex data
class User(BaseModel):
    id: str
    name: str
    email: str
    role: str

class Document(BaseModel):
    id: str
    title: str
    content: str
    updated: str

# RESOURCES (Read-only data access)

@mcp.resource("data://server-info")
async def get_server_info():
    """Get general information about this MCP server"""
    return {
        "name": "Demo MCP Server",
        "version": "1.0.0",
        "description": "A demonstration MCP server with users and documents",
        "capabilities": ["user management", "document management", "progress reporting"],
        "uptime": datetime.now().isoformat()
    }

@mcp.resource("data://users")
async def get_all_users():
    """Get a list of all users in the system"""
    return {
        "users": list(users_db.values()),
        "total_count": len(users_db)
    }

@mcp.resource("data://user/{user_id}")
async def get_user_profile(user_id: str):
    """Get detailed information about a specific user"""
    if user_id not in users_db:
        raise ValueError(f"User with ID '{user_id}' not found")
    
    user = users_db[user_id]
    return {
        "user": user,
        "last_accessed": datetime.now().isoformat(),
        "permissions": ["read", "write"] if user["role"] == "admin" else ["read"]
    }

@mcp.resource("data://documents")
async def get_all_documents():
    """Get a list of all documents"""
    return {
        "documents": list(documents_db.values()),
        "total_count": len(documents_db)
    }

@mcp.resource("data://document/{doc_id}")
async def get_document(doc_id: str):
    """Get a specific document by ID"""
    if doc_id not in documents_db:
        raise ValueError(f"Document with ID '{doc_id}' not found")
    
    return documents_db[doc_id]

# TOOLS (Actions that modify data or perform operations)

@mcp.tool()
async def create_user(name: str, email: str, role: str = "user"):
    """Create a new user in the system"""
    if role not in ["user", "admin"]:
        raise ValueError("Role must be either 'user' or 'admin'")
    
    # Generate a simple ID
    user_id = str(len(users_db) + 1)
    
    new_user = {
        "id": user_id,
        "name": name,
        "email": email,
        "role": role
    }
    
    users_db[user_id] = new_user
    return f"User '{name}' created successfully with ID: {user_id}"

@mcp.tool()
async def update_document(doc_id: str, title: Optional[str] = None, content: Optional[str] = None):
    """Update an existing document's title or content"""
    if doc_id not in documents_db:
        raise ValueError(f"Document with ID '{doc_id}' not found")
    
    document = documents_db[doc_id]
    
    if title:
        document["title"] = title
    if content:
        document["content"] = content
    
    document["updated"] = datetime.now().isoformat()
    
    return f"Document '{doc_id}' updated successfully"

@mcp.tool()
async def delete_user(user_id: str):
    """Delete a user from the system"""
    if user_id not in users_db:
        raise ValueError(f"User with ID '{user_id}' not found")
    
    user_name = users_db[user_id]["name"]
    del users_db[user_id]
    
    return f"User '{user_name}' (ID: {user_id}) deleted successfully"

@mcp.tool()
async def search_documents(query: str):
    """Search for documents containing the specified query"""
    results = []
    
    for doc_id, doc in documents_db.items():
        if query.lower() in doc["title"].lower() or query.lower() in doc["content"].lower():
            results.append({
                "id": doc_id,
                "title": doc["title"],
                "relevance": "title" if query.lower() in doc["title"].lower() else "content"
            })
    
    return {
        "query": query,
        "results": results,
        "total_found": len(results)
    }

@mcp.tool()
async def simulate_long_task(duration: int, ctx: Context):
    """Simulate a long-running task with progress reporting"""
    if duration < 1 or duration > 30:
        raise ValueError("Duration must be between 1 and 30 seconds")
    
    steps = min(duration * 2, 20)  # Update progress every 0.5 seconds, max 20 updates
    
    for i in range(steps + 1):
        progress = i / steps
        await ctx.report_progress(i, steps)
        
        if i < steps:
            await asyncio.sleep(duration / steps)
    
    return f"Long task completed! Ran for {duration} seconds with {steps} progress updates."

@mcp.tool()
async def get_system_stats():
    """Get current system statistics"""
    return {
        "users_count": len(users_db),
        "documents_count": len(documents_db),
        "admin_users": len([u for u in users_db.values() if u["role"] == "admin"]),
        "timestamp": datetime.now().isoformat(),
        "memory_usage": {
            "users_db_size": len(str(users_db)),
            "documents_db_size": len(str(documents_db))
        }
    }

@mcp.tool()
async def get_all_users_tool():
    """Get a list of all users in the system (as a tool)"""
    return {
        "users": list(users_db.values()),
        "total_count": len(users_db)
    }

@mcp.tool()
async def execute_code(code: str):
    """Execute given Python code and return the output or error. (Highly restricted environment)"""
    import io
    import contextlib

    # Restrict builtins
    safe_builtins = {"print": print}
    local_vars = {}
    stdout = io.StringIO()
    error = None
    
    try:
        with contextlib.redirect_stdout(stdout):
            exec(code, {"__builtins__": safe_builtins}, local_vars)
    except Exception as e:
        error = str(e)
    
    return {
        "output": stdout.getvalue(),
        "error": error
    }

# MAIN - Run the server
if __name__ == "__main__":
    import sys
    
    # Check if we should run with SSE transport (for web access)
    if len(sys.argv) > 1 and sys.argv[1] == "--sse":
        print("🚀 Starting MCP Server with SSE transport on http://localhost:8000")
        print("📡 You can connect MCP clients to: http://localhost:8000/sse")
        print("🔍 Available resources:")
        print("   - data://server-info")
        print("   - data://users")
        print("   - data://user/{user_id}")
        print("   - data://documents")
        print("   - data://document/{doc_id}")
        print("🛠️  Available tools:")
        print("   - create_user")
        print("   - update_document")
        print("   - delete_user")
        print("   - search_documents")
        print("   - simulate_long_task")
        print("   - get_system_stats")
        print("   - get_all_users_tool")
        print("\nPress Ctrl+C to stop the server")
        
        mcp.run(transport="sse", port=8000)
    else:
        print("🚀 Starting MCP Server with STDIO transport")
        print("📝 This mode is for integration with tools like Claude Desktop")
        print("💡 To run with web access, use: python script.py --sse")
        
        mcp.run()