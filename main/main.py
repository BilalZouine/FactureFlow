#!/usr/bin/env python3
"""
OMBJI TRANS — Flask app factory.
To run the server use from project root:  python run.py
"""
import sys, traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flask import Flask, jsonify, render_template
from main.routes import bp
from main.utils.errors import AppError
from main.utils.response import server_error

DEFAULT_INVOICE_NUMBER = 1


def create_app():
    template_dir = Path(__file__).resolve().parent / "templates"
    app = Flask(__name__, template_folder=str(template_dir))
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

    app.register_blueprint(bp)

    @app.route("/")
    def index():
        return render_template("index.html", default_invoice_number=DEFAULT_INVOICE_NUMBER)

    @app.errorhandler(AppError)
    def handle_app_error(e): return e.to_response()

    @app.errorhandler(404)
    def handle_404(e):
        return jsonify({"status":"error","error_code":"NOT_FOUND","message":str(e)}), 404

    @app.errorhandler(405)
    def handle_405(e):
        return jsonify({"status":"error","error_code":"METHOD_NOT_ALLOWED","message":str(e)}), 405

    @app.errorhandler(413)
    def handle_413(e):
        return jsonify({"status":"error","error_code":"FILE_TOO_LARGE","message":"File exceeds 16 MB limit."}), 413

    @app.errorhandler(Exception)
    def handle_unexpected(e):
        traceback.print_exc()
        return server_error("Unexpected error.", details={"type":type(e).__name__,"info":str(e)})

    return app