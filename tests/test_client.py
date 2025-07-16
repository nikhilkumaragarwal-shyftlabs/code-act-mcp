from fastmcp import Client
import asyncio

async def main():
    # Connect via SSE to your MCP server
    async with Client("http://localhost:3456/sse") as client:
        # List available tools
        tools = await client.list_tools()
        print(f"Available tools: {tools}")
        
        # Test 1: Simple Python code
        print("\n=== Test 1: Simple Python code ===")
        result1 = await client.call_tool("execute_code", {"code": "print('Hello, World!')\nx = 5 + 3\nprint(f'Result: {x}')"})
        print(f"Result: {result1.text}")
        
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
        print(f"Result: {result2.text}")
        
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
        print(f"Result: {result3.text}")
        
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
        print(f"Result: {result4.text}")
        
        # Test 5: Error handling - division by zero
        print("\n=== Test 5: Error handling ===")
        error_code = """
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"Error caught: {e}")
"""
        result5 = await client.call_tool("execute_code", {"code": error_code})
        print(f"Result: {result5.text}")

if __name__ == "__main__":
    asyncio.run(main()) 