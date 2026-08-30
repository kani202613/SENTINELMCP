"""
SentinelMCP Tool: PDF Reader (Core Tool 1)
Backed by 'PDF Docs Seed' sheet in SentinelMCP_Dataset_Clean.xlsx
Returns literal DataFrame cell values.
"""
from tools.base import ToolDataProvider

def read_pdf(doc_path: str = None, doc_id: int = 1) -> dict:
    """Reads PDF document contents returning exact literal cell values from PDF Docs Seed sheet."""
    df = ToolDataProvider.get_sheet('PDF Docs Seed')
    
    if doc_id is not None:
        match = df[df['doc_id'] == int(doc_id)]
    elif doc_path:
        match = df[df['path'].str.contains(doc_path, case=False, na=False) | df['title'].str.contains(doc_path, case=False, na=False)]
    else:
        match = df.iloc[[0]]
        
    if match.empty:
        match = df.iloc[[0]]
        
    row = match.iloc[0].to_dict()
    
    return {
        "status": "success",
        "doc_id": int(row['doc_id']),
        "title": str(row['title']),
        "path": str(row['path']),
        "content": str(row['content']),
        "classification": str(row.get('classification', 'PUBLIC')),
        "source_sheet": "PDF Docs Seed"
    }
