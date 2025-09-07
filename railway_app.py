#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простое приложение для Railway
"""

import os
import sys
from pathlib import Path

# Добавляем текущую директорию в путь для импортов
sys.path.append(str(Path(__file__).parent))

# Импортируем Flask приложение из bot.py
from bot import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Запуск приложения на порту {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
