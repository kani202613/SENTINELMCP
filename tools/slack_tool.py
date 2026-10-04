"""
SentinelMCP Tool: Slack Tool (Core Tool 5)
Backed by 'Slack Seed' sheet in SentinelMCP_Dataset_Clean.xlsx
Returns literal cell values.
"""
from tools.base import ToolDataProvider

def slack_tool(action: str = "send_message", channel: str = "#general", message: str = "", sandboxed: bool = False) -> dict:
    """Handles Slack communication returning exact literal cell values from Slack Seed sheet."""
    df = ToolDataProvider.get_sheet('Slack Seed')
    recent_messages = df.to_dict(orient='records')
    
    if action == "send_message":
        return {
            "status": "success",
            "action": "send_message",
            "channel": channel,
            "message": message,
            "recent_channel_messages": recent_messages,
            "source_sheet": "Slack Seed",
            "sandboxed": sandboxed,
            "delivery_status": "mock_delivered" if sandboxed else "delivered"
        }
    else:
        return {"status": "error", "message": f"Unknown Slack action: {action}"}
