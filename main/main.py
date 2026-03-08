#!/usr/bin/env python3
"""
OMBJI TRANS — Flask app factory.
To run the server use from project root: python run.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flask import Flask, render_template, send_from_directory

from main.routes import bp
from main.utils.logger import setup_logger
from main.utils.request_logger import register_request_logging
from main.utils.error_handlers import register_error_handlers

DEFAULT_INVOICE_NUMBER = 1


def create_app():
    BASE_DIR = Path(__file__).resolve().parent.parent

    template_dir = BASE_DIR / "templates"
    static_dir = BASE_DIR / "static"
    app = Flask(
        __name__,
        template_folder=str(template_dir),
        static_folder=str(static_dir),
        static_url_path="/static",
    )
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

    logger = setup_logger()

    app.register_blueprint(bp)

    register_request_logging(app, logger)
    register_error_handlers(app, logger)

    @app.route("/")
    def index():
        return render_template(
            "index.html", default_invoice_number=DEFAULT_INVOICE_NUMBER
        )

    logger.info("Flask app created successfully")

    return app
