# Secure MCP Server

A FastAPI-based server for secure, containerized Python code execution using Docker and FastMCP. Supports code execution with popular data science libraries in a sandboxed environment.

---

## Features
- Execute arbitrary Python code securely in Docker containers
- Pre-installed data science libraries (pandas, numpy, matplotlib, etc.)
- FastMCP tool interface for agent integration
- REST API for HTTP clients (e.g., n8n)

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
   cd mcp-server-demo
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Build the custom Docker image**
   ```bash
   docker build -t fastmcp-python:latest .
   ```
   This image includes all allowed libraries for code execution.

---

## Running the Server

### 1. **FastAPI HTTP Server (for REST API)**

```bash
uvicorn secure_mcp_server:app --reload
```
- Access the API at: `http://localhost:8000`
- Endpoints:
  - `POST /execute_code` — Execute Python code (form-data: `code`, optional `timeout`, optional `files`)
  - `GET /available_libraries` — List allowed libraries
  - `GET /mcp_schema` — Tool schema for agents

### 2. **MCP Server (for agent/CLI integration, with SSE)**

```bash
fastmcp run secure_mcp_server.py --transport sse --port 9000
```
- SSE endpoint: `http://localhost:9000/sse`
- Use with MCP-compatible clients or agents

---

## Example: Execute Code via HTTP (e.g., n8n or curl)

**Request:**
```json
{
  "code": "print(\"hello world!\")"
}
```

**With curl:**
```bash
curl -X POST -F "code=print('hello world!')" http://localhost:8000/execute_code
```

**Complex Example:**
```json
{
  "code": "import pandas as pd\nimport numpy as np\n\nnp.random.seed(42)\ndata = pd.DataFrame({\n    'A': np.random.randint(1, 100, 20),\n    'B': np.random.normal(0, 1, 20),\n    'C': np.random.choice(['X', 'Y', 'Z'], 20)\n})\nprint('First 5 rows:')\nprint(data.head())\nprint('\\nSummary statistics:')\nprint(data.describe())\nprint('\\nValue counts for column C:')\nprint(data['C'].value_counts())\nprint('\\nCorrelation matrix:')\nprint(data.corr())"
}
```
