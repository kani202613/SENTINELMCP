"""
SentinelMCP Tool: HTTP / Email Client Tool (Extended Tool 2)
Backed by 'Email Seed' sheet in SentinelMCP_Dataset_Clean.xlsx
Returns literal cell values from DataFrame rows.
Handles both 'endpoint' and 'url' keyword parameters seamlessly.
"""
from tools.base import ToolDataProvider

def http_tool(action: str = "send_request", endpoint: str = "https://api.external.com/data", method: str = "POST", payload: dict = None, email_id: str = "MSG-1002", sandboxed: bool = False, **kwargs) -> dict:
    """Handles external HTTP API / Email requests returning literal Email Seed cell values."""
    if "url" in kwargs and kwargs["url"]:
        endpoint = kwargs["url"]
        
    df = ToolDataProvider.get_sheet('Email Seed')
    
    if email_id:
        match = df[df['id'].astype(str) == str(email_id)] if 'id' in df.columns else df.iloc[[0]]
        if match.empty:
            match = df.iloc[[1]]  # Default to MSG-1002 poisoned email
    else:
        match = df.iloc[[1]]
        
    row = match.iloc[0].to_dict()
    
    return {
        "status": "success",
        "action": action,
        "method": method,
        "endpoint": endpoint,
        "email_record": {
            "id": str(row.get('id', 'MSG-1002')),
            "from": str(row.get('from', '')),
            "to": str(row.get('to', '')),
            "subject": str(row.get('subject', '')),
            "body": str(row.get('body', '')),
            "trust_level": str(row.get('trust_level', 'EXTERNAL_CONTENT'))
        },
        "source_sheet": "Email Seed",
        "sandboxed": sandboxed
    }
