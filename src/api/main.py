import asyncio
import os
from concurrent.futures import ThreadPoolExecutor

#from fastapi import FastAPI
#from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agentrun import AgentRun
from fastmcp import FastMCP


class CodeSchema(BaseModel):
    code: str


class OutputSchema(BaseModel):
    output: str


# Create the MCP server instance
mcp = FastMCP("Code MCP Server")

@mcp.tool()
async def execute_code(code: str) -> OutputSchema:
    """Execute Python code in a sandbox environment
    
    Args:
        code: The Python code to execute
    """
    # AgentRun 
    runner = AgentRun(
        container_name=os.environ.get("CONTAINER_NAME", "code_act_python_runner_1"),  # Default container name
        cached_dependencies=[],
        default_timeout=60 * 5,
    )
    python_code = code
    with ThreadPoolExecutor() as executor:
        future = executor.submit(runner.execute_code_in_container, python_code)
        output = await asyncio.wrap_future(future)
    return OutputSchema(output=output)


