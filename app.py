#!/usr/bin/env python3
"""
Главный файл приложения для Railway
"""

import os
from payment_server import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
