import os
import shutil
import uuid
import tempfile
import logging
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import docker
import threading
import time
from fastmcp import FastMCP, Context
import asyncio

# --- CONFIGURATION ---
PYTHON_IMAGE = "fastmcp-python:latest"
MEMORY_LIMIT = "512m"
CPU_LIMIT = 1.0  # CPUs
TIMEOUT = 30  # seconds (default)
MAX_TIMEOUT = 90
WORKSPACE_DIR = os.path.join(tempfile.gettempdir(), "mcp_workspace")
ALLOWED_MODULES = [
    "pandas", "numpy", "openpyxl", "xlsxwriter", "PyPDF2", "pdfplumber", "python_docx", "python_pptx",
    "PIL", "pytesseract", "matplotlib", "plotly", "seaborn", "reportlab",
    "json", "csv", "datetime", "re", "os", "io", "sys"
]

# --- LOGGING SETUP ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("secure_mcp")

# --- FASTAPI APP ---
app = FastAPI(title="Secure MCP Server", description="Containerized Python code execution with MCP tool interface.")

# --- DOCKER CLIENT ---
docker_client = docker.from_env()

# --- UTILS ---
def clean_workspace(path):
    if os.path.exists(path):
        shutil.rmtree(path)

def allowed_imports(code: str) -> bool:
    """Check if code only imports allowed modules."""
    import ast
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] not in ALLOWED_MODULES:
                        return False
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.split(".")[0] not in ALLOWED_MODULES:
                    return False
        return True
    except Exception as e:
        logger.warning(f"Import check failed: {e}")
        return False

def run_code_in_container(code: str, input_files: List[str], timeout: int) -> dict:
    """Run code in a Docker container with resource and security limits."""
    run_id = str(uuid.uuid4())
    workspace = os.path.join(WORKSPACE_DIR, run_id)
    os.makedirs(workspace, exist_ok=True)
    code_file = os.path.join(workspace, "user_code.py")
    with open(code_file, "w", encoding="utf-8") as f:
        f.write(code)
    # Copy input files
    for fpath in input_files:
        shutil.copy(fpath, workspace)
    # Prepare Docker run
    mounts = {workspace: {"bind": "/workspace", "mode": "rw"}}
    command = ["python", "/workspace/user_code.py"]
    logs = ""
    error = None
    files_out = []
    container = None
    try:
        container = docker_client.containers.run(
            PYTHON_IMAGE,
            command,
            volumes=mounts,
            working_dir="/workspace",
            network_mode="none",
            mem_limit=MEMORY_LIMIT,
            cpu_period=100000,
            cpu_quota=int(CPU_LIMIT * 100000),
            detach=True,
            stdout=True,
            stderr=True,
            remove=False, 
            user="1000:1000"
        )
        def kill_after():
            time.sleep(timeout)
            try:
                container.kill()
            except Exception:
                pass
        killer = threading.Thread(target=kill_after)
        killer.start()
        result = container.wait(timeout=timeout)
        logs = container.logs(stdout=True, stderr=True).decode("utf-8")
        killer.join()
        # Collect output files
        files_out = [f for f in os.listdir(workspace) if f != "user_code.py"]
    except Exception as e:
        error = str(e)
        logger.error(f"Execution error: {error}")
    finally:
        if container is not None:
            try:
                container.remove(force=True)
            except Exception as e:
                logger.warning(f"Failed to remove container: {e}")
        clean_workspace(workspace)
    return {"stdout": logs, "error": error, "output_files": files_out}

# --- API MODELS ---
class ExecuteRequest(BaseModel):
    code: str
    timeout: Optional[int] = TIMEOUT
    input_files: Optional[List[str]] = None

class ExecuteResponse(BaseModel):
    stdout: str
    error: Optional[str]
    output_files: List[str]

@app.post("/execute_code", response_model=ExecuteResponse)
async def execute_code(
    code: str = Form(...),
    timeout: int = Form(TIMEOUT),
    files: Optional[List[UploadFile]] = None
):
    """Execute Python code in a secure, containerized environment."""
    logger.info("Received code execution request.")
    if timeout > MAX_TIMEOUT:
        raise HTTPException(status_code=400, detail=f"Timeout exceeds max allowed: {MAX_TIMEOUT}s")
    if not allowed_imports(code):
        raise HTTPException(status_code=400, detail="Code contains disallowed imports.")
    # Save uploaded files
    input_file_paths = []
    if files:
        temp_dir = tempfile.mkdtemp()
        for file in files:
            dest = os.path.join(temp_dir, file.filename)
            with open(dest, "wb") as f:
                f.write(await file.read())
            input_file_paths.append(dest)
    result = run_code_in_container(code, input_file_paths, timeout)
    # Clean up temp files
    if files:
        shutil.rmtree(temp_dir)
    return ExecuteResponse(**result)

@app.get("/available_libraries")
def available_libraries():
    """Expose the list of available libraries for code execution."""
    return {"allowed_libraries": ALLOWED_MODULES}

# --- MCP TOOL INTERFACE (SCHEMA) ---
@app.get("/mcp_schema")
def mcp_schema():
    """Expose MCP tool schema for agents."""
    return {
        "tools": [
            {
                "name": "execute_code",
                "description": "Execute Python code in a secure, containerized environment. Accepts code string, optional timeout, and file uploads. Returns stdout, error, and output file list.",
                "parameters": {
                    "code": "Python code as string",
                    "timeout": f"Execution timeout in seconds (max {MAX_TIMEOUT})",
                    "files": "List of input files (optional)"
                },
                "available_libraries": ALLOWED_MODULES
            }
        ]
    }

# --- FASTMCP SERVER SETUP ---
mcp = FastMCP("Secure MCP Server")

@mcp.tool()
async def execute_code_tool(code: str, timeout: int = TIMEOUT, ctx: Context = None):
    """Execute Python code in a secure, containerized environment. Returns stdout, error, and output file list."""
    if timeout > MAX_TIMEOUT:
        return {"error": f"Timeout exceeds max allowed: {MAX_TIMEOUT}s"}
    if not allowed_imports(code):
        return {"error": "Code contains disallowed imports."}
    result = run_code_in_container(code, [], timeout)
    return result

@mcp.tool()
async def list_available_libraries():
    """List available Python libraries for code execution."""
    return {"allowed_libraries": ALLOWED_MODULES}

# --- MAIN ENTRY POINT ---
if __name__ == "__main__":
    import sys
    print("🚀 Starting Secure MCP Server (FastMCP mode)")
    print("🛠️  Available tools:")
    print("   - execute_code_tool")
    print("   - list_available_libraries")
    print("💡 To run as HTTP server, use: uvicorn secure_mcp_server:app --reload")
    mcp.run() 