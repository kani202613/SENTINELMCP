"""
SentinelMCP Tool: Filesystem Tool (Core Tool 2)
Backed by 'Enterprise DB - Files' sheet in SentinelMCP_Dataset_Clean.xlsx
Returns literal DataFrame cell values.
"""
from tools.base import ToolDataProvider

def file_tool(action: str = "read_file", filepath: str = "secret.txt", content: str = "", sandboxed: bool = False) -> dict:
    """Handles filesystem operations returning exact literal DataFrame row values."""
    df = ToolDataProvider.get_sheet('Enterprise DB - Files')
    
    if action == "read_file":
        match = df[df['path'].str.contains(filepath, case=False, na=False) | df['filename'].str.contains(filepath, case=False, na=False)]
        if match.empty:
            match = df.iloc[[0]]
        row = match.iloc[0].to_dict()
        
        return {
            "status": "success",
            "action": "read_file",
            "file_id": int(row.get('file_id', 1)),
            "filename": str(row.get('filename', filepath)),
            "path": str(row.get('path', f'/files/{filepath}')),
            "classification": str(row.get('classification', 'PUBLIC')),
            "owner": str(row.get('owner', 'Alice')),
            "content": str(row.get('content', '')),
            "size_kb": int(row.get('size_kb', 4)),
            "created_at": str(row.get('created_at', '')),
            "source_sheet": "Enterprise DB - Files",
            "sandboxed": sandboxed
        }
        
    elif action == "write_file":
        return {
            "status": "success",
            "action": "write_file",
            "filepath": filepath,
            "bytes_written": len(content),
            "source_sheet": "Enterprise DB - Files",
            "sandboxed": sandboxed,
            "message": f"Successfully wrote {len(content)} bytes to {filepath}" + (" (SANDBOXED EXCLUSIVELY)" if sandboxed else "")
        }
        
    elif action == "delete_file":
        return {
            "status": "success",
            "action": "delete_file",
            "filepath": filepath,
            "source_sheet": "Enterprise DB - Files",
            "sandboxed": sandboxed,
            "message": f"File {filepath} scheduled for deletion" + (" (SANDBOXED MOCK)" if sandboxed else "")
        }
        
    else:
        return {"status": "error", "message": f"Unknown action: {action}"}
