#!/usr/bin/env python3
"""
OMBJI TRANS — Run the invoice server (professional entry point).
Usage (from project root):
    python run.py
"""
import sys
from pathlib import Path

# Ensure project root is on path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from main.main import create_app

if __name__ == "__main__":
    app = create_app()
    print("=" * 55)
    print("  OMBJI TRANS  v1.0.0")
    print("  http://127.0.0.1:5000")
    print("=" * 55)
    app.run(debug=True, host="0.0.0.0", port=5000)
