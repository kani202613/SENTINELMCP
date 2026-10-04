"""
SentinelMCP Tool: Database Tool (Core Tool 4)
Backed by 'Enterprise DB - Employees', 'Projects', and 'Invoices' sheets in SentinelMCP_Dataset_Clean.xlsx
Returns literal row records directly from the loaded DataFrame sheets.
"""
from tools.base import ToolDataProvider

def database_tool(action: str = "query_select", query: str = "SELECT * FROM Employees", table: str = "Employees", sandboxed: bool = False) -> dict:
    """Handles SQL database operations returning exact literal DataFrame row records."""
    if action == "query_select":
        table_clean = table.strip().lower()
        sheet_map = {
            "employees": "Enterprise DB - Employees",
            "projects": "Enterprise DB - Projects",
            "invoices": "Enterprise DB - Invoices",
            "files": "Enterprise DB - Files"
        }
        sheet_name = sheet_map.get(table_clean, "Enterprise DB - Employees")
        df = ToolDataProvider.get_sheet(sheet_name)
        records = df.to_dict(orient='records')
        
        return {
            "status": "success",
            "action": "query_select",
            "table": table,
            "query": query,
            "row_count": len(records),
            "data": records,
            "source_sheet": sheet_name,
            "sandboxed": sandboxed
        }
        
    elif action == "query_delete":
        return {
            "status": "success",
            "action": "query_delete",
            "table": table,
            "query": query,
            "rows_affected": 1 if sandboxed else 5,
            "source_sheet": "Enterprise DB",
            "sandboxed": sandboxed,
            "message": f"Executed SQL delete query on table {table}" + (" (SANDBOXED IN-MEMORY ROLLBACK)" if sandboxed else "")
        }
        
    else:
        return {"status": "error", "message": f"Unknown database action: {action}"}
