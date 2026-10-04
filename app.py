"""
SentinelMCP — Flask Application Entry Point (Milestone 1)
Serves SentinelMCP APIs and Dashboard telemetry endpoints.
"""
import os
import json
from flask import Flask, jsonify, render_template
from data_loader import load_dataset, generate_configs

app = Flask(__name__)

# Initialize engine data & configs on startup
print("Initializing SentinelMCP Engine...")
try:
    dataset = load_dataset()
    generate_configs(dataset)
    print("SentinelMCP Data & Configuration loaded successfully.")
except Exception as e:
    print(f"Warning during initialization: {e}")

@app.route('/')
def index():
    return jsonify({
        "status": "online",
        "service": "SentinelMCP Security Interception Layer",
        "version": "1.0.0"
    })

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "sheets_loaded": len(dataset) if 'dataset' in globals() else 0
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
