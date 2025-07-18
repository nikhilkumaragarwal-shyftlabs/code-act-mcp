from fastmcp import Client
import asyncio
import os

async def main():
    # Connect via SSE to your MCP server
    port = os.getenv("PORT", "3000")
    async with Client(f"http://localhost:{port}/sse") as client:
        # List available tools
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")
        
        # Test 1: Simple Python code
        print("\n=== Test 1: Simple Python code ===")
        result1 = await client.call_tool("execute_code", {"code": "print('Hello, World!')\nx = 5 + 3\nprint(f'Result: {x}')"})
        print(f"Result:\n\n {result1.data.output}")
        
        # Test 2: Using approved library (pandas)
        print("\n=== Test 2: Using approved library (pandas) ===")
        pandas_code = """
import pandas as pd
df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
print("DataFrame created:")
print(df)
print(f"Shape: {df.shape}")
"""
        result2 = await client.call_tool("execute_code", {"code": pandas_code})
        print(f"Result:\n\n {result2.data.output}")
        
        # Test 3: Using approved library (numpy)
        print("\n=== Test 3: Using approved library (numpy) ===")
        numpy_code = """
import numpy as np
arr = np.array([1, 2, 3, 4, 5])
print(f"Array: {arr}")
print(f"Mean: {np.mean(arr)}")
print(f"Sum: {np.sum(arr)}")
"""
        result3 = await client.call_tool("execute_code", {"code": numpy_code})
        print(f"Result:\n\n {result3.data.output}")
        
        # Test 4: Using approved library (matplotlib)
        print("\n=== Test 4: Using approved library (matplotlib) ===")
        matplotlib_code = """
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.figure(figsize=(8, 6))
plt.plot(x, y, 'b-', label='sin(x)')
plt.title('Sine Wave')
plt.xlabel('x')
plt.ylabel('sin(x)')
plt.legend()
plt.grid(True)
plt.savefig('sine_wave.png')
print("Plot saved as sine_wave.png")
"""
        result4 = await client.call_tool("execute_code", {"code": matplotlib_code})
        print(f"Result:\n\n {result4.data.output}")
        
        # Test 5: Error handling - division by zero
        print("\n=== Test 5: Error handling ===")
        error_code = """
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"Error caught: {e}")
"""
        result5 = await client.call_tool("execute_code", {"code": error_code})
        print(f"Result:\n\n {result5.data.output}")

if __name__ == "__main__":
    asyncio.run(main()) 