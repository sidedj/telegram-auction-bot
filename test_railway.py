#!/usr/bin/env python3
"""
Тест для проверки работы на Railway
"""

import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from Railway! Server is working."

@app.route('/health')
def health():
    return {"status": "ok", "message": "Server is healthy"}

@app.route('/test')
def test():
    return {
        "status": "ok",
        "port": os.getenv("PORT", "No PORT env var"),
        "python_version": os.sys.version,
        "working_directory": os.getcwd()
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
