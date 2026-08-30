"""
SentinelMCP Tool: Web Tool (Extended Tool 1)
Backed by 'Web Pages Seed' sheet in SentinelMCP_Dataset_Clean.xlsx
Returns literal cell values.
"""
from tools.base import ToolDataProvider

def web_tool(action: str = "fetch_page", url: str = "https://example.com/news", sandboxed: bool = False) -> dict:
    """Handles web page fetching returning exact literal cell values from Web Pages Seed sheet."""
    df = ToolDataProvider.get_sheet('Web Pages Seed')
    match = df[df['url'].str.contains(url, case=False, na=False)] if 'url' in df.columns else df.iloc[[0]]
    if match.empty:
        match = df.iloc[[0]]
    row = match.iloc[0].to_dict()
    
    return {
        "status": "success",
        "action": "fetch_page",
        "url": str(row.get('url', url)),
        "title": str(row.get('title', 'Web Page')),
        "content": str(row.get('content', 'Web page HTML content')),
        "trust_score": float(row.get('trust_score', 0.9)),
        "source_sheet": "Web Pages Seed",
        "sandboxed": sandboxed
    }
