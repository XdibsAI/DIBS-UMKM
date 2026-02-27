#!/usr/bin/env python3
"""
MCP Server untuk DIBS AI - PRODUCTION VERSION
Compatible dengan Pydantic v2.8.x
"""

import os
import subprocess
import shlex
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
import uvicorn

# ============ CONFIGURATION ============
PROJECT_ROOT = Path("/home/dibs/dibs1")
ALLOWED_PATHS = [PROJECT_ROOT]
ALLOWED_COMMANDS = ["ls", "cat", "grep", "find", "head", "tail", "pwd", "echo"]

# ============ MODELS ============
class ToolRequest(BaseModel):
    tool: str
    args: Dict[str, Any] = {}

class ToolResponse(BaseModel):
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    model_config = ConfigDict(arbitrary_types_allowed=True)

class FileInfo(BaseModel):
    name: str
    type: str
    size: int
    modified: str

class DirInfo(BaseModel):
    name: str
    exists: bool
    files: int

class ProjectInfo(BaseModel):
    root: str
    directories: List[DirInfo]

# ============ FASTAPI APP ============
app = FastAPI(title="DIBS MCP Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ VALIDATION ============
def validate_path(path: str) -> Path:
    """Validate path is within project"""
    full_path = Path(path).resolve()
    for allowed in ALLOWED_PATHS:
        if str(full_path).startswith(str(allowed)):
            return full_path
    raise HTTPException(403, "Access denied: path outside project")

# ============ ENDPOINTS ============
@app.get("/health")
async def health():
    return {"status": "healthy", "project": str(PROJECT_ROOT), "uptime": datetime.now().isoformat()}

@app.get("/tools")
async def list_tools():
    return {
        "tools": [
            {"name": "file_read", "description": "Read content from a file", "args": {"path": "string"}},
            {"name": "file_write", "description": "Write content to a file", "args": {"path": "string", "content": "string"}},
            {"name": "list_dir", "description": "List directory contents", "args": {"path": "string"}},
            {"name": "run_command", "description": "Run a system command", "args": {"cmd": "string"}},
            {"name": "search_code", "description": "Search for text in codebase", "args": {"query": "string"}},
            {"name": "get_project_info", "description": "Get project structure info", "args": {}},
            {"name": "file_exists", "description": "Check if file exists", "args": {"path": "string"}},
            {"name": "get_file_size", "description": "Get file size", "args": {"path": "string"}},
        ]
    }

@app.post("/execute", response_model=ToolResponse)
async def execute_tool(request: ToolRequest):
    try:
        tool = request.tool
        args = request.args
        
        # ===== FILE READ =====
        if tool == "file_read":
            path = validate_path(args.get("path", ""))
            if not path.exists():
                return ToolResponse(success=False, error="File not found")
            if path.is_dir():
                return ToolResponse(success=False, error="Path is a directory, not a file")
            
            content = path.read_text(encoding='utf-8')
            return ToolResponse(success=True, result=content[:50000])  # Limit 50k chars
        
        # ===== FILE WRITE =====
        elif tool == "file_write":
            path = validate_path(args.get("path", ""))
            content = args.get("content", "")
            
            # Security: only allow text files in specific directories
            if not str(path).endswith(('.txt', '.md', '.env', '.json', '.yaml', '.yml', '.py', '.dart')):
                return ToolResponse(success=False, error="File type not allowed for writing")
            
            path.write_text(content, encoding='utf-8')
            return ToolResponse(success=True, result={"path": str(path), "size": len(content)})
        
        # ===== LIST DIRECTORY =====
        elif tool == "list_dir":
            path = validate_path(args.get("path", str(PROJECT_ROOT)))
            if not path.exists():
                return ToolResponse(success=False, error="Path not found")
            if not path.is_dir():
                return ToolResponse(success=False, error="Path is not a directory")
            
            items = []
            for item in sorted(path.iterdir()):
                items.append({
                    "name": item.name,
                    "type": "dir" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else 0,
                    "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                })
            return ToolResponse(success=True, result=items)
        
        # ===== RUN COMMAND =====
        elif tool == "run_command":
            cmd = args.get("cmd", "")
            
            # Security: only allow safe commands
            cmd_base = cmd.split()[0] if cmd else ""
            if cmd_base not in ALLOWED_COMMANDS:
                return ToolResponse(success=False, error=f"Command '{cmd_base}' not allowed. Allowed: {', '.join(ALLOWED_COMMANDS)}")
            
            result = subprocess.run(
                shlex.split(cmd),
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(PROJECT_ROOT)
            )
            return ToolResponse(
                success=True,
                result={
                    "stdout": result.stdout[:10000],
                    "stderr": result.stderr[:1000],
                    "returncode": result.returncode
                }
            )
        
        # ===== SEARCH CODE =====
        elif tool == "search_code":
            query = args.get("query", "")
            if not query:
                return ToolResponse(success=False, error="No query provided")
            
            # Search in code files only
            result = subprocess.run(
                ["grep", "-r", "-n", "-I", "--include=*.{py,dart,js,ts,html,css,md,txt}", query, str(PROJECT_ROOT)],
                capture_output=True,
                text=True,
                timeout=30
            )
            lines = result.stdout.split('\n')[:100]  # Limit to 100 results
            return ToolResponse(success=True, result=[l for l in lines if l.strip()])
        
        # ===== GET PROJECT INFO =====
        elif tool == "get_project_info":
            info = {
                "root": str(PROJECT_ROOT),
                "directories": []
            }
            for d in ["backend", "frontend", "downloads", "mcp-server"]:
                path = PROJECT_ROOT / d
                if path.exists():
                    file_count = len([f for f in path.glob("**/*") if f.is_file()])
                    info["directories"].append({
                        "name": d,
                        "exists": True,
                        "files": file_count,
                        "size": sum(f.stat().st_size for f in path.glob("**/*") if f.is_file()) // 1024  # KB
                    })
            return ToolResponse(success=True, result=info)
        
        # ===== FILE EXISTS =====
        elif tool == "file_exists":
            path = validate_path(args.get("path", ""))
            return ToolResponse(success=True, result={"exists": path.exists(), "is_file": path.is_file(), "is_dir": path.is_dir()})
        
        # ===== GET FILE SIZE =====
        elif tool == "get_file_size":
            path = validate_path(args.get("path", ""))
            if not path.exists() or not path.is_file():
                return ToolResponse(success=False, error="File not found")
            return ToolResponse(success=True, result={"size": path.stat().st_size, "size_kb": path.stat().st_size // 1024})
        
        # ===== UNKNOWN TOOL =====
        else:
            return ToolResponse(success=False, error=f"Unknown tool: {tool}")
            
    except HTTPException as e:
        return ToolResponse(success=False, error=e.detail)
    except subprocess.TimeoutExpired:
        return ToolResponse(success=False, error="Command timed out")
    except Exception as e:
        return ToolResponse(success=False, error=str(e))

# ============ MAIN ============
if __name__ == "__main__":
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║              DIBS MCP SERVER - PRODUCTION                    ║
║                  Listening on port 8765                       ║
╠══════════════════════════════════════════════════════════════╣
║ Project Root: {str(PROJECT_ROOT):<35} ║
║ Pydantic Version: Compatible with v2.8.x                      ║
║ Allowed Commands: {', '.join(ALLOWED_COMMANDS):<25} ║
╚══════════════════════════════════════════════════════════════╝
    """)
    uvicorn.run(app, host="0.0.0.0", port=8765, log_level="info")
