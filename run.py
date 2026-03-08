#!/usr/bin/env python3
"""
OMBJI TRANS — Run the invoice server (production entry point).
Usage:
    python run.py
"""

import sys
import logging
from pathlib import Path
# from waitress import serve

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

logging.getLogger("werkzeug").disabled = True

from main.main import create_app

if __name__ == "__main__":
    app = create_app()
    
    app.run(debug=True , port=5000)

    print("=" * 55)
    print("  OMBJI TRANS  v1.0.0")
    print("  Production server: Waitress")
    print("  http://127.0.0.1:5000")
    print("=" * 55)

    # serve(app, host="0.0.0.0", port=5000)