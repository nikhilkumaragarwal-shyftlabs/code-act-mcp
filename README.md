# Secure Python Code Execution Server (with FastMCP)

A secure, containerized Python code execution server using Docker and [FastMCP](https://github.com/nikhilkumaragarwal-shyftlabs/FastMCP). Supports safe execution of Python code with popular data science libraries in a sandboxed environment, accessible via the MCP tool interface.

---

## Features
- Execute arbitrary Python code securely in Docker containers
- Whitelisted data science libraries (pandas, numpy, matplotlib, etc.)
- [FastMCP](https://github.com/nikhilkumaragarwal-shyftlabs/FastMCP) tool interface for agent and client integration
- Resource limits (CPU, memory, timeout) and code safety checks
- Example test clients provided

---

## Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (must be running)
- Python 3.11+
- (Recommended) Use WSL2 backend for Docker on Windows for better performance

---

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/nikhilkumaragarwal-shyftlabs/FastMCP.git
   cd code-act-mcp
   ```

2. **Install Python dependencies**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r agentrun-api/requirements.txt
   ```

3. **Build the Docker image**
   ```bash
   docker build -t codeact-api:latest -f agentrun-api/docker/api/Dockerfile agentrun-api/
   ```

---

## Running the Server

### 1. **Start a Docker container for code execution**
You must have a running Docker container named **agentrun-api_python_runner_1** for the server to execute code in. Example:
```bash
docker run -d --name agentrun-api_python_runner_1 --rm -v /tmp:/tmp codeact-api:latest tail -f /dev/null
```

### 2. **Start the MCP Server**
With your virtual environment activated:
```bash
python agentrun-api/src/api/main.py
```
- The server will listen on port 3456 by default (SSE transport).
- The MCP tool `execute_code` will be available for clients.
- **Note:** By default, the server looks for a container named `agentrun-api_python_runner_1`. If you want to use a different name, set the `CONTAINER_NAME` environment variable before starting the server.

---

## Usage Example (with FastMCP Client)

See `tests/simple_test.py` and `tests/test_client.py` for usage examples.

**Example:**
```python
from fastmcp import Client
import asyncio

async def test():
    async with Client("http://localhost:3456/sse") as client:
        result = await client.call_tool("execute_code", {"code": "print('Hello, World!')"})
        print(result.text)

asyncio.run(test())
```

---

## Approved Libraries
The following libraries are allowed for code execution (see `utils.py`):
- pandas, numpy, openpyxl, xlsxwriter, PyPDF2, pdfplumber, python-docx, python-pptx, pillow, pytesseract, matplotlib, plotly, seaborn, reportlab

---

## Security Model
- All code is executed in an isolated Docker container with resource limits (CPU, memory, timeout).
- Only whitelisted libraries can be imported and installed.
- Code is statically analyzed for dangerous patterns (e.g., use of os, sys, subprocess, exec, eval, etc.) before execution.
- Each code execution is sandboxed and cleaned up after running.

---

## Testing

- Run the provided test clients:
  ```bash
  python tests/simple_test.py
  python tests/test_client.py
  ```
- These tests connect to the MCP server and exercise code execution, library usage, and error handling.

---

## Project Structure

- `agentrun/` — Core code execution logic (AgentRun class)
- `agentrun-api/src/api/` — MCP server API (main.py)
- `utils.py` — Approved libraries utility
- `tests/` — Example test clients
- `agentrun-api/docker/` — Dockerfiles for API and code runner

---

## Quick Reference Table

| Step | Command                                                                                  | Notes                        |
|------|------------------------------------------------------------------------------------------|------------------------------|
| 1    | Start Docker Desktop                                                                     |                              |
| 2    | `python3 -m venv venv`<br>`source venv/bin/activate`                                     |                              |
| 3    | `pip install -r agentrun-api/requirements.txt`                                           |                              |
| 4    | `docker build -t codeact-api:latest -f agentrun-api/docker/api/Dockerfile agentrun-api/` |                              |
| 5    | `docker run -d --name agentrun-api_python_runner_1 --rm -v /tmp:/tmp codeact-api:latest tail -f /dev/null` | Must use this name |
| 6    | `python agentrun-api/src/api/main.py`                                                    | Leave this running           |
| 7    | `source venv/bin/activate` (in new terminal)                                             |                              |
| 8    | `python tests/test_client.py`                                                            | See test results             |

---

## License
MIT
