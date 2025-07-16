from fastmcp import Client
import asyncio

async def test_execute_code():
    async with Client("http://localhost:3456/sse") as client:
        # List available tools
        tools = await client.list_tools()
        print(f"Available tools: {tools}")
        
        # Test simple code execution
        code = """print("Testing MCP server!")
x = 10
y = 20
print(f"Sum: {x + y}")
        """
        
        result = await client.call_tool("execute_code", {"code": code})
        print(f"Execution result:\n{result}")

if __name__ == "__main__":
    asyncio.run(test_execute_code()) 
