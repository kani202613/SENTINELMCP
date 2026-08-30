"""
SentinelMCP Milestone 7 — Security Operations Web Dashboard (dashboard/app.py)
Flask server serving real-time security dashboard consuming actual runtime SentinelMCP audit data.
Supports Manual Security Testing for 7 input categories + Advanced Tool Simulation Mode.
"""
import os
import sys
import json
import numpy as np
from flask import Flask, jsonify, render_template, request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentinel.interceptor import SentinelInterceptor

app = Flask(__name__, template_folder="templates", static_folder="static")
interceptor_instance = SentinelInterceptor(audit_log_path="data/m5_audit_log.jsonl")

def load_audit_entries() -> list:
    log_path = "data/m5_audit_log.jsonl"
    entries = []
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            for line in f:
                if line.strip():
                    try:
                        entries.append(json.loads(line))
                    except Exception:
                        pass
    return entries

@app.route("/")
@app.route("/dashboard")
def index():
    return render_template("index.html")

@app.route("/api/stats", methods=["GET"])
def get_stats():
    entries = load_audit_entries()
    total_requests = len(entries)
    blocked_count = sum(1 for e in entries if e.get("decision") == "BLOCKED")
    sandboxed_count = sum(1 for e in entries if e.get("sandboxed", False))
    
    sris = [e.get("sri", 0) for e in entries]
    latencies = [e.get("scoring_latency_ms", 0.0) for e in entries]
    
    mean_sri = round(float(np.mean(sris)), 1) if sris else 0.0
    mean_latency = round(float(np.mean(latencies)), 2) if latencies else 0.0

    return jsonify({
        "total_requests": total_requests,
        "blocked_count": blocked_count,
        "sandboxed_count": sandboxed_count,
        "mean_sri": mean_sri,
        "mean_latency_ms": mean_latency
    })

@app.route("/api/audit_stream", methods=["GET"])
def get_audit_stream():
    entries = load_audit_entries()
    return jsonify(entries[-50:])

@app.route("/api/policies", methods=["GET"])
def get_policies():
    policy_path = "config/policy.json"
    catalog_path = "config/tool_catalog.json"

    policies = {}
    catalog = {}

    if os.path.exists(policy_path):
        with open(policy_path, "r") as f:
            policies = json.load(f)

    if os.path.exists(catalog_path):
        with open(catalog_path, "r") as f:
            catalog = json.load(f)

    return jsonify({"policies": policies, "catalog": catalog})

@app.route("/api/intercept", methods=["POST"])
@app.route("/api/manual_test", methods=["POST"])
def intercept_request():
    data = request.json or {}
    session_id = data.get("session_id", "manual_test_session")
    mode = data.get("mode", "category")  # category or advanced
    
    context = data.get("context", "Manual security testing prompt")
    user_role = data.get("user_role", "junior_analyst")
    source_trust = data.get("source_trust", "INTERNAL")

    if mode == "advanced":
        tool_name = data.get("tool_name", "file_tool")
        action = data.get("action", "read_file")
        args = data.get("args", {})
    else:
        input_type = data.get("input_type", "Email").lower()
        if input_type == "email":
            tool_name = "http_tool"
            action = data.get("action", "read_email")
            args = {"email_id": data.get("email_id", 1), "content": data.get("content", "")}
            source_trust = "EXTERNAL_CONTENT"
        elif input_type == "web":
            tool_name = "web_tool"
            action = "fetch_page"
            args = {"url": data.get("url", "https://company.internal/doc")}
            source_trust = "EXTERNAL_CONTENT"
        elif input_type == "pdf":
            tool_name = "pdf_reader"
            action = "read_pdf"
            args = {"doc_id": data.get("doc_id", 1)}
            source_trust = "EXTERNAL_CONTENT"
        elif input_type == "github":
            tool_name = "github_tool"
            action = data.get("action", "read_issue")
            args = {"repo": data.get("repo", "core-backend"), "issue_id": data.get("issue_id", 2)}
            source_trust = "EXTERNAL_CONTENT"
        elif input_type == "slack":
            tool_name = "slack_tool"
            action = "send_message"
            args = {"channel": data.get("channel", "#public"), "message": data.get("message", "Hello")}
        elif input_type == "database":
            tool_name = "database_tool"
            action = data.get("action", "query_select")
            args = {"query": data.get("query", "SELECT * FROM Employees")}
        elif input_type in ["http", "api", "http/api"]:
            tool_name = "http_tool"
            action = "send_request"
            args = {"url": data.get("url", "https://api.external/data"), "payload": data.get("payload", "")}
        else:
            tool_name = "file_tool"
            action = "read_file"
            args = {"filepath": "doc.txt"}

    req = {
        "session_id": session_id,
        "tool_name": tool_name,
        "action": action,
        "user_role": user_role,
        "context": context,
        "args": args,
        "source_trust": source_trust
    }

    res = interceptor_instance.intercept_and_execute(req)

    # Build Cytoscape graph nodes and edges for session history
    history = interceptor_instance.session_histories.get(session_id, [])
    nodes = []
    edges = []
    
    seen_nodes = set()
    for idx, h in enumerate(history):
        node_id = f"{h['tool_name']}.{h['action']}"
        if node_id not in seen_nodes:
            seen_nodes.add(node_id)
            nodes.append({"data": {"id": node_id, "label": node_id}})
        
        if idx > 0:
            prev_id = f"{history[idx-1]['tool_name']}.{history[idx-1]['action']}"
            edge_id = f"e_{idx}"
            is_danger = (res.get("sri_details", {}).get("matched_path") != "")
            edges.append({
                "data": {
                    "id": edge_id,
                    "source": prev_id,
                    "target": node_id,
                    "dangerous": is_danger
                }
            })

    res["graph_elements"] = {"nodes": nodes, "edges": edges}
    res["request_echo"] = req
    return jsonify(res)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
