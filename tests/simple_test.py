from fastmcp import Client
import asyncio
import os
from pydantic import BaseModel

class CodeSchema(BaseModel):
    code: str

async def test_execute_code():
    port = os.getenv("PORT", "3000")
    async with Client(f"http://localhost:{port}/sse") as client:
        # List available tools
        tools = await client.list_tools()
        print(f"Available tools: {tools}")
        
        # Test simple code execution
        
        code_str = """print("Testing MCP server!")
x = 10
y = 20
print(f"Sum: {x + y}")
        """
        code_schema = CodeSchema(code=code_str)
        result = await client.call_tool("execute_code", {"code_schema":code_schema})
        print(f"Execution result:\n\n{result.data.output}")

if __name__ == "__main__":
    asyncio.run(test_execute_code()) 
