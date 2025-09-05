#!/usr/bin/env python3
"""
Временный файл для Railway - перенаправляет на railway_server.py
"""

import subprocess
import sys
import os

if __name__ == "__main__":
    # Перенаправляем на railway_server.py
    script_path = os.path.join(os.path.dirname(__file__), "railway_server.py")
    
    if os.path.exists(script_path):
        print("🔄 Перенаправление на railway_server.py...")
        subprocess.run([sys.executable, script_path])
    else:
        print("❌ Файл railway_server.py не найден!")
        sys.exit(1)
