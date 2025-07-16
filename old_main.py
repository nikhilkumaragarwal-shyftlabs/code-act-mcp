from fastmcp import FastMCP
from llm_sandbox import SandboxSession
# local imports
from utils import get_approved_libraries

# Create the MCP server instance
mcp = FastMCP("Code MCP Server")

@mcp.tool()
async def execute_code(code: str) -> str:
    """Execute Python code in a sandbox environment
    
    Args:
        code: The Python code to execute
    """
    approved_libs = get_approved_libraries()
    print(approved_libs)
    # Check code for library names
    for lib in approved_libs:
        if lib in code:
            # If library name found in code but not approved, return error
            if lib not in approved_libs:
                return f"Error: Attempting to use non-approved library '{lib}'. Only pre-approved libraries are allowed."
    print("Code is approved")
    with SandboxSession(lang="python") as session:
        result = session.run(code)
        return result.stdout

# MAIN - Run the server
if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=3456)