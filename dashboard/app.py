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
from agent.chat_service import SecureChatService

app = Flask(__name__, template_folder="templates", static_folder="static")
interceptor_instance = SentinelInterceptor(audit_log_path="data/m5_audit_log.jsonl")
chat_service = SecureChatService(interceptor=interceptor_instance)

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
    total_latencies = [e.get("total_latency_ms", e.get("scoring_latency_ms", 0.0)) for e in entries]
    
    mean_sri = round(float(np.mean(sris)), 1) if sris else 0.0
    mean_latency = round(float(np.mean(latencies)), 2) if latencies else 0.0
    mean_total_latency = round(float(np.mean(total_latencies)), 2) if total_latencies else 0.0

    return jsonify({
        "total_requests": total_requests,
        "blocked_count": blocked_count,
        "sandboxed_count": sandboxed_count,
        "mean_sri": mean_sri,
        "mean_latency_ms": mean_latency,
        "mean_total_latency_ms": mean_total_latency
    })

@app.route("/api/audit_stream", methods=["GET"])
def get_audit_stream():
    entries = load_audit_entries()
    limit = request.args.get("limit", 100, type=int)
    if limit > 0:
        return jsonify(entries[-limit:])
    return jsonify(entries)

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

@app.route("/api/sessions", methods=["GET"])
def get_sessions():
    entries = load_audit_entries()
    sessions = {}
    for e in entries:
        sid = e.get("session_id") or e.get("workflow_id")
        if sid:
            if sid not in sessions:
                sessions[sid] = {"session_id": sid, "turns": 0, "max_sri": 0, "max_decision": "SAFE", "matched_path": ""}
            sessions[sid]["turns"] += 1
            sri = e.get("sri", 0)
            if sri > sessions[sid]["max_sri"]:
                sessions[sid]["max_sri"] = sri
            dec = e.get("decision", "SAFE")
            if dec == "BLOCKED" or (dec == "SUSPICIOUS" and sessions[sid]["max_decision"] != "BLOCKED"):
                sessions[sid]["max_decision"] = dec
            path = e.get("matched_path") or e.get("graph_path", "")
            if path:
                sessions[sid]["matched_path"] = path

    # Also include active in-memory sessions
    for sid, hist in interceptor_instance.session_histories.items():
        if sid not in sessions:
            sessions[sid] = {"session_id": sid, "turns": len(hist), "max_sri": 0, "max_decision": "SAFE", "matched_path": ""}

    return jsonify(list(sessions.values()))

@app.route("/api/session_graph/<session_id>", methods=["GET"])
def get_session_graph(session_id):
    entries = [e for e in load_audit_entries() if (e.get("session_id") == session_id or e.get("workflow_id") == session_id)]
    
    if not entries:
        hist = interceptor_instance.session_histories.get(session_id, [])
        entries = hist

    nodes = []
    edges = []
    matched_path = ""
    max_sri = 0
    max_decision = "SAFE"

    for idx, h in enumerate(entries):
        node_id = f"node_{idx+1}"
        tool_name = h.get("tool_name", "unknown")
        action = h.get("action", "action")
        sri = h.get("sri", 0)
        dec = h.get("decision", "SAFE")
        if sri > max_sri: max_sri = sri
        if dec == "BLOCKED" or (dec == "SUSPICIOUS" and max_decision != "BLOCKED"):
            max_decision = dec
        
        path = h.get("matched_path") or h.get("graph_path") or (h.get("sri_details", {}).get("matched_path", "") if isinstance(h.get("sri_details"), dict) else "")
        if path:
            matched_path = path

        label = f"{tool_name}\n{action}"
        nodes.append({
            "data": {
                "id": node_id,
                "label": label,
                "tool": tool_name,
                "action": action,
                "turn": idx + 1,
                "sri": sri,
                "decision": dec
            }
        })

        if idx > 0:
            prev_id = f"node_{idx}"
            is_danger = bool(path) or (h.get("graph_bonus", 0) > 0) or (h.get("sri_details", {}).get("graph_bonus", 0) > 0)
            edges.append({
                "data": {
                    "id": f"edge_{idx}",
                    "source": prev_id,
                    "target": node_id,
                    "dangerous": is_danger
                }
            })

    return jsonify({
        "session_id": session_id,
        "nodes": nodes,
        "edges": edges,
        "matched_path": matched_path,
        "max_sri": max_sri,
        "max_decision": max_decision,
        "total_turns": len(entries),
        "entries": entries
    })

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
    
    for idx, h in enumerate(history):
        node_id = f"node_{idx+1}"
        tool_action = f"{h['tool_name']}.{h['action']}"
        label = f"Turn {idx+1}: {tool_action}"
        nodes.append({"data": {"id": node_id, "label": label, "tool": h['tool_name'], "action": h['action']}})
        
        if idx > 0:
            prev_id = f"node_{idx}"
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

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json or {}
    message = data.get("message", "").strip()
    session_id = data.get("session_id", "chat_session_001")
    user_role = data.get("user_role", "junior_analyst")
    confirm_action = data.get("confirm_action", False)
    attachment = data.get("attachment", None)

    if not message and not attachment:
        return jsonify({
            "status": "ERROR",
            "message": "Empty user message.",
            "response": "Please enter a message, upload a file, or select a scenario shortcut."
        }), 400

    result = chat_service.process_user_message(
        message=message or f"Analyze uploaded file: {attachment.get('filename') if attachment else 'attachment'}",
        session_id=session_id,
        user_role=user_role,
        confirm_action=confirm_action,
        attachment=attachment
    )

    return jsonify(result)

@app.route("/api/chat/upload", methods=["POST"])
def chat_upload():
    if "file" not in request.files:
        return jsonify({"status": "ERROR", "message": "No file uploaded."}), 400

    file = request.files["file"]
    if not file or file.filename == "":
        return jsonify({"status": "ERROR", "message": "Empty file."}), 400

    filename = file.filename
    upload_dir = "data/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, filename)
    file.save(file_path)

    # Read content preview
    content = ""
    try:
        if filename.lower().endswith('.pdf'):
            try:
                import PyPDF2
                with open(file_path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        text = page.extract_text()
                        if text:
                            content += text + "\n"
            except ImportError:
                content = "[PDF parsing error: PyPDF2 not installed]"
        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
    except Exception as e:
        content = f"[Unreadable file content: {e}]"

    size_kb = round(os.path.getsize(file_path) / 1024, 1)
    file_type = filename.split(".")[-1].upper() if "." in filename else "FILE"

    attachment = {
        "filename": filename,
        "filepath": file_path,
        "size_kb": size_kb,
        "file_type": file_type,
        "content": content
    }

    return jsonify({
        "status": "SUCCESS",
        "message": f"Successfully uploaded '{filename}' ({size_kb} KB).",
        "attachment": attachment
    })

@app.route("/api/chat/clear", methods=["POST"])
def chat_clear():
    data = request.json or {}
    session_id = data.get("session_id", "chat_session_001")
    chat_service.clear_conversation(session_id)
    return jsonify({"status": "SUCCESS", "message": f"Cleared session '{session_id}'."})

@app.route("/api/chat/export", methods=["GET"])
def chat_export():
    session_id = request.args.get("session_id", "chat_session_001")
    history = chat_service.conversations.get(session_id, [])
    return jsonify({"session_id": session_id, "history": history})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
